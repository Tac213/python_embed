#include <cstdlib>
#include <filesystem>
#include <string>
#if defined(_DEBUG)
#    undef _DEBUG // https://stackoverflow.com/questions/38860915/lnk2019-error-in-pycaffe-in-debug-mode-for-caffe-for-windows
#endif
#include <Python.h>
#if defined(_MSC_VER)
#    include <Windows.h>
#endif

#define STR_HELPER(x) #x
#define STR(x)        STR_HELPER(x)

static int
pymain_run_module(const wchar_t* modname, int set_argv0)
{
    PyObject *module, *runpy, *runmodule, *runargs, *result;
    if (PySys_Audit("cpython.run_module", "u", modname) < 0)
    {
        PyErr_Print();
        return 1;
    }
    runpy = PyImport_ImportModule("runpy");
    if (runpy == nullptr)
    {
        fprintf(stderr, "Could not import runpy module\n");
        PyErr_Print();
        return 1;
    }
    runmodule = PyObject_GetAttrString(runpy, "_run_module_as_main");
    if (runmodule == nullptr)
    {
        fprintf(stderr, "Could not access runpy._run_module_as_main\n");
        Py_DECREF(runpy);
        PyErr_Print();
        return 1;
    }
    module = PyUnicode_FromWideChar(modname, wcslen(modname));
    if (module == nullptr)
    {
        fprintf(stderr, "Could not convert module name to unicode\n");
        Py_DECREF(runpy);
        Py_DECREF(runmodule);
        PyErr_Print();
        return 1;
    }
    runargs = PyTuple_Pack(2, module, set_argv0 ? Py_True : Py_False);
    if (runargs == nullptr)
    {
        fprintf(stderr, "Could not create arguments for runpy._run_module_as_main\n");
        Py_DECREF(runpy);
        Py_DECREF(runmodule);
        Py_DECREF(module);
        PyErr_Print();
        return 1;
    }
    result = PyObject_Call(runmodule, runargs, nullptr);
    Py_DECREF(runpy);
    Py_DECREF(runmodule);
    Py_DECREF(module);
    Py_DECREF(runargs);
    if (result == nullptr)
    {
        PyErr_Print();
        return 1;
    }
    Py_DECREF(result);
    return 0;
}


#if defined(NEED_CONSOLE)
int main(int argc, char** argv)
#else
int WINAPI
WinMain(HINSTANCE hInst, HINSTANCE hPrevInst, LPSTR lpCmdLine, int nShowCmd) // NOLINT(readability-identifier-naming)
#endif
{
#if !defined(NEED_CONSOLE)
    int    argc = __argc;
    char** argv = __argv;
#endif
    PyStatus status;

    PyConfig config;
    PyConfig_InitPythonConfig(&config);

    bool is_dev = false;
#if defined(_MSC_VER)
    char*  env_p = nullptr;
    size_t sz    = 0;
    if (_dupenv_s(&env_p, &sz, "VIRTUAL_ENV") == 0 && env_p != nullptr)
#else
    if (const char* env_p = std::getenv("VIRTUAL_ENV"))
#endif
    {
        is_dev = true;

        std::string python_executable = env_p;
#if defined(_MSC_VER)
        python_executable += "\\Scripts\\python.exe";
        free(env_p);
#else
        python_executable += "/bin/python";
#endif
        status = PyConfig_SetBytesString(&config, &config.program_name, python_executable.c_str());
        if (PyStatus_Exception(status))
        {
            PyConfig_Clear(&config);
            fprintf(stderr, "%s", PyStatus_IsError(status) != 0 ? status.err_msg : "Failed to set venv python executable.");
            return 1;
        }
    }
    else
    {
        is_dev = false;

        config.module_search_paths_set = 1;

        std::filesystem::path executable_path(argv[0]);
        auto                  executable_directory = executable_path.parent_path();
        auto                  standard_lib         = executable_directory / "python" STR(PY_MAJOR_VERSION) STR(PY_MINOR_VERSION) ".zip";
        auto                  python_src           = executable_directory / "src.zip";

        status = PyWideStringList_Append(&config.module_search_paths,
                                         python_src.wstring().c_str());
        if (PyStatus_Exception(status))
        {
            PyConfig_Clear(&config);
            fprintf(stderr, "%s", PyStatus_IsError(status) != 0 ? status.err_msg : "Failed to set sys.path.");
            return 1;
        }
        status = PyWideStringList_Append(&config.module_search_paths,
                                         standard_lib.wstring().c_str());
        if (PyStatus_Exception(status))
        {
            PyConfig_Clear(&config);
            fprintf(stderr, "%s", PyStatus_IsError(status) != 0 ? status.err_msg : "Failed to set sys.path.");
            return 1;
        }
        status = PyWideStringList_Append(&config.module_search_paths,
                                         executable_directory.wstring().c_str());
        if (PyStatus_Exception(status))
        {
            PyConfig_Clear(&config);
            fprintf(stderr, "%s", PyStatus_IsError(status) != 0 ? status.err_msg : "Failed to set sys.path.");
            return 1;
        }
        config.write_bytecode = 0;
    }
    status = PyConfig_SetBytesArgv(&config, argc, const_cast<char* const*>(argv));
    if (PyStatus_Exception(status))
    {
        PyConfig_Clear(&config);
        fprintf(stderr, "%s", PyStatus_IsError(status) != 0 ? status.err_msg : "Failed to set sys.argv.");
        return 1;
    }
    status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status))
    {
        PyConfig_Clear(&config);
        fprintf(stderr, "%s", PyStatus_IsError(status) != 0 ? status.err_msg : "Failed to initialize CPython from config.");
        return 1;
    }

    PyConfig_Clear(&config);

    int exitcode = 0;

    if (is_dev)
    {
        exitcode = Py_RunMain();
    }
    else
    {
        exitcode = pymain_run_module(L"python_embed", 0);
    }

    return exitcode;
}