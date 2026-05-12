cmake_minimum_required(VERSION 3.16)

project(dbc_extension LANGUAGES CXX)

# C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Release by default if not specified
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type" FORCE)
endif()

# Collect sources
set(SRC_FILES
    "${CMAKE_CURRENT_SOURCE_DIR}/main.cpp"
)

add_executable(dbc-parser ${SRC_FILES})
target_include_directories(dbc-parser PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Python extension
include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11
  GIT_TAG        v2.13.6
)
FetchContent_MakeAvailable(pybind11)

pybind11_add_module(pydbc_cpp dbc_extension.cpp)
target_include_directories(pydbc_cpp PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

pybind11_add_module(ldf_extension ldf_extension.cpp)
target_include_directories(ldf_extension PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

pybind11_add_module(ncf_extension ncf_extension.cpp)
target_include_directories(ncf_extension PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Compiler-Warnungen (plattformabhängig)
if(MSVC)
  target_compile_options(dbc-parser PRIVATE /W4 /permissive-)
  target_compile_options(pydbc_cpp PRIVATE /W4 /permissive-)
  target_compile_options(ldf_extension PRIVATE /W4 /permissive-)
  target_compile_options(ncf_extension PRIVATE /W4 /permissive-)
else()
  target_compile_options(dbc-parser PRIVATE -Wall -Wextra -Wpedantic -Wno-sign-compare)
  target_compile_options(pydbc_cpp PRIVATE -Wall -Wextra -Wpedantic -Wno-sign-compare)
  target_compile_options(ldf_extension PRIVATE -Wall -Wextra -Wpedantic -Wno-sign-compare)
  target_compile_options(ncf_extension PRIVATE -Wall -Wextra -Wpedantic -Wno-sign-compare)
  target_compile_options(dbc-parser PRIVATE -fdiagnostics-color=always)
  target_compile_options(pydbc_cpp PRIVATE -fdiagnostics-color=always)
  target_compile_options(ldf_extension PRIVATE -fdiagnostics-color=always)
  target_compile_options(ncf_extension PRIVATE -fdiagnostics-color=always)
endif()

# Optional: install target
install(TARGETS dbc-parser RUNTIME DESTINATION bin)