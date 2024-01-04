set(third_party_dir "${CMAKE_CURRENT_SOURCE_DIR}")

if(NOT TARGET pybind11)
  add_subdirectory(pybind11)
endif()
