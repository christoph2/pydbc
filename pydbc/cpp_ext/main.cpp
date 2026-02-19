// cpp
#include "dbc_parser.h"
#include <iostream>
#include <fstream>
#include <sstream>

int main(int argc, char** argv) {
    bool trace = false;
    std::string filename;
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--trace") trace = true;
        else if (filename.empty()) filename = arg;
    }

    if (filename.empty()) { std::cerr << "Usage: dbcparse [--trace] <file.dbc>\n"; return 1; }

    DbcParser parser(filename);
    parser.setTrace(trace);
    DbcFile dbc = parser.parse();
    for (auto &d: parser.getDiagnostics()) {
        std::cerr << (d.severity == Diagnostic::Severity::Error ? "Error: " : "Warning: ")
                  << (d.line?std::to_string(d.line):std::string("0")) << ":" << d.column << " - " << d.message << "\n";
    }
    std::cout << "Parsed DBC: version='" << dbc.version << "' messages=" << dbc.messages.size() << "\n";
    return 0;
}