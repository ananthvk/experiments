#include "image_filter.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#include "stb_image_write.h"
#include <iostream>
#include <stdlib.h>
#include <string>

static struct Image
{
    std::string filename;
    uint8_t *data;
    int width;
    int height;
    int channels;
} image;

bool loaded = false;


extern "C"
{

    uint8_t *ImageFilter_create_image(int width, int height, int channels)
    {
        return (uint8_t *)malloc(width * height * channels);
    }

    bool ImageFilter_write_image(const char *filename, int width, int height, int channels,
                                 uint8_t *data)
    {
        if (!stbi_write_png(filename, width, height, channels, data, width * channels))
        {
            return false;
        }
        return true;
    }

    void ImageFilter_destroy_image(uint8_t *data) { free(data); }

    void ImageFilter_set_image(int width, int height, int channels, uint8_t *data)
    {
        image.channels = channels;
        image.height = height;
        image.width = width;
        image.data = data;
    }

    int ImageFilter_get_width() { return image.width; }

    int ImageFilter_get_height() { return image.height; }

    int ImageFilter_get_channels() { return image.channels; }

    uint8_t *ImageFilter_get_image() { return image.data; }

    bool ImageFilter_load_image(const char *filename)
    {
        // If an image is already loaded, free it
        if(loaded)
        {
            free(image.data);
            loaded = false;
        }
        image.data = stbi_load(filename, &(image.width), &(image.height), &(image.channels), 0);
        if (!image.data)
        {
            return false;
        }
        image.filename = filename;
        loaded = true;
        return true;
    }

    void ImageFilter_reset()
    {
        if (loaded)
        {
            ImageFilter_destroy_image(image.data);
            image.width = 0;
            image.height = 0;
            image.channels = 0;
            image.data = nullptr;
            loaded = false;
        }
    }
}

void ImageFilter_unload()
{
    std::cout << "[INFO] Stopping ImageFilter" << std::endl;
    if (loaded)
    {
        ImageFilter_destroy_image(image.data);
        image.width = 0;
        image.height = 0;
        image.channels = 0;
        image.data = nullptr;
        loaded = false;
    }
}