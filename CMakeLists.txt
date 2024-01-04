cmake_minimum_required(VERSION 3.4...3.18)
project(python_embed)

if(${WIN32})
  set(PYTHON_EXECUTABLE
    ${CMAKE_SOURCE_DIR}/.venv/Scripts/python.exe
  )
else()
  set(PYTHON_EXECUTABLE
    ${CMAKE_SOURCE_DIR}/.venv/bin/python.exe
  )
endif()
add_subdirectory(thirdparty)

add_executable(${PROJECT_NAME}
  src/main.cpp
)

target_link_libraries(${PROJECT_NAME}
PRIVATE
  pybind11::embed
)

if(${WIN32})
  add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_RUNTIME_DLLS:${PROJECT_NAME}> $<TARGET_FILE_DIR:${PROJECT_NAME}>
    COMMAND_EXPAND_LISTS
  )
endif()
