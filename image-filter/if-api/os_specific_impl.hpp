#pragma once
#include <iostream>
#include <set>
#include <stdexcept>
#include <string>
#include <vector>
#include <filesystem>
#include <stdlib.h>

#if defined(_WIN64) || defined(_WIN32)
#define EXPORT __declspec(dllexport)
#define IMPORT __declspec(dllimport)
#include<windows.h>
typedef HINSTANCE DLLHandle;
#elif defined(__unix__) || defined(__APPLE__) || defined(__linux__)
#define EXPORT __attribute__((visibility("default")))
#define IMPORT
#include <dlfcn.h>
typedef void *DLLHandle;
#endif

// Loads a shared object using dlopen() and returns the opened handle
void *load_handle(const char *filename);

// Returns a dlerror() as std::string
std::string get_dll_error();

// Get a symbol in a shared library
void *get_function_by_name(DLLHandle handle, const char *name);

// Close the shared object handle
void close_handle(DLLHandle handle);

// Return path to the directory in which the executable program is present
std::filesystem::path get_executable_dir();

// Return the shared object extension for this system (.dll)
const char *get_plugin_extension(); 

// Return paths to check for plugins
std::vector<std::filesystem::path> get_search_paths();

// A wrapper around get_function_by_name, which throws a runtime error if the symbol is not found
void *get_symbol(DLLHandle handle, const char *name);

