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

```bash
cmake -S . -B build/Frozen -G "Visual Studio 17 2022" -DNEED_CONSOLE=OFF -DFREEZE_APPLICATION=ON -DCMAKE_BUILD_TYPE:STRING=Release
cd build/Frozen
cmake --build . --config Release
```

All needed files will be compiled under: `build/Frozen/Release`

Copy all files under that folder into another folder (let's call it folder A), except these two files：

- python_embed.exp
- python_embed.lib

Copy PySide6 and shiboken6 folder under .venv folder, to folder A.

Double click python_embed.exe under folder A, the demo PySide application will be launched.
