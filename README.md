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
cmake --build build/Frozen --config Release  -- -maxCpuCount:20  # Set your cpu count at the last parameter to speed up
```

You can also use ninja as generator: (Ninja is always faster than MSBuild for some reasons.)

```bash
"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
cmake -S . -B build/Frozen -G "Ninja" -DNEED_CONSOLE=OFF -DFREEZE_APPLICATION=ON -DCMAKE_BUILD_TYPE:STRING=Release
cmake --build build/Frozen --config Release
```

All needed files will be deployed under: `frozen`

If the application doesn't work, try `-DNEED_CONSOLE=ON`, run the application with command line and get useful information from standard output.
