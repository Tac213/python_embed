"""
Script for generating source zip
"""

import sys
import os
import py_compile
import importlib
from importlib import machinery
import zipfile


def compile_pyc(src_file: str) -> bytes:
    """
    Compile source code to python byte code
    Returns:
        bytearray
    """
    if not os.path.isfile(src_file):
        raise RuntimeError(f"File {src_file} does not exist.")
    cfile = py_compile.compile(src_file, doraise=True)
    with open(cfile, "rb") as f:
        pyc = f.read()
    return pyc


def main() -> None:
    """
    Entry point
    Returns:
        None
    """
    entry_module_name = sys.argv[1]
    entry_module = importlib.import_module(entry_module_name)
    package_directory = os.path.dirname(entry_module.__file__)
    root_directory = os.path.dirname(package_directory)

    target_file = "src.zip"
    if os.path.exists(target_file):
        os.remove(target_file)

    with zipfile.ZipFile("src.zip", "w", compression=zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(package_directory):
            for file_name in files:
                if not file_name.endswith(tuple(machinery.SOURCE_SUFFIXES)):
                    continue
                file_path = os.path.join(root, file_name)
                pyc = compile_pyc(file_path)
                file_path_without_ext, _ = os.path.splitext(file_path)
                arcname = f"{os.path.relpath(file_path_without_ext, root_directory)}.pyc"
                z.writestr(arcname, pyc)


if __name__ == "__main__":
    main()
