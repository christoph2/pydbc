#ifndef __NCF_LEXER_H
#define __NCF_LEXER_H

#include "ncf_token.h"
#include "diagnostic.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <cctype>
#include <unordered_map>
#include <stdexcept>

class NcfLexer {
public:
    NcfLexer(const std::string& filename = {})
        : file(filename) {
        std::ifstream in(filename);
        if (!in) {
            throw std::runtime_error("Cannot open file " + filename);
        }
        std::stringstream ss;
        ss << in.rdbuf();
        text = ss.str();
        // Skip UTF-8 BOM if present
        if (text.size() >= 3 &&
            (unsigned char)text[0] == 0xEF &&
            (unsigned char)text[1] == 0xBB &&
            (unsigned char)text[2] == 0xBF) {
            pos = 3;
        }
        initKeywords();
    }

    NcfToken next() {
        skipWhitespace();
        NcfToken tk;
        tk.line = line;
        tk.column = column;
        if (pos >= text.size()) {
            tk.type = NcfTokenType::EndOfFile;
            tk.text = "<EOF>";
            return tk;
        }
        char c = text[pos];
        if (c == '"') return readString();
        if (c == '+' || c == '-') {
            if (pos + 1 < text.size() && std::isdigit((unsigned char)text[pos + 1])) {
                return readNumber();
            }
            pos++;
            advanceColumn(1);
            tk.type = (c == '+') ? NcfTokenType::Plus : NcfTokenType::Minus;
            tk.text = std::string(1, c);
            return tk;
        }
        if (c == '0' && pos + 1 < text.size() && (text[pos + 1] == 'x' || text[pos + 1] == 'X')) {
            return readHexNumber();
        }
        if (std::isdigit((unsigned char)c) || (c == '.' && pos + 1 < text.size() && std::isdigit((unsigned char)text[pos + 1]))) {
            return readNumber();
        }
        if (isIdentStart(c)) return readIdentifierOrKeyword();
        pos++;
        advanceColumn(1);
        switch (c) {
            case ':': tk.type = NcfTokenType::Colon;     tk.text = ":"; break;
            case ';': tk.type = NcfTokenType::Semicolon; tk.text = ";"; break;
            case ',': tk.type = NcfTokenType::Comma;     tk.text = ","; break;
            case '{': tk.type = NcfTokenType::LBrace;    tk.text = "{"; break;
            case '}': tk.type = NcfTokenType::RBrace;    tk.text = "}"; break;
            case '[': tk.type = NcfTokenType::LBracket;  tk.text = "["; break;
            case ']': tk.type = NcfTokenType::RBracket;  tk.text = "]"; break;
            case '(': tk.type = NcfTokenType::LParen;    tk.text = "("; break;
            case ')': tk.type = NcfTokenType::RParen;    tk.text = ")"; break;
            case '=': tk.type = NcfTokenType::Equals;    tk.text = "="; break;
            default:  tk.type = NcfTokenType::Unknown;   tk.text = std::string(1, c); break;
        }
        return tk;
    }

    const std::vector<Diagnostic>& diagnostics() const { return diags; }

private:
    std::string text;
    std::string file;
    size_t pos = 0;
    size_t line = 1;
    size_t column = 1;
    std::vector<Diagnostic> diags;
    std::unordered_map<std::string, NcfTokenType> keywords;

    void initKeywords() {
        keywords["node_capability_file"]  = NcfTokenType::KW_NODE_CAPABILITY_FILE;
        keywords["LIN_language_version"]  = NcfTokenType::KW_LIN_LANGUAGE_VERSION;
        keywords["node"]                  = NcfTokenType::KW_NODE;
        keywords["general"]               = NcfTokenType::KW_GENERAL;
        keywords["LIN_protocol_version"]  = NcfTokenType::KW_LIN_PROTOCOL_VERSION;
        keywords["supplier"]              = NcfTokenType::KW_SUPPLIER;
        keywords["function"]              = NcfTokenType::KW_FUNCTION;
        keywords["variant"]               = NcfTokenType::KW_VARIANT;
        keywords["bitrate"]               = NcfTokenType::KW_BITRATE;
        keywords["automatic"]             = NcfTokenType::KW_AUTOMATIC;
        keywords["min"]                   = NcfTokenType::KW_MIN;
        keywords["max"]                   = NcfTokenType::KW_MAX;
        keywords["select"]                = NcfTokenType::KW_SELECT;
        keywords["kbps"]                  = NcfTokenType::KW_KBPS;
        keywords["sends_wake_up_signal"]  = NcfTokenType::KW_SENDS_WAKE_UP_SIGNAL;
        keywords["yes"]                   = NcfTokenType::KW_YES;
        keywords["no"]                    = NcfTokenType::KW_NO;
        keywords["volt_range"]            = NcfTokenType::KW_VOLT_RANGE;
        keywords["temp_range"]            = NcfTokenType::KW_TEMP_RANGE;
        keywords["conformance"]           = NcfTokenType::KW_CONFORMANCE;
        keywords["diagnostic"]            = NcfTokenType::KW_DIAGNOSTIC;
        keywords["NAD"]                   = NcfTokenType::KW_NAD;
        keywords["to"]                    = NcfTokenType::KW_TO;
        keywords["diagnostic_class"]      = NcfTokenType::KW_DIAGNOSTIC_CLASS;
        keywords["P2_min"]                = NcfTokenType::KW_P2_MIN;
        keywords["ST_min"]                = NcfTokenType::KW_ST_MIN;
        keywords["N_As_timeout"]          = NcfTokenType::KW_N_AS_TIMEOUT;
        keywords["N_Cr_timeout"]          = NcfTokenType::KW_N_CR_TIMEOUT;
        keywords["support_sid"]           = NcfTokenType::KW_SUPPORT_SID;
        keywords["max_message_length"]    = NcfTokenType::KW_MAX_MESSAGE_LENGTH;
        keywords["ms"]                    = NcfTokenType::KW_MS;
        keywords["frames"]                = NcfTokenType::KW_FRAMES;
        keywords["publish"]               = NcfTokenType::KW_PUBLISH;
        keywords["subscribe"]             = NcfTokenType::KW_SUBSCRIBE;
        keywords["length"]                = NcfTokenType::KW_LENGTH;
        keywords["min_period"]            = NcfTokenType::KW_MIN_PERIOD;
        keywords["max_period"]            = NcfTokenType::KW_MAX_PERIOD;
        keywords["event_triggered_frame"] = NcfTokenType::KW_EVENT_TRIGGERED_FRAME;
        keywords["signals"]               = NcfTokenType::KW_SIGNALS;
        keywords["size"]                  = NcfTokenType::KW_SIZE;
        keywords["init_value"]            = NcfTokenType::KW_INIT_VALUE;
        keywords["offset"]                = NcfTokenType::KW_OFFSET;
        keywords["encoding"]              = NcfTokenType::KW_ENCODING;
        keywords["logical_value"]         = NcfTokenType::KW_LOGICAL_VALUE;
        keywords["physical_value"]        = NcfTokenType::KW_PHYSICAL_VALUE;
        keywords["bcd_value"]             = NcfTokenType::KW_BCD_VALUE;
        keywords["ascii_value"]           = NcfTokenType::KW_ASCII_VALUE;
        keywords["status_management"]     = NcfTokenType::KW_STATUS_MANAGEMENT;
        keywords["response_error"]        = NcfTokenType::KW_RESPONSE_ERROR;
        keywords["fault_state_signals"]   = NcfTokenType::KW_FAULT_STATE_SIGNALS;
        keywords["free_text"]             = NcfTokenType::KW_FREE_TEXT;
    }

    void skipWhitespace() {
        while (pos < text.size()) {
            char c = text[pos];
            if (c == '\r') { pos++; }
            else if (c == '\n') { pos++; line++; column = 1; }
            else if (c == ' ' || c == '\t') { pos++; column++; }
            else if (c == '/' && pos + 1 < text.size() && text[pos + 1] == '/') {
                while (pos < text.size() && text[pos] != '\n') { pos++; }
            } else if (c == '/' && pos + 1 < text.size() && text[pos + 1] == '*') {
                pos += 2; column += 2;
                while (pos < text.size()) {
                    if (text[pos] == '*' && pos + 1 < text.size() && text[pos + 1] == '/') {
                        pos += 2; column += 2;
                        break;
                    }
                    if (text[pos] == '\n') { line++; column = 1; }
                    else column++;
                    pos++;
                }
            } else {
                break;
            }
        }
    }

    bool isIdentStart(char c) { return (std::isalpha((unsigned char)c) || c == '_'); }
    bool isIdentChar(char c)  { return (std::isalnum((unsigned char)c) || c == '_'); }

    void advanceColumn(size_t count) { column += count; }

    NcfToken readString() {
        NcfToken tk;
        tk.line = line; tk.column = column;
        pos++; advanceColumn(1);
        std::string out;
        while (pos < text.size()) {
            char c = text[pos];
            if (c == '\\' && pos + 1 < text.size()) {
                char esc = text[pos + 1];
                out += c; out += esc;
                pos += 2; advanceColumn(2);
            } else if (c == '"') {
                pos++; advanceColumn(1);
                tk.type = NcfTokenType::String;
                tk.text = latin1ToUtf8(out);
                return tk;
            } else {
                if (c == '\n') { line++; column = 1; }
                else advanceColumn(1);
                out += c;
                pos++;
            }
        }
        Diagnostic d; d.severity = Diagnostic::Severity::Error; d.file = file;
        d.line = tk.line; d.column = tk.column;
        d.message = "Unterminated string literal";
        diags.push_back(d);
        tk.type = NcfTokenType::String;
        tk.text = latin1ToUtf8(out);
        return tk;
    }

    NcfToken readNumber() {
        NcfToken tk;
        tk.line = line; tk.column = column;
        size_t start = pos;
        bool hasDot = false;
        if (text[pos] == '+' || text[pos] == '-') { pos++; advanceColumn(1); }
        while (pos < text.size()) {
            char c = text[pos];
            if (std::isdigit((unsigned char)c)) { pos++; advanceColumn(1); continue; }
            if (c == '.' && !hasDot) { hasDot = true; pos++; advanceColumn(1); continue; }
            if ((c == 'e' || c == 'E') && pos + 1 < text.size()) {
                size_t p = pos + 1;
                if (text[p] == '+' || text[p] == '-') p++;
                if (p < text.size() && std::isdigit((unsigned char)text[p])) {
                    pos++; advanceColumn(1);
                    if (text[pos] == '+' || text[pos] == '-') { pos++; advanceColumn(1); }
                    while (pos < text.size() && std::isdigit((unsigned char)text[pos])) { pos++; advanceColumn(1); }
                    continue;
                }
            }
            break;
        }
        tk.text = text.substr(start, pos - start);
        if (tk.text.find('.') != std::string::npos || tk.text.find('e') != std::string::npos || tk.text.find('E') != std::string::npos) {
            tk.type = NcfTokenType::Float;
        } else {
            tk.type = NcfTokenType::Int;
        }
        return tk;
    }

    NcfToken readHexNumber() {
        NcfToken tk;
        tk.line = line; tk.column = column;
        size_t start = pos;
        pos += 2; advanceColumn(2);
        while (pos < text.size() && std::isxdigit((unsigned char)text[pos])) {
            pos++; advanceColumn(1);
        }
        tk.text = text.substr(start, pos - start);
        tk.type = NcfTokenType::Int;
        return tk;
    }

    NcfToken readIdentifierOrKeyword() {
        NcfToken tk;
        tk.line = line; tk.column = column;
        size_t start = pos;
        while (pos < text.size() && isIdentChar(text[pos])) {
            pos++; advanceColumn(1);
        }
        tk.text = text.substr(start, pos - start);
        auto it = keywords.find(tk.text);
        if (it != keywords.end()) {
            tk.type = it->second;
        } else {
            tk.type = NcfTokenType::Identifier;
        }
        return tk;
    }

    static std::string latin1ToUtf8(const std::string& input) {
        std::string out;
        out.reserve(input.size());
        for (unsigned char ch : input) {
            if (ch < 0x80) {
                out.push_back(static_cast<char>(ch));
            } else {
                out.push_back(static_cast<char>(0xC0 | (ch >> 6)));
                out.push_back(static_cast<char>(0x80 | (ch & 0x3F)));
            }
        }
        return out;
    }
};

#endif // __NCF_LEXER_H
