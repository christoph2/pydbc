#!/usr/bin/env python

import multiprocessing as mp
import os
import platform
import re
import subprocess  # nosec
import sys
import sysconfig
from pathlib import Path
from tempfile import TemporaryDirectory


TOP_DIR = Path(__file__).parent

print("Platform", platform.system())
uname = platform.uname()
if uname.system == "Darwin":
    os.environ["MACOSX_DEPLOYMENT_TARGET"] = "11.0"

VARS = sysconfig.get_config_vars()


def get_python_base() -> str:
    # Applies in this form only to Windows.
    if "base" in VARS and VARS["base"]:  # noqa: RUF019
        return VARS["base"]
    if "installed_base" in VARS and VARS["installed_base"]:  # noqa: RUF019
        return VARS["installed_base"]


def alternate_libdir(pth: str):
    base = Path(pth).parent
    libdir = Path(base) / "libs"
    if libdir.exists():
        # available_libs = os.listdir(libdir)
        return str(libdir)
    else:
        return ""


def get_py_config() -> dict:
    pynd = VARS["py_version_nodot"]  # Should always be present.
    include = sysconfig.get_path("include")  # Seems to be cross-platform.
    if uname.system == "Windows":
        base = get_python_base()
        library = f"python{pynd}.lib"
        libdir = Path(base) / "libs"
        if libdir.exists():
            available_libs = os.listdir(libdir)
            if library in available_libs:
                libdir = str(libdir)
            else:
                libdir = ""
        else:
            libdir = alternate_libdir(include)
    else:
        library = VARS["LIBRARY"]
        DIR_VARS = (
            "LIBDIR",
            "BINLIBDEST",
            "DESTLIB",
            "LIBDEST",
            "MACHDESTLIB",
            "DESTSHARED",
            "LIBPL",
        )
        arch = None
        if uname.system == "Linux":
            arch = VARS.get("MULTIARCH", "")
        found = False
        for dir_var in DIR_VARS:
            if found:
                break
            dir_name = VARS.get(dir_var)
            if not dir_name:
                continue
            if uname.system == "Darwin":
                full_path = [Path(dir_name) / library]
            elif uname.system == "Linux":
                full_path = [Path(dir_name) / arch / library, Path(dir_name) / library]
            else:
                pass
            for fp in full_path:
                print(f"Trying {fp!r}")
                if fp.exists():
                    print(f"found Python library: {fp!r}")
                    libdir = str(fp.parent)
                    found = True
                    break
        if not found:
            print("Could NOT locate Python library.")
            return None
    return dict(exe=sys.executable, include=include, libdir=libdir, library=library)


def banner(msg: str) -> None:
    print("=" * 80)
    print(str.center(msg, 80))
    print("=" * 80)


def get_env_int(name: str, default: int = 0) -> int:
    return int(os.environ.get(name, default))


def get_env_bool(name: str, default: int = 0) -> bool:
    return get_env_int(name, default)


def build_extension(debug: bool = False, use_temp_dir: bool = False) -> None:
    print("build_ext::build_extension()")

    use_temp_dir = use_temp_dir or get_env_bool("BUILD_TEMP")
    debug = debug or get_env_bool("BUILD_DEBUG")

    cfg = "Debug" if debug else "Release"
    bits, linkage = platform.architecture()
    print(f"Bits: {bits!r} Linkage: {linkage!r} Build-Type: {cfg!r}")

    cmake_args = []

    # Locate pybind11's CMake config directory so that `find_package(pybind11 CONFIG REQUIRED)`
    # works reliably across all platforms (esp. Windows, where pybind11's install prefix
    # inside the isolated PEP 517 build environment is not on CMAKE_PREFIX_PATH).
    pybind11_cmake_dir = ""
    try:
        pybind11_cmake_dir = subprocess.check_output(  # nosec
            [sys.executable, "-m", "pybind11", "--cmakedir"], text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            import pybind11  # type: ignore

            pybind11_cmake_dir = pybind11.get_cmake_dir()
        except Exception as exc:  # pragma: no cover
            print(f"WARNING: Could not locate pybind11 CMake dir: {exc!r}")
    if pybind11_cmake_dir:
        print(f"Using pybind11 CMake dir: {pybind11_cmake_dir!r}")
        os.environ["pybind11_DIR"] = pybind11_cmake_dir

    py_cfg = get_py_config()
    if py_cfg is not None:
        cmake_args = [
            f"-DPython3_EXECUTABLE={py_cfg['exe']}",
            f"-DPython3_INCLUDE_DIR={py_cfg['include']}",
            f"-DCMAKE_BUILD_TYPE={cfg}",  # not used on MSVC, but no harm
        ]
        if pybind11_cmake_dir:
            cmake_args.append(f"-Dpybind11_DIR={pybind11_cmake_dir}")
        # Only add library path if we found one
        if py_cfg["libdir"]:
            cmake_args.append(
                f"-DPython3_LIBRARY={str(Path(py_cfg['libdir']) / Path(py_cfg['library']))}"
            )
        else:
            print("INFO: No explicit Python library path - CMake will auto-detect")

    build_args = ["--config Release", "--verbose"]

    if sys.platform.startswith("darwin"):
        # Cross-compile support for macOS - respect ARCHFLAGS if set
        archs = re.findall(r"-arch (\S+)", os.environ.get("ARCHFLAGS", ""))
        if archs:
            cmake_args += ["-DCMAKE_OSX_ARCHITECTURES={}".format(";".join(archs))]

    if use_temp_dir:
        build_temp = (
            Path(TemporaryDirectory(suffix=".build-temp").name) / "extension_it_in"
        )
    else:
        build_temp = Path(".")
    if not build_temp.exists():
        build_temp.mkdir(parents=True)

    # Clean CMake cache to avoid conflicts when building multiple Python versions in sequence
    cmake_cache = build_temp / "CMakeCache.txt"
    if cmake_cache.exists():
        cmake_cache.unlink()

    banner("Step #1: Configure")
    # cmake_args += ["--debug-output"]
    subprocess.run(
        ["cmake", "-S", str(TOP_DIR), *cmake_args], cwd=build_temp, check=True
    )  # nosec

    cmake_args += [f"--parallel {mp.cpu_count()}"]

    banner("Step #2: Build")
    # build_args += ["-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON"]
    subprocess.run(
        ["cmake", "--build", str(build_temp), *build_args], cwd=TOP_DIR, check=True
    )  # nosec

    banner("Step #3: Install")
    # subprocess.run(["cmake", "--install", "."], cwd=build_temp, check=True)  # nosec
    subprocess.run(["cmake", "--install", build_temp], cwd=TOP_DIR, check=True)  # nosec


if __name__ == "__main__":
    build_extension(use_temp_dir=False)
