project(if-api CXX)
set(SOURCES plugin_manager.cpp image_filter.cpp os_specific_impl.cpp)
add_library(${PROJECT_NAME} SHARED ${SOURCES})
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_SOURCE_DIR}/include)