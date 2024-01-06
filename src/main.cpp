#include <cstdlib>
#include <string>
#include <pybind11/embed.h> // everything needed for embedding

namespace py = pybind11;

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
            return status.exitcode;
        }
    }
    py::scoped_interpreter guard{&config, argc, argv}; // start the interpreter and keep it alive

    py::print("Hello, World!"); // use the Python API
    py::module_::import("test");

    return 0;
}