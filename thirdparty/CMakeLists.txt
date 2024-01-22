set(third_party_dir "${CMAKE_CURRENT_SOURCE_DIR}")

if(NOT TARGET python)
    set(PYTHON_VERSION "3.11.7")
    option(BUILD_LIBPYTHON_SHARED "" ON)
    option(BUILD_EXTENSIONS_AS_BUILTIN "" ON)
    add_subdirectory(python-cmake)
endif()
