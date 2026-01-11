#include "plugin_manager.hpp"
#include <algorithm>
void ImageFilter_unload();

inline void ltrim(std::string &s)
{
    s.erase(s.begin(),
            std::find_if(s.begin(), s.end(), [](unsigned char ch) { return !std::isspace(ch); }));
}

inline void rtrim(std::string &s)
{
    s.erase(std::find_if(s.rbegin(), s.rend(), [](unsigned char ch) { return !std::isspace(ch); })
                .base(),
            s.end());
}

int main()
{
    std::cout << "[INFO] Started application" << std::endl;
    PluginManager manager;
    for (const auto &path : manager.get_search_paths())
        manager.load_from_directory(path);
    std::cout << "[INFO] Loaded " << manager.number_of_plugins_loaded() << " plugins" << std::endl;
    manager.init();
    std::string line;
    std::cout << "Type \"list\" to view the list of available commands and type \"exit\" to exit"
              << std::endl;
    std::cout << "> ";
    while (std::getline(std::cin, line))
    {
        ltrim(line);
        rtrim(line);
        if (line.empty())
            continue;
        if (line == "exit" || line == "quit")
            break;
        if (line == "list")
            manager.list_commands();
        else
            manager.execute_command(line);
        std::cout << "> ";
    }
    ImageFilter_unload();
}