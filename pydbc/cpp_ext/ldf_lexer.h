#if !defined(__LDF_LEXER_H)
#define __LDF_LEXER_H

#include "ldf_token.h"
#include "diagnostic.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <cctype>
#include <unordered_map>
#include <stdexcept>

class LdfLexer {
public:
    LdfLexer(const std::string& filename = {})
        : file(filename) {
        std::ifstream in(filename);
        if (!in) {
            throw std::runtime_error("Cannot open file " + filename);
        }
        std::stringstream ss;
        ss << in.rdbuf();
        text = ss.str();
        initKeywords();
    }

    LdfToken next() {
        skipWhitespace();
        LdfToken tk;
        tk.line = line;
        tk.column = column;
        if (pos >= text.size()) {
            tk.type = LdfTokenType::EndOfFile;
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
            tk.type = (c == '+') ? LdfTokenType::Plus : LdfTokenType::Minus;
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
            case ':': tk.type = LdfTokenType::Colon; tk.text = ":"; break;
            case ';': tk.type = LdfTokenType::Semicolon; tk.text = ";"; break;
            case ',': tk.type = LdfTokenType::Comma; tk.text = ","; break;
            case '{': tk.type = LdfTokenType::LBrace; tk.text = "{"; break;
            case '}': tk.type = LdfTokenType::RBrace; tk.text = "}"; break;
            case '[': tk.type = LdfTokenType::LBracket; tk.text = "["; break;
            case ']': tk.type = LdfTokenType::RBracket; tk.text = "]"; break;
            case '(':
                tk.type = LdfTokenType::LParen;
                tk.text = "(";
                break;
            case ')':
                tk.type = LdfTokenType::RParen;
                tk.text = ")";
                break;
            case '=': tk.type = LdfTokenType::Equals; tk.text = "="; break;
            case '%': tk.type = LdfTokenType::Percent; tk.text = "%"; break;
            default: tk.type = LdfTokenType::Unknown; tk.text = std::string(1, c); break;
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
    std::unordered_map<std::string, LdfTokenType> keywords;

    void initKeywords() {
        keywords["LIN_description_file"] = LdfTokenType::KW_LIN_DESCRIPTION_FILE;
        keywords["LIN_protocol_version"] = LdfTokenType::KW_LIN_PROTOCOL_VERSION;
        keywords["LIN_language_version"] = LdfTokenType::KW_LIN_LANGUAGE_VERSION;
        keywords["LDF_file_revision"] = LdfTokenType::KW_LDF_FILE_REVISION;
        keywords["LIN_speed"] = LdfTokenType::KW_LIN_SPEED;
        keywords["Channel_name"] = LdfTokenType::KW_CHANNEL_NAME;
        keywords["Nodes"] = LdfTokenType::KW_NODES;
        keywords["Master"] = LdfTokenType::KW_MASTER;
        keywords["Slaves"] = LdfTokenType::KW_SLAVES;
        keywords["Node_attributes"] = LdfTokenType::KW_NODE_ATTRIBUTES;
        keywords["LIN_protocol"] = LdfTokenType::KW_LIN_PROTOCOL;
        keywords["configured_NAD"] = LdfTokenType::KW_CONFIGURED_NAD;
        keywords["initial_NAD"] = LdfTokenType::KW_INITIAL_NAD;
        keywords["product_id"] = LdfTokenType::KW_PRODUCT_ID;
        keywords["response_error"] = LdfTokenType::KW_RESPONSE_ERROR;
        keywords["fault_state_signals"] = LdfTokenType::KW_FAULT_STATE_SIGNALS;
        keywords["P2_min"] = LdfTokenType::KW_P2_MIN;
        keywords["ST_min"] = LdfTokenType::KW_ST_MIN;
        keywords["N_As_timeout"] = LdfTokenType::KW_N_AS_TIMEOUT;
        keywords["N_Cr_timeout"] = LdfTokenType::KW_N_CR_TIMEOUT;
        keywords["response_tolerance"] = LdfTokenType::KW_RESPONSE_TOLERANCE;
        keywords["configurable_frames"] = LdfTokenType::KW_CONFIGURABLE_FRAMES;
        keywords["composite"] = LdfTokenType::KW_COMPOSITE;
        keywords["configuration"] = LdfTokenType::KW_CONFIGURATION;
        keywords["Signals"] = LdfTokenType::KW_SIGNALS;
        keywords["Diagnostic_signals"] = LdfTokenType::KW_DIAGNOSTIC_SIGNALS;
        keywords["Frames"] = LdfTokenType::KW_FRAMES;
        keywords["Sporadic_frames"] = LdfTokenType::KW_SPORADIC_FRAMES;
        keywords["Event_triggered_frames"] = LdfTokenType::KW_EVENT_TRIGGERED_FRAMES;
        keywords["Diagnostic_frames"] = LdfTokenType::KW_DIAGNOSTIC_FRAMES;
        keywords["Schedule_tables"] = LdfTokenType::KW_SCHEDULE_TABLES;
        keywords["Signal_groups"] = LdfTokenType::KW_SIGNAL_GROUPS;
        keywords["Signal_encoding_types"] = LdfTokenType::KW_SIGNAL_ENCODING_TYPES;
        keywords["Signal_representation"] = LdfTokenType::KW_SIGNAL_REPRESENTATION;
        keywords["logical_value"] = LdfTokenType::KW_LOGICAL_VALUE;
        keywords["physical_value"] = LdfTokenType::KW_PHYSICAL_VALUE;
        keywords["bcd_value"] = LdfTokenType::KW_BCD_VALUE;
        keywords["ascii_value"] = LdfTokenType::KW_ASCII_VALUE;
        keywords["MasterReq"] = LdfTokenType::KW_MASTER_REQ;
        keywords["SlaveResp"] = LdfTokenType::KW_SLAVE_RESP;
        keywords["AssignNAD"] = LdfTokenType::KW_ASSIGN_NAD;
        keywords["ConditionalChangeNAD"] = LdfTokenType::KW_CONDITIONAL_CHANGE_NAD;
        keywords["DataDump"] = LdfTokenType::KW_DATA_DUMP;
        keywords["SaveConfiguration"] = LdfTokenType::KW_SAVE_CONFIGURATION;
        keywords["AssignFrameIdRange"] = LdfTokenType::KW_ASSIGN_FRAME_ID_RANGE;
        keywords["FreeFormat"] = LdfTokenType::KW_FREE_FORMAT;
        keywords["AssignFrameId"] = LdfTokenType::KW_ASSIGN_FRAME_ID;
        keywords["delay"] = LdfTokenType::KW_DELAY;
        keywords["kbps"] = LdfTokenType::KW_KBPS;
        keywords["ms"] = LdfTokenType::KW_MS;
        keywords["bits"] = LdfTokenType::KW_BITS;
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
    bool isIdentChar(char c) { return (std::isalnum((unsigned char)c) || c == '_'); }

    void advanceColumn(size_t count) { column += count; }

    LdfToken readString() {
        LdfToken tk;
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
                tk.type = LdfTokenType::String;
                tk.text = latin1ToUtf8(out);
                return tk;
            } else {
                if (c == '\n') { line++; column = 1; }
                else advanceColumn(1);
                out += c;
                pos++;
            }
        }
        Diagnostic d; d.severity = Diagnostic::Severity::Error; d.file = file; d.line = tk.line; d.column = tk.column;
        d.message = "Unterminated string literal";
        diags.push_back(d);
        tk.type = LdfTokenType::String;
        tk.text = latin1ToUtf8(out);
        return tk;
    }

    LdfToken readNumber() {
        LdfToken tk;
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
            tk.type = LdfTokenType::Float;
        } else {
            tk.type = LdfTokenType::Int;
        }
        return tk;
    }

    LdfToken readHexNumber() {
        LdfToken tk;
        tk.line = line; tk.column = column;
        size_t start = pos;
        pos += 2; advanceColumn(2);
        while (pos < text.size() && std::isxdigit((unsigned char)text[pos])) {
            pos++; advanceColumn(1);
        }
        tk.text = text.substr(start, pos - start);
        tk.type = LdfTokenType::Int;
        return tk;
    }

    LdfToken readIdentifierOrKeyword() {
        LdfToken tk;
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
            tk.type = LdfTokenType::Identifier;
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

#endif // __LDF_LEXER_H