#pragma once
#include <filesystem>
#include <iostream>
#include <set>
#include <string>
#include <vector>
#if defined(_WIN64) || defined(_WIN32)
#define EXPORT __declspec(dllexport)
#define IMPORT __declspec(dllimport)
#include <windows.h>
typedef HINSTANCE DLLHandle;
#elif defined(__unix__) || defined(__APPLE__) || defined(__linux__)
#define EXPORT __attribute__((visibility("default")))
#define IMPORT
#include <dlfcn.h>
typedef void *DLLHandle;
#endif
/*
 * This class represents a plugin (shared object).
 * It holds a handle to the shared library, and path to the shared library file
 */
class Plugin
{
    DLLHandle handle;
    std::filesystem::path path;
    const char *(*plugin_get_name)();
    const char *(*plugin_get_id)();
    void (*plugin_init)();
    void (*plugin_destroy)();

  public:
    Plugin(const std::filesystem::path &path);

    ~Plugin();

    const char *get_name();

    const char *get_id();

    void init();

    void destroy();
};

/*
 * This class manages a number of plugins.
 */
class PluginManager
{
    std::vector<std::shared_ptr<Plugin>> plugins;
    std::set<std::string> plugin_ids;

  public:
    void load_from_directory(const std::filesystem::path &path);

    void init();

    size_t number_of_plugins_loaded();

    void unload();

    void list_commands();

    void execute_command(const std::string &command);
    
    std::vector<std::filesystem::path> get_search_paths();
};