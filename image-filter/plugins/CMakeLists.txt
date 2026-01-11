project(plugins)

set(SOURCES basic_filters.cpp core.cpp)
foreach(SRC ${SOURCES})
    get_filename_component(LIB_NAME ${SRC} NAME_WE)
    add_library(${LIB_NAME} SHARED ${SRC})
    target_include_directories(${LIB_NAME} PRIVATE ${CMAKE_SOURCE_DIR}/include)
    target_link_libraries(${LIB_NAME} PRIVATE if-api)
endforeach(SRC ${SOURCE_FILES})
