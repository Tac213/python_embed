set(third_party_dir "${CMAKE_CURRENT_SOURCE_DIR}")

if(NOT TARGET python)
    execute_process(
        COMMAND ${PYTHON_EXECUTABLE} "--version"
        OUTPUT_VARIABLE _venv_python_version_output
        OUTPUT_STRIP_TRAILING_WHITESPACE
        RESULT_VARIABLE _result
    )
    if(${_result})
        message(FATAL_ERROR "Failed to get python version.")
    endif()
    string(REGEX MATCH "([0-9]+\.)+([0-9]+)" _venv_python_version ${_venv_python_version_output})
    set(PYTHON_VERSION ${_venv_python_version})
    set(WIN32_EMBEDED_APPLICATION_NAME "python_embed.exe")
    option(BUILD_LIBPYTHON_SHARED "" OFF)
    option(BUILD_EXTENSIONS_AS_BUILTIN "" ON)
    option(LOAD_NORMAL_EXTENSIONS_IN_DEBUG "" ON)
    add_subdirectory(python-cmake)
endif()

option(PYBIND11_NOPYTHON "" ON)
add_subdirectory(pybind11)
