"""
Scripts for cmake to link python
"""

import sys
import sysconfig
import re
import os
import dataclasses
from importlib import machinery


@dataclasses.dataclass
class PythonLinkData:
    """
    Helper data class for python link data
    """

    libdir: str
    lib: str


def is_debug() -> bool:
    """
    Check whether python is debug build
    Returns:
        bool
    """
    debug_suffix = "_d.pyd" if sys.platform == "win32" else "_d.so"
    return any(s.endswith(debug_suffix) for s in machinery.EXTENSION_SUFFIXES)


def python_version() -> str:
    """
    Get python version
    Returns:
        str
    """
    return f"{sys.version_info.major}.{sys.version_info.minor}"


def get_python_include_path() -> str:
    """
    Get python include path
    Returns:
        str
    """
    return sysconfig.get_path("include")


def python_link_flags_cmake() -> str:
    """
    Get cmake python link flags
    Returns:
        str
    """
    data = python_link_data()
    libdir = data.libdir
    lib = re.sub(r".dll$", ".lib", data.lib)
    return f"{libdir};{lib}"


def python_link_data() -> PythonLinkData:
    """
    Get python link data
    Returns:
        PythonLinkData
    """
    libdir = sysconfig.get_config_var("LIBDIR")
    if libdir is None:
        libdir = os.path.abspath(os.path.join(sysconfig.get_config_var("LIBDEST"), "..", "libs"))
    version = python_version()
    version_no_dots = version.replace(".", "")

    lib = ""
    if sys.platform == "win32":
        suffix = "_d" if is_debug() else ""
        lib = f"python{version_no_dots}{suffix}"

    elif sys.platform == "darwin":
        lib = f"python{version}"

    # Linux and anything else
    else:
        lib = f"python{version}{sys.abiflags}"  # pylint: disable=no-member

    return PythonLinkData(libdir, lib)


def main() -> None:
    """
    Entry point
    Returns:
        None
    """
    options = []

    # option, function, error, description
    options.append(
        (
            "--python-include-path",
            get_python_include_path,
            "Unable to locate the Python include headers directory.",
            "Print Python include path",
        )
    )
    options.append(
        (
            "--python-link-flags-cmake",
            python_link_flags_cmake,
            "Unable to locate the Python library for linking.",
            "Print python link flags for cmake",
        )
    )

    option = sys.argv[1]
    for argument, handler, error, _ in options:
        if option != argument:
            continue
        handler_result = handler()
        if handler_result is None:
            sys.exit(error)

        line = handler_result
        print(line)


if __name__ == "__main__":
    main()
