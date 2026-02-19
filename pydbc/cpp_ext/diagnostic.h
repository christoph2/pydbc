// cpp
#pragma once
#include <string>

struct Diagnostic {
    enum class Severity { Error, Warning, Info } severity;
    std::string file;
    size_t line = 0;
    size_t column = 0;
    std::string message;
};