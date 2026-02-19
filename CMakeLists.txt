
cmake_minimum_required(VERSION 3.20...3.30)
project(pydbc_extensions LANGUAGES C CXX)

cmake_policy(SET CMP0135 NEW)
cmake_policy(SET CMP0094 NEW)

find_package(Python3 COMPONENTS Interpreter Development.Module REQUIRED)

include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11
  GIT_TAG        v2.13.6
)
FetchContent_MakeAvailable(pybind11)


SET(CMAKE_C_STANDARD 17)
# set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED YES)

set(CMAKE_POSITION_INDEPENDENT_CODE ON)
message( STATUS "Found pybind11 v${pybind11_VERSION} ${pybind11_VERSION_TYPE}: ${pybind11_INCLUDE_DIRS}")


set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/dist")

SET(GCC_N_CLANG_BASE_OPTIONS "-Wall -Wextra -Wpedantic -Warray-bounds -mtune=native -fexceptions")

SET(MSVC_BASE_OPTIONS "/W3 /permissive- /EHsc /bigobj /Zc:__cplusplus /std:c++latest")



if (CMAKE_BUILD_TYPE STREQUAL "Debug")
	if (MSVC)
		SET(MSVC_BASE_OPTIONS "${MSVC_BASE_OPTIONS} /Od /fsanitize=address /Zi /FAcs")
	else()
		SET(GCC_N_CLANG_BASE_OPTIONS "${GCC_N_CLANG_BASE_OPTIONS} -Og -g3 -ggdb -fno-omit-frame-pointer -fsanitize=address -fsanitize=undefined -fsanitize=bounds")	# -fsanitize=hwaddress
	endif()
else ()
	if (MSVC)
		SET(MSVC_BASE_OPTIONS "${MSVC_BASE_OPTIONS} /Ox")
	else()
		SET(GCC_N_CLANG_BASE_OPTIONS "${GCC_N_CLANG_BASE_OPTIONS} -O3 -fomit-frame-pointer")
	endif()
 endif ()


if (CMAKE_SYSTEM_NAME STREQUAL  "Darwin")
    set(ENV{MACOSX_DEPLOYMENT_TARGET}  "11.0")
	SET(GCC_N_CLANG_EXTRA_OPTIONS "-stdlib=libc++")
	message("Platform is Darwin")
elseif (CMAKE_SYSTEM_NAME STREQUAL  "Windows")
	message("Platform is WINDOWS")
	SET(MSVC_EXTRA_OPTIONS "")
elseif (CMAKE_SYSTEM_NAME STREQUAL  "Linux")
    SET(GCC_N_CLANG_EXTRA_OPTIONS "-fvisibility=hidden -g0") # -fcoroutines
	message("Platform is LINUX")
endif()


IF (CMAKE_C_COMPILER_ID STREQUAL "GNU")

ELSEIF (CMAKE_C_COMPILER_ID MATCHES "Clang")

ELSEIF (CMAKE_C_COMPILER_ID MATCHES "MSVC")

ELSE ()

ENDIF ()

IF (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")

ELSEIF (CMAKE_CXX_COMPILER_ID MATCHES "Clang")

ELSEIF (CMAKE_CXX_COMPILER_ID MATCHES "MSVC")

ELSE ()


ENDIF ()

message("Compiling C with: " ${CMAKE_C_COMPILER_ID})
message("Compiling Cpp with: " ${CMAKE_CXX_COMPILER_ID})

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/pydbc/cpp_ext)

# List all source files needed for the extension
set(DBC_EXTENSION_SOURCES
    pydbc/cpp_ext/dbc_extension.cpp
)

set(LDF_EXTENSION_SOURCES
    pydbc/cpp_ext/ldf_extension.cpp
)

pybind11_add_module(dbc_extension ${DBC_EXTENSION_SOURCES})
pybind11_add_module(ldf_extension ${LDF_EXTENSION_SOURCES})

target_compile_options(dbc_extension PUBLIC "-DEXTENSION_NAME=dbc_extension" PUBLIC $<$<AND:$<COMPILE_LANGUAGE:CXX>,$<CXX_COMPILER_ID:MSVC>>:/utf-8>)
target_compile_options(ldf_extension PUBLIC "-DEXTENSION_NAME=ldf_extension" PUBLIC $<$<AND:$<COMPILE_LANGUAGE:CXX>,$<CXX_COMPILER_ID:MSVC>>:/utf-8>)

IF (CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
	SET(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} ${GCC_N_CLANG_BASE_OPTIONS} ${GCC_N_CLANG_EXTRA_OPTIONS}")
	target_link_options(dbc_extension PUBLIC -flto=auto)
    target_link_options(ldf_extension PUBLIC -flto=auto)
ELSEIF (MSVC)
	SET(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} ${MSVC_BASE_OPTIONS} ${MSVC_EXTRA_OPTIONS}")
ENDIF()

# Install to the correct location within the package
install(TARGETS dbc_extension DESTINATION pydbc/cpp_ext)
install(TARGETS ldf_extension DESTINATION pydbc/cpp_ext)
