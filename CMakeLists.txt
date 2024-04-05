cmake_minimum_required(VERSION 3.4...3.18)
project(python_embed)

set(CMAKE_CXX_STANDARD 20)

option(NEED_CONSOLE "Whether to build a console application." ON)
option(FREEZE_APPLICATION "Whether to freeze the python application." OFF)

if(${WIN32})
  set(PYTHON_EXECUTABLE
    ${CMAKE_SOURCE_DIR}/.venv/Scripts/python.exe
  )
else()
  set(PYTHON_EXECUTABLE
    ${CMAKE_SOURCE_DIR}/.venv/bin/python
  )
endif()

add_subdirectory(thirdparty)

set(SOURCES
  ${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp
)

if(FREEZE_APPLICATION)
  set(ENTRY_MODULE_NAME python_embed)
  set(HIDDEN_IMPORTS "encodings.cp437")
  set(EXCLUDES "test,unittest")

  # Get frozen header file names
  execute_process(
    COMMAND ${PYTHON_EXECUTABLE} "${CMAKE_SOURCE_DIR}/scripts/generate_frozen_modules.py" "--get-frozen-header-file-names" "${ENTRY_MODULE_NAME}"
    "--hidden-imports=${HIDDEN_IMPORTS}" "--excludes=${EXCLUDES}"
    OUTPUT_VARIABLE _frozen_headers
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE _resullt
  )

  if(${_resullt})
    message(FATAL_ERROR "Failed to get frozen header file names.")
  endif()

  add_custom_command(
    OUTPUT ${_frozen_headers}
    COMMAND
    ${CMAKE_CROSSCOMPILING_EMULATOR} ${PYTHON_EXECUTABLE} "${CMAKE_SOURCE_DIR}/scripts/generate_frozen_modules.py" "--make-freeze" $<TARGET_FILE:_freeze_module>
    "${ENTRY_MODULE_NAME}" "--hidden-imports=${HIDDEN_IMPORTS}" "--excludes=${EXCLUDES}"
    DEPENDS
    _freeze_module
    WORKING_DIRECTORY
    ${CMAKE_SOURCE_DIR}
    COMMENT
    "Generating frozen module headers"
  )

  set(SOURCES
    ${SOURCES}
    ${_frozen_headers}
  )
endif()

add_executable(${PROJECT_NAME}
  ${SOURCES}
)

if(NEED_CONSOLE)
  target_compile_definitions(${PROJECT_NAME}
    PRIVATE
    NEED_CONSOLE
  )
endif()

if(FREEZE_APPLICATION)
  target_compile_definitions(${PROJECT_NAME}
    PRIVATE
    FREEZE_APPLICATION
  )
endif()

target_link_libraries(${PROJECT_NAME}
  PRIVATE
  libpython-static
  pybind11::headers
)

if(${WIN32})
  add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_RUNTIME_DLLS:${PROJECT_NAME}> $<TARGET_FILE_DIR:${PROJECT_NAME}>
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:libpython3-shared> $<TARGET_FILE_DIR:${PROJECT_NAME}>
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
  if(FREEZE_APPLICATION)
    add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
      COMMAND ${PYTHON_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/scripts/assemble_application.py"
      "${ENTRY_MODULE_NAME}" "--hidden-imports=${HIDDEN_IMPORTS}" "--excludes=${EXCLUDES}" "--binaries=$<TARGET_FILE:${PROJECT_NAME}>,$<TARGET_FILE:libpython3-shared>"
      "--pyside6-modules=PySide6.QtWidgets"
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    )
  endif()
endif()
