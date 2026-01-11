#include "image_filter.h"
#include <iostream>
extern "C"
{
    const char *Plugin_Name() { return "Basic filters"; }

    const char *Plugin_Id() { return "001"; }

    void *grayscale_filter(void*)
    {
        if (!ImageFilter_get_image())
        {
            std::cerr << "ERROR: No image loaded yet!, load an image to apply a filter"
                      << std::endl;
            return NULL;
        }
        int channels = ImageFilter_get_channels();
        if (!(channels == 3 || channels == 4))
        {
            std::cerr << "ERROR: This filter requires 3(RGB) or 4(RGBA) channels images"
                      << std::endl;
            return NULL;
        }
        int width = ImageFilter_get_width();
        int height = ImageFilter_get_height();
        uint8_t *img = ImageFilter_get_image();
        for (int i = 0; i < width * height; i++)
        {
            uint8_t avg = ((img[i * channels] + img[i * channels + 1] + img[i * channels + 2]) / 3)%256;
            img[i * channels] = avg;
            img[i * channels + 1] = avg;
            img[i * channels + 2] = avg;
        }
        return NULL;
    }

    void Plugin_Init()
    {
        // Perform initialization, such as registering commands
        PluginManager_register("grayscale", grayscale_filter);
    }

    void Plugin_Destroy()
    {
        // Cleanup resources
    }
}