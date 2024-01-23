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

add_executable(${PROJECT_NAME}
  src/main.cpp
)

if(NEED_CONSOLE)
  target_compile_definitions(${PROJECT_NAME}
  PRIVATE
    NEED_CONSOLE
  )
endif()

target_link_libraries(${PROJECT_NAME}
PRIVATE
  libpython-static
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
endif()
