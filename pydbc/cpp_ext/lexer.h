#if !defined(__LEXER_H)
#define __LEXER_H

#include "token.h"
#include "diagnostic.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <cctype>
#include <unordered_map>
#include <stdexcept>

class Lexer {
public:
    Lexer(const std::string& filename = {})
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

    Token next() {
        skipWhitespace();
        Token tk;
        tk.line = line;
        tk.column = column;
        if (pos >= text.size()) {
            tk.type = TokenType::EndOfFile;
            tk.text = "<EOF>";
            return tk;
        }
        char c = text[pos];
        if (c == '"') return readString();
        if (c=='+' || c=='-') {
            // could be sign of number or operator; peek next
            if (pos+1 < text.size() && std::isdigit((unsigned char)text[pos+1])) {
                return readNumber();
            } else {
                pos++; advanceColumn(1);
                tk.type = (c=='+')?TokenType::Plus:TokenType::Minus;
                tk.text = std::string(1,c);
                return tk;
            }
        }
        if (std::isdigit((unsigned char)c) || (c=='.' && pos+1<text.size() && std::isdigit((unsigned char)text[pos+1]))) {
            return readNumber();
        }
        if (isIdentStart(c)) return readIdentifierOrKeyword();
        // punctuation
        pos++; advanceColumn(1);
        switch (c) {
            case ':': tk.type = TokenType::Colon; tk.text = ":"; break;
            case ';': tk.type = TokenType::Semicolon; tk.text = ";"; break;
            case ',': tk.type = TokenType::Comma; tk.text = ","; break;
            case '[': tk.type = TokenType::LBracket; tk.text = "["; break;
            case ']': tk.type = TokenType::RBracket; tk.text = "]"; break;
            case '(': tk.type = TokenType::LParen; tk.text = "("; break;
            case ')': tk.type = TokenType::RParen; tk.text = ")"; break;
            case '|': tk.type = TokenType::Pipe; tk.text = "|"; break;
            case '@': tk.type = TokenType::At; tk.text = "@"; break;
            default: tk.type = TokenType::Unknown; tk.text = std::string(1,c); break;
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
    std::unordered_map<std::string, TokenType> keywords;

    void initKeywords() {
        keywords["VERSION"] = TokenType::KW_VERSION;
        keywords["BU_"] = TokenType::KW_BU;
        keywords["BO_"] = TokenType::KW_BO;
        keywords["SG_"] = TokenType::KW_SG;
        keywords["SIG_VALTYPE_"] = TokenType::KW_SIG_VALTYPE;
        keywords["BO_TX_BU_"] = TokenType::KW_BO_TX_BU;
        keywords["VAL_TABLE_"] = TokenType::KW_VAL_TABLE;
        keywords["NS_"] = TokenType::KW_NS;
        keywords["BS_"] = TokenType::KW_BS;
        keywords["EV_"] = TokenType::KW_EV;
        keywords["ENVVAR_DATA_"] = TokenType::KW_ENVVAR_DATA;
        keywords["VAL_"] = TokenType::KW_VAL;
        keywords["CM_"] = TokenType::KW_CM;
        keywords["BA_DEF_"] = TokenType::KW_BA_DEF_;
        keywords["BA_DEF_REL_"] = TokenType::KW_BA_DEF_REL_;
        keywords["BA_DEF_DEF_"] = TokenType::KW_BA_DEF_DEF_;
        keywords["BA_DEF_DEF_REL_"] = TokenType::KW_BA_DEF_DEF_REL_;
        keywords["BA_"] = TokenType::KW_BA_;
        keywords["BA_REL_"] = TokenType::KW_BA_REL_;
        keywords["SIG_GROUP_"] = TokenType::KW_SIG_GROUP;
        keywords["CAT_DEF_"] = TokenType::KW_CAT_DEF;
        keywords["CAT_"] = TokenType::KW_CAT;
        keywords["SGTYPE_"] = TokenType::KW_SGTYPE;
        keywords["INT"] = TokenType::KW_INT;
        keywords["HEX"] = TokenType::KW_HEX;
        keywords["FLOAT"] = TokenType::KW_FLOAT;
        keywords["STRING"] = TokenType::KW_STRING;
        keywords["ENUM"] = TokenType::KW_ENUM;
        keywords["SG_MUL_VAL_"] = TokenType::KW_SG_MUL_VAL;
        keywords["BU_SG_REL_"] = TokenType::KW_BU_SG_REL;
        keywords["BU_EV_REL_"] = TokenType::KW_BU_EV_REL;
        keywords["BU_BO_REL_"] = TokenType::KW_BU_BO_REL;
    }

    void skipWhitespace() {
        while (pos < text.size()) {
            char c = text[pos];
            if (c == '\r') { pos++; /* ignore */ }
            else if (c == '\n') { pos++; line++; column = 1; }
            else if (c==' '|| c=='\t') { pos++; column++; }
            else if (c == '/' && pos+1 < text.size() && text[pos+1] == '/') {
                // skip line comment
                while (pos < text.size() && text[pos] != '\n') { pos++; }
            }
            else if (c == '/' && pos+1 < text.size() && text[pos+1] == '*') {
                // skip block comment
                pos += 2; column += 2;
                while (pos < text.size()) {
                    if (text[pos] == '*' && pos+1 < text.size() && text[pos+1] == '/') {
                        pos += 2; column += 2;
                        break;
                    }
                    if (text[pos] == '\n') { line++; column = 1; }
                    else column++;
                    pos++;
                }
            }
            else break;
        }
    }

    bool isIdentStart(char c) {
        return (std::isalpha((unsigned char)c) || c=='_');
    }
    bool isIdentChar(char c) {
        return (std::isalnum((unsigned char)c) || c=='_');
    }

    Token readString() {
        Token tk;
        tk.line = line; tk.column = column;
        pos++; advanceColumn(1); // skip opening "
        std::string out;
        while (pos < text.size()) {
            char c = text[pos];
            if (c == '\\' && pos+1 < text.size()) {
                char esc = text[pos+1];
                out += c; out += esc; // keep raw escape for now
                pos += 2; advanceColumn(2);
            } else if (c == '"') {
                pos++; advanceColumn(1);
                tk.type = TokenType::String;
                tk.text = out;
                return tk;
            } else {
                if (c=='\n') { line++; column = 1; }
                else advanceColumn(1);
                out += c;
                pos++;
            }
        }
        // unterminated string
        Diagnostic d; d.severity = Diagnostic::Severity::Error; d.file = file; d.line = tk.line; d.column = tk.column;
        d.message = "Unterminated string literal";
        diags.push_back(d);
        tk.type = TokenType::String;
        tk.text = out;
        return tk;
    }

    Token readNumber() {
        Token tk;
        tk.line = line; tk.column = column;
        size_t start = pos;
        bool hasDot = false;
        if (text[pos]=='+' || text[pos]=='-') { pos++; advanceColumn(1); }
        while (pos < text.size()) {
            char c = text[pos];
            if (std::isdigit((unsigned char)c)) { pos++; advanceColumn(1); continue; }
            if (c=='.' && !hasDot) { hasDot = true; pos++; advanceColumn(1); continue; }
            // exponent
            if ((c=='e' || c=='E') && pos+1 < text.size()) {
                size_t p = pos+1;
                if (text[p]=='+'||text[p]=='-') p++;
                if (p < text.size() && std::isdigit((unsigned char)text[p])) {
                    pos++; advanceColumn(1);
                    // consume exponent digits and optional sign
                    if (text[pos]=='+'||text[pos]=='-') { pos++; advanceColumn(1); }
                    while (pos < text.size() && std::isdigit((unsigned char)text[pos])) { pos++; advanceColumn(1); }
                    continue;
                }
            }
            break;
        }
        tk.text = text.substr(start, pos-start);
        if (tk.text.find('.')!=std::string::npos || tk.text.find('e')!=std::string::npos || tk.text.find('E')!=std::string::npos)
            tk.type = TokenType::Float;
        else tk.type = TokenType::Int;
        return tk;
    }

    Token readIdentifierOrKeyword() {
        Token tk;
        tk.line = line; tk.column = column;
        size_t start = pos;
        while (pos < text.size() && isIdentChar(text[pos])) {
            pos++; advanceColumn(1);
        }
        // Special case for keywords ending with underscore like BO_
        // If we are at an underscore, it might be part of the keyword.
        // The current isIdentChar includes underscore.
        tk.text = text.substr(start, pos-start);
        
        auto it = keywords.find(tk.text);
        if (it != keywords.end()) {
            tk.type = it->second;
        } else {
            // Try to see if it's a keyword that we might have over-read
            // e.g. "BO_MyMessage" -> read "BO_MyMessage" but "BO_" is keyword.
            // In DBC, keywords like BO_ are usually followed by space or colon.
            // But let's check if the prefix is a keyword.
            // Actually, in DBC "BO_" is a keyword, and "BO_NAME" could be an identifier.
            // So we should only match "BO_" if it's exactly "BO_".
            tk.type = TokenType::Identifier;
        }
        return tk;
    }

    void advanceColumn(size_t n) { column += n; }
};

#endif // __LEXER_H
