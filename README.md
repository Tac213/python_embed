# python_embed

## Development

```bash
# create virtual env, the name should be ".venv"
python -m venv .venv
# activate venv
.venv/Scripts/activate.bat
# install packages with editable project sources
pip3 install -e .[dev]

# Open current folder with VSCode
# Run `CMake: Configure` command
# Then press `F5`, the demo PySide application will be launched

# You can also build with Visual Studio
# First, configure to generate: build/VisualStudio/python_embed.sln
cmake -S . -B build/VisualStudio -G "Visual Studio 17 2022"
# Change directory to build folder
cd build/VisualStudio
# Build
cmake --build .
# You can also open python_embed.sln with Visual Studio and build inside Visual Studio
# But the result is not as expected unless you set args and envs correctly (See `.vscode/launch.json` for more information)

# Keep venv activated, execute the follow command, the demo PySide application will also be launched
./Debug/python_embed.exe -m python_embed
```

## Freezing

Check your python version，download corresponding win64 embeddable package，such as：https://www.python.org/ftp/python/3.11.7/python-3.11.7-embed-amd64.zip

Unzip the zip，delete the following files：

- python.exe
- python3.dll
- python311.dll, can also be python312.dll or python310.dll, depending on your python version
- pythonw.exe

Build a Release version of python_embed.exe(Debug is also OK), copy it to the forementioned unzip folder.

Copy PySide6 and shiboken6 folder under .venv folder, to the forementioned unzip folder.

Activate venv，execute the following command under python_embed folder:

```bash
python scripts/generated_source_zip.py python_embed  # The 3rd argument is the name of the entry python module
```

A src.zip will be generated, copy it to the forementioned unzip folder.

Double click python_embed.exe, the demo PySide application will be launched.
