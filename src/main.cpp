#include <cstdlib>
#include <stdexcept>
#include <string>
#include <Python.h>

int main(int argc, char** argv)
{
    PyStatus status;

    PyConfig config;
    PyConfig_InitPythonConfig(&config);
#if defined(_MSC_VER)
    char*  env_p = nullptr;
    size_t sz    = 0;
    if (_dupenv_s(&env_p, &sz, "VIRTUAL_ENV") == 0 && env_p != nullptr)
#else
    if (const char* env_p = std::getenv("VIRTUAL_ENV"))
#endif
    {
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
            throw std::runtime_error(PyStatus_IsError(status) != 0 ? status.err_msg : "Failed to set venv python executable.");
        }
    }
    status = PyConfig_SetBytesArgv(&config, argc, const_cast<char* const*>(argv));
    if (PyStatus_Exception(status))
    {
        PyConfig_Clear(&config);
        throw std::runtime_error(PyStatus_IsError(status) != 0 ? status.err_msg : "Failed to set sys.argv.");
    }
    status = Py_InitializeFromConfig(&config);
    if (PyStatus_Exception(status))
    {
        PyConfig_Clear(&config);
        throw std::runtime_error(PyStatus_IsError(status) != 0 ? status.err_msg : "Failed to initialize CPython from config.");
    }

    PyConfig_Clear(&config);

    int exitcode = Py_RunMain();

    return exitcode;
}