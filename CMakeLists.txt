cmake_minimum_required(VERSION 3.4...3.18)
project(python_embed)

set(CMAKE_CXX_STANDARD 20)

add_subdirectory(thirdparty)

option(NEED_CONSOLE "Whether to build a console application." ON)

if(${WIN32})
  set(PYTHON_EXECUTABLE
    ${CMAKE_SOURCE_DIR}/.venv/Scripts/python.exe
  )
else()
  set(PYTHON_EXECUTABLE
    ${CMAKE_SOURCE_DIR}/.venv/bin/python
  )
endif()

# Macro to get various python include / link flags.
macro(python_config option output_var)
  if(${ARGC} GREATER 2)
    set(is_list ${ARGV2})
  else()
    set(is_list "")
  endif()

  execute_process(
    COMMAND ${PYTHON_EXECUTABLE} "${CMAKE_SOURCE_DIR}/scripts/python_config.py"
            ${option}
    OUTPUT_VARIABLE ${output_var}
    OUTPUT_STRIP_TRAILING_WHITESPACE)

  if ("${${output_var}}" STREQUAL "")
    message(FATAL_ERROR "Error: Calling python_config.py ${option} returned no output.")
  endif()
  if(is_list)
    string (REPLACE " " ";" ${output_var} "${${output_var}}")
  endif()
endmacro()

# python_config(--python-include-path PYTHON_INCLUDE_DIR)
python_config(--python-link-flags-cmake PYTHON_LINKING_DATA 0)

add_executable(${PROJECT_NAME}
  src/main.cpp
)

# target_include_directories(${PROJECT_NAME}
# PRIVATE
#   ${PYTHON_INCLUDE_DIR}
# )

if(NEED_CONSOLE)
  target_compile_definitions(${PROJECT_NAME}
  PRIVATE
    NEED_CONSOLE
  )
endif()

# Find and link to the python library.
list(GET PYTHON_LINKING_DATA 0 PYTHON_LIBDIR)
list(GET PYTHON_LINKING_DATA 1 PYTHON_LIB_BASENAME)
find_library(PYTHON_LIB ${PYTHON_LIB_BASENAME} PATHS ${PYTHON_LIBDIR} HINTS ${PYTHON_LIBDIR})

target_link_libraries(${PROJECT_NAME}
PRIVATE
  libpython-static
  # ${PYTHON_LIB}
)

if(${WIN32})
  add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_RUNTIME_DLLS:${PROJECT_NAME}> $<TARGET_FILE_DIR:${PROJECT_NAME}>
    COMMAND_EXPAND_LISTS
  )
  set(PYTHON_VERSIONS_LIST 3 310 311 312)
  set(PYTHON_ADDITIONAL_LINK_FLAGS "")
  foreach(VER ${PYTHON_VERSIONS_LIST})
    set(PYTHON_ADDITIONAL_LINK_FLAGS
        "${PYTHON_ADDITIONAL_LINK_FLAGS} /NODEFAULTLIB:\"python${VER}_d.lib\"")
    set(PYTHON_ADDITIONAL_LINK_FLAGS
        "${PYTHON_ADDITIONAL_LINK_FLAGS} /NODEFAULTLIB:\"python${VER}.lib\"")
  endforeach()
  set_target_properties(${PROJECT_NAME} PROPERTIES LINK_FLAGS "${PYTHON_ADDITIONAL_LINK_FLAGS}")
  if(NOT NEED_CONSOLE)
    set_target_properties(${PROJECT_NAME} PROPERTIES WIN32_EXECUTABLE 1)
  endif()
endif()
