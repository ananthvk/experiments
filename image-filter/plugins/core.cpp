#include "image_filter.h"
#include <iostream>
extern "C"
{
    const char *Plugin_Name() { return "Core"; }

    const char *Plugin_Id() { return "000"; }

    void *load_image(void *)
    {
        std::cout << "Filename: ";
        std::string filename;
        std::cin >> filename;
        if (!ImageFilter_load_image(filename.c_str()))
        {
            std::cerr << "Could not load image" << std::endl;
            return NULL;
        }
        return NULL;
    }

    void *save_image(void *)
    {
        if (!ImageFilter_get_image())
        {
            std::cerr << "No image loaded yet!" << std::endl;
            return NULL;
        }
        std::string filename;
        std::cout << "Output filename: ";
        std::cin >> filename;
        if (!ImageFilter_write_image(filename.c_str(), ImageFilter_get_width(),
                                     ImageFilter_get_height(), ImageFilter_get_channels(),
                                     ImageFilter_get_image()))
        {
            // TODO: Display actual cause of error
            std::cerr << "Could not write image" << std::endl;
        }
        return NULL;
    }

    void *get_image_info(void *)
    {

        if (!ImageFilter_get_image())
        {
            std::cerr << "No image loaded yet!" << std::endl;
            return NULL;
        }
        std::cout << "Width: " << ImageFilter_get_width() << std::endl;
        std::cout << "Height: " << ImageFilter_get_height() << std::endl;
        std::cout << "Channels: " << ImageFilter_get_channels() << std::endl;
        return NULL;
    }

    void Plugin_Init()
    {
        // Perform initialization, such as registering commands
        PluginManager_register("load", load_image);
        PluginManager_register("save", save_image);
        PluginManager_register("info", get_image_info);
    }

    void Plugin_Destroy()
    {
        // Cleanup resources
    }
}