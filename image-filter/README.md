# image-filter

The goal of this project is to implement a cross platform plugin system for an image filter application. The plugins should be compiled as either `.dll` or as `.so` and placed in a folder. The main program should find all plugins, load them and execute them depending upon the requirements.
Plugins are widely used in various applications to provide the user a way to extend functionality without recompiling. Examples include browser plugins, VS Code extensions, game mods, etc.

## What Are Image Filters?

Image filters are algorithms which operate on images (2 dimensional array of pixels) to produce various outputs. For example a blur filter blurs the input image, a sharpen mask sharpens the image, etc.
These filters could be implemented directly in the main application but that would mean for each new filter, the application has to be recompiled. To avoid that, the filters can be implemented as shared objects (`.dll / .so`).

## Requirements

- Dynamic loading of code using shared objects / DLLs
- Command line application

## Planned Usage
Interactive mode:
```
$ image-filter
> load cat.png 
> blur 50
> grayscale
> save cat_out.png
> exit
```

## API

A plugin manager should read all shared objects / DLLs in a directory, use `dlopen` or `LoadLibraryEx` to load it, then find the required symbols.

The Plugin must implement the following API
```
#include "image_filter.h"
extern "C" 
{
    const char* Plugin_Name()
    {
        // Return the name of the plugin
    }
    const char* Plugin_Id()
    {
        // Return the unique ID of the plugin (preferably UUID)
    }
    void Plugin_Init()
    {
        // Perform initialization, such as registering commands
    }
    void Plugin_Destroy()
    {
        // Cleanup resources
    }
}
```

## How to run?

Currently, for demonstrating runtime loading of plugins, this project builds a subproject `plugins`, after which the shared library files are stored in `plugins` folder of the build directory.
Practically, the plugins will be built separately and then copied over to the plugins folder.

To run this project,
```
$ git clone https://github.com/ananthvk/image-filter
$ cd image-filter
$ mkdir build
$ cd build
$ cmake ..
$ cmake --build .
$ ./image-filter
```

## Advantages and disadvantages of plugin system
Advantage of a plugin system is that it improves flexiblity and permits parallel development. Many developers can develop various components (here, filters) parallely. As the main application does not need to be recompiled each time, it can save testing and development time.
It also allows users to extend functionality by installing custom plugins.

Disadvantages include increase in complexity of code, dependency on platform specific features or libraries, increased testing and slightly slower code. 

## TODOs
- [ ] Better error messages in case of failure
- [ ] Support other file extensions while saving (currently only png)

## Note:
Currently does not run on Windows, works only on Linux
