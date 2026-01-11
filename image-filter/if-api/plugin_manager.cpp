#include "plugin_manager.hpp"
#include "image_filter.h"
#include "os_specific_impl.hpp"
#include <map>

static std::map<std::string, fptr> commands;

void PluginManager_register(const char *command, fptr fp) { commands[command] = fp; }

void *PluginManager_execute(const char *command, void *arg) { return commands[command](arg); }

bool PluginManager_command_exists(const char *command)
{
    return commands.find(command) != commands.end();
}

Plugin::Plugin(const std::filesystem::path &path) : path(path)
{
    handle = (DLLHandle)load_handle(path.generic_string().c_str());
    if (!handle)
    {
        throw std::runtime_error(get_dll_error());
    }
    // Load all required symbols from the DLL
    plugin_get_name = (const char *(*)())get_symbol(handle, "Plugin_Name");
    plugin_get_id = (const char *(*)())get_symbol(handle, "Plugin_Id");
    plugin_init = (void (*)())get_symbol(handle, "Plugin_Init");
    plugin_destroy = (void (*)())get_symbol(handle, "Plugin_Destroy");
    std::cout << "[INFO] Loaded plugin: " << path.filename() << std::endl;
}

// Handle is automatically closed when destructor is run
Plugin::~Plugin()
{
    destroy();
    close_handle(handle);
}

// Return the name of the plugin
const char *Plugin::get_name() { return plugin_get_name(); }

const char *Plugin::get_id() { return plugin_get_id(); }

void Plugin::init() { plugin_init(); }

void Plugin::destroy() { plugin_destroy(); }

// This function loads all shared objects from the given path
void PluginManager::load_from_directory(const std::filesystem::path &path)
{
    // First check if the path exists
    if (!std::filesystem::exists(path))
    {
        return;
    }
    if (!std::filesystem::is_directory(path))
    {
        return;
    }
    for (const auto &dirEntry : std::filesystem::directory_iterator(path))
    {
        // Check if the entry exists, also check if it is a regular file or a symlink
        if (std::filesystem::exists(dirEntry) &&
            (std::filesystem::is_regular_file(dirEntry) || std::filesystem::is_symlink(dirEntry)))
        {
            // Check if the file has the OS specific extension - i.e. .dll for windows, .so for
            // linux
            if (dirEntry.path().extension() != get_plugin_extension())
            {
                continue;
            }
            try
            {
                // Load the plugin
                auto plugin = std::make_shared<Plugin>(dirEntry.path().generic_string());
                // Check if the plugin is already loaded, i.e. this is a duplicate
                // If so, remove it
                if (plugin_ids.find(plugin->get_id()) != plugin_ids.end())
                {
                    std::cout << "[INFO] Duplicate plugin " << dirEntry.path().filename()
                              << " found. Removing it" << std::endl;
                    continue;
                }
                plugin_ids.insert(plugin->get_id());
                plugins.push_back(plugin);
            }
            catch (std::exception &e)
            {
                std::cerr << "[ERROR] Could not load " << dirEntry << std::endl;
                std::cerr << e.what() << std::endl;
            }
        }
    }
}

void PluginManager::init()
{
    for (auto &plugin : plugins)
    {
        std::cout << "[INFO] Initializing " << plugin->get_name() << " [" << plugin->get_id() << "]"
                  << std::endl;
        plugin->init();
    }
}

size_t PluginManager::number_of_plugins_loaded() { return plugins.size(); }

// Unloads all loaded plugins
void PluginManager::unload() { plugins.clear(); }

void PluginManager::list_commands()
{
    if (commands.empty())
    {
        std::cout << "No commands registered .... check if plugins have been loaded" << std::endl;
        return;
    }
    for (const auto &command : commands)
    {
        if (command.first.size() >= 2 && command.first[0] == '-' && command.first[1] == '-')
        {
            // A hidden command, do not show
            continue;
        }
        std::cout << command.first << " ";
    }
    std::cout << std::endl;
}

void PluginManager::execute_command(const std::string &command)
{
    if (commands.find(command) != commands.end())
    {
        commands[command](NULL);
    }
    else
    {
        std::cerr << "Unrecognized command \"" << command
                  << "\", type \"list\" to see list of available commands" << std::endl;
    }
}

std::vector<std::filesystem::path> PluginManager::get_search_paths() { return ::get_search_paths(); }