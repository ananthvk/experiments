#include "plugin_manager.hpp"
#if defined(_WIN64) || defined(_WIN32)
// Loads a shared object using dlopen() and returns the opened handle
void *load_handle(const char *filename) { return LoadLibrary(filename); }

// Returns a dlerror() as std::string
std::string get_dll_error()
{
    DWORD error_id = GetLastError();
    if (!error_id)
    {
        // No errors
        return std::string();
    }
    return std::system_category().message(error_id);
}

// Get a symbol in a shared library
void *get_function_by_name(DLLHandle handle, const char *name)
{
    return (void *)GetProcAddress(handle, name);
}

// Close the shared object handle
void close_handle(DLLHandle handle) { FreeLibrary(handle); }

// Return path to the directory in which the executable program is present
std::filesystem::path get_executable_dir()
{
    TCHAR szFileName[MAX_PATH];
    GetModuleFileName(NULL, szFileName, MAX_PATH);
    return std::filesystem::canonical(szFileName).parent_path();
}

// Return the shared object extension for this system (.dll)
const char *get_plugin_extension() { return ".dll"; }

// Return paths to check for plugins
std::vector<std::filesystem::path> get_search_paths()
{
    std::vector<std::filesystem::path> paths = {
        get_executable_dir(), get_executable_dir().append("plugins"), "~/.image-filter/plugins"};
    return paths;
}


#elif defined(__unix__) || defined(__APPLE__) || defined(__linux__)
// Loads a shared object using dlopen() and returns the opened handle
void *load_handle(const char *filename) { return dlopen(filename, RTLD_LAZY | RTLD_LOCAL); }

// Returns a dlerror() as std::string
std::string get_dll_error() { return std::string(dlerror()); }

// Get a symbol in a shared library
void *get_function_by_name(DLLHandle handle, const char *name) { return dlsym(handle, name); }

// Close the shared object handle
void close_handle(DLLHandle handle) { dlclose(handle); }

// Return path to the directory in which the executable program is present
std::filesystem::path get_executable_dir()
{
    // For linux use /proc/self/exe
    return std::filesystem::canonical("/proc/self/exe").parent_path();
}

// Return the shared object extension for this system (.so)
const char *get_plugin_extension() { return ".so"; }

// Return paths to check for plugins
std::vector<std::filesystem::path> get_search_paths()
{
    std::vector<std::filesystem::path> paths = {
        get_executable_dir(), get_executable_dir().append("plugins"), "~/.image-filter/plugins"};
    return paths;
}
#endif

// A wrapper around get_function_by_name, which throws a runtime error if the symbol is not found
void *get_symbol(DLLHandle handle, const char *name)
{
    void *fptr = get_function_by_name(handle, name);
    if (!fptr)
    {
        auto err = get_dll_error();
        close_handle(handle);
        throw std::runtime_error(err);
    }
    return fptr;
}
