cmake_minimum_required(VERSION 3.12)
project(image-filter-project CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

if(MSVC)
  add_compile_options(/W4 /WX)
  add_link_options(/FORCE:UNRESOLVED)
  add_compile_definitions(_CRT_SECURE_NO_WARNINGS)

else()
  add_compile_options(-Wall -Wextra -Wpedantic -Wno-unused-parameter)
endif()

add_subdirectory(if-api)
add_subdirectory(src)
add_subdirectory(plugins)