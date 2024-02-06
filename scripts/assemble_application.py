"""
Script for assembling application
"""

import sys
import os
import re
import types
import dataclasses
import shutil
import itertools
import importlib
from importlib import machinery, util


from PyInstaller import hooks
from PyInstaller.building import build_main

import generate_frozen_modules


@dataclasses.dataclass
class AssembleInfo:
    """
    Data struct for assemble info
    """

    entry_module_name: str  # A python module name or a signle python_file
    hidden_imports: list[str]  # hidden import module names
    excludes: list[str]  # exclude module names
    binaries: list[str]  # list all needed binaries
    datas: list[str]  # list all needed datas
    pyside6_modules: list[str]  # list all used PySide6 module
    output_directory = os.path.join(generate_frozen_modules.ROOT_DIR, "deployment")
    ignore_platform_dynload = True
    static_python = True


class PyiPySide6HookModule(types.ModuleType):
    """
    Type helper class for PyInstaller PySide6 hook modules
    """

    hiddenimports: list[str]
    binaries: list[tuple[str, str]]
    datas: list[tuple[str, str]]


def get_platform_dynload_dir() -> str:
    """
    Get platform dynamic load directory
    Returns:
        str
    """
    for path in sys.path:
        if path.endswith(("DLLs", "lib-dynload")):
            return path
    raise FileNotFoundError


def import_pyi_pyside6_hooks(fullname: str) -> PyiPySide6HookModule:
    """
    import PyInstaller PySide6 hook modules
    Args:
        name: fullname of PySide6 module
    Returns:
        PyiPySide6HookModule
    """
    hooks_dir = os.path.dirname(hooks.__file__)
    module_path = os.path.join(hooks_dir, f"hook-{fullname}.py")
    real_fullname = f"PyInstaller.hooks.{fullname}"
    loader = machinery.SourceFileLoader(real_fullname, module_path)
    spec = util.spec_from_file_location(real_fullname, module_path, loader=loader)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_pyi_toc(entry: list[str], typecode: str, level: int = 1) -> tuple[str, str, str]:
    """
    Return PyInstaller TOC with the input string list
    PyInstaller TOC: destination_path, source_path, typecode ("BINARY" / "DATA")
    """
    up_to = [".." for _ in range(level)]
    start_from = os.path.normpath(os.path.join(entry, *up_to))
    dest = os.path.relpath(entry, start_from)
    src = os.path.abspath(entry)
    return (dest, src, typecode)


def process_pyside6_files(assemble_info: AssembleInfo) -> None:
    """
    Process PySide6 files
    """
    imported_module_names = set()
    binaries = set()
    datas = set()

    def process_pyside6_import(module_names: list[str]) -> None:
        if not module_names:
            return
        todo: list[str] = []
        for module_name in module_names:
            if module_name in imported_module_names:
                continue
            hook = import_pyi_pyside6_hooks(module_name)
            todo.extend(hook.hiddenimports)
            binaries.update(hook.binaries)
            datas.update(hook.datas)
            imported_module_names.add(module_name)

            module = importlib.import_module(module_name)
            assert isinstance(module.__loader__, machinery.ExtensionFileLoader)
            module_file = module.__file__
            start_from = os.path.normpath(os.path.join(module_file, "..", ".."))
            dest = os.path.relpath(module_file, start_from)
            dest_dir = os.path.normpath(os.path.join(dest, ".."))
            binaries.add((module_file, dest_dir))
        process_pyside6_import(todo)

    process_pyside6_import(assemble_info.pyside6_modules)
    for src, dest_dir in itertools.chain(binaries, datas):
        dest_dir = os.path.join(assemble_info.output_directory, dest_dir)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        try:
            shutil.copy(src, dest_dir)
        except FileExistsError:
            # File is already there, skip it.
            pass


def assemble_application(assemble_info: AssembleInfo) -> None:
    """
    Assemble application
    """
    pyi_binaries = [normalize_pyi_toc(binary, "BINARY") for binary in assemble_info.binaries]
    analysis_info = generate_frozen_modules.ModuleAnalysisInfo(
        assemble_info.entry_module_name, assemble_info.hidden_imports, assemble_info.excludes
    )
    modules = generate_frozen_modules.analyze_module(
        analysis_info, generate_frozen_modules.ModuleType.EXTENSION_MODULE | generate_frozen_modules.ModuleType.SOURCE_MODULE
    )

    # Process extension binaries
    platform_dynload_dir = get_platform_dynload_dir()
    for module_name, module in modules.items():
        if not module.__file__.endswith(tuple(machinery.EXTENSION_SUFFIXES)):
            continue
        if module.__file__.startswith(platform_dynload_dir):
            if assemble_info.ignore_platform_dynload:
                continue
        level = module_name.count(".") + 1
        pyi_binaries.append(normalize_pyi_toc(module.__file__, "BINARY", level))

    import_packages = sorted(modules.keys())
    dependencies = build_main.find_binary_dependencies(pyi_binaries, import_packages)

    if os.path.isdir(assemble_info.output_directory):
        shutil.rmtree(assemble_info.output_directory)
    os.makedirs(assemble_info.output_directory)
    for dest, src, _ in dependencies:
        if re.match(r"py(?:thon(?:com(?:loader)?)?|wintypes)\d+\.dll", dest):
            if not src.startswith(generate_frozen_modules.ROOT_DIR) and assemble_info.static_python:
                continue
        dest = os.path.join(assemble_info.output_directory, dest)
        dirname = os.path.dirname(dest)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        shutil.copyfile(src, dest)

    process_pyside6_files(assemble_info)


def main() -> None:
    """
    Entry point
    Returns:
        None
    """
    assemble_info = AssembleInfo("", [], [], [], [], [])
    if len(sys.argv) < 2:
        generate_frozen_modules.usage("Need at least 1 argument to assemble application.")
    for arg in sys.argv[1:]:
        if arg.startswith("--hidden-imports"):
            hidden_imports = generate_frozen_modules.get_list_arg(arg, "--hidden-imports")
            assemble_info.hidden_imports = hidden_imports
        elif arg.startswith("--excludes"):
            excludes = generate_frozen_modules.get_list_arg(arg, "--excludes")
            assemble_info.excludes = excludes
        elif arg.startswith("--binaries"):
            binaries = generate_frozen_modules.get_list_arg(arg, "--binaries")
            assemble_info.binaries = binaries
        elif arg.startswith("--datas"):
            datas = generate_frozen_modules.get_list_arg(arg, "--datas")
            assemble_info.datas = datas
        elif arg.startswith("--pyside6-modules"):
            pyside6_modules = generate_frozen_modules.get_list_arg(arg, "--pyside6-modules")
            assemble_info.pyside6_modules = pyside6_modules
        elif arg.startswith("--dont-ignore-platform-dynload"):
            assemble_info.ignore_platform_dynload = False
        elif arg.startswith("--dynamic-python"):
            assemble_info.static_python = False
        else:
            assemble_info.entry_module_name = arg
    assemble_application(assemble_info)


if __name__ == "__main__":
    main()
