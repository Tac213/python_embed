set(third_party_dir "${CMAKE_CURRENT_SOURCE_DIR}")

if(NOT TARGET python)
    set(PYTHON_VERSION "3.12.2")
    set(WIN32_EMBEDED_APPLICATION_NAME "python_embed.exe")
    option(BUILD_LIBPYTHON_SHARED "" OFF)
    option(BUILD_EXTENSIONS_AS_BUILTIN "" ON)
    option(LOAD_NORMAL_EXTENSIONS_IN_DEBUG "" ON)
    add_subdirectory(python-cmake)
endif()

option(PYBIND11_NOPYTHON "" ON)
add_subdirectory(pybind11)
