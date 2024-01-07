# python_embed

## 开发

```bash
# 在python_embed根目录下创建venv, 名字必须叫.venv
python -m venv .venv
# 激活venv
.venv/Scripts/activate.bat
# editable装依赖
pip3 install -e .[dev]

# 开启VS Code, Configure之后F5就行

# 下面是Visual Studio的编译示例
# 先Configure生成build/VisualStudio/python_embed.sln
cmake -S . -B build/VisualStudio -G "Visual Studio 17 2022"
# 进入build目录
cd build/VisualStudio
# 编译, 也可以打开python_embed.sln手动编译，但是运行结果会不符合预期，要参考.vscode/launch.json配下运行命令和环境变量
cmake --build .

# 保持在venv里，运行
./Debug/python_embed.exe -m python_embed
```

## 打包

看下 python 版本，下载对应版本的 win64 embeddable package，比如：https://www.python.org/ftp/python/3.11.7/python-3.11.7-embed-amd64.zip

解压这个 zip，把里面的这 4 个东西删掉：

- python.exe
- python3.dll
- python311.dll, 也有可能是 python312.dll 或者 python310.dll 之类的，根据你的 python 版本决定
- pythonw.exe

编译一个 Release 版本的 python_embed.exe(Debug 的也行)，拷贝到刚才 zip 的解压目录下。

去.venv 下面找到 PySide6 和 shiboken6 目录，拷贝到刚才 zip 的解压目录下。

激活 venv，在 python_embed 源码根目录下执行：

```bash
python scripts/generated_source_zip.py python_embed  # 第3个参数是入口模块
```

执行完成后会生成 src.zip，拷贝到刚才 zip 的解压目录下。

此时在刚才 zip 的解压目录下双击 python_embed.exe，即可正常开启应用。
