
#ifndef __TOKEN_H
#define __TOKEN_H

#include <string>

enum class TokenType {
    Identifier,
    Int,
    Float,
    String,
    // punctuation
    Colon, Semicolon, Comma, LBracket, RBracket, LParen, RParen, Pipe, At,
    Plus, Minus,
    EndOfFile,
    Unknown,
    // keywords (mapped when lexing)
    KW_VERSION, KW_BU, KW_BO, KW_SG, KW_SIG_VALTYPE, KW_BO_TX_BU, KW_VAL_TABLE,
    KW_NS, KW_BS, KW_EV, KW_ENVVAR_DATA,
    KW_VAL, KW_CM, KW_BA_DEF_, KW_BA_DEF_REL_, KW_BA_DEF_DEF_, KW_BA_DEF_DEF_REL_,
    KW_BA_, KW_BA_REL_, KW_SIG_GROUP, KW_CAT_DEF, KW_CAT, KW_SGTYPE,
    KW_INT, KW_HEX, KW_FLOAT, KW_STRING, KW_ENUM, KW_SG_MUL_VAL,
    KW_BU_SG_REL, KW_BU_EV_REL, KW_BU_BO_REL
};

struct Token {
    TokenType type = TokenType::Unknown;
    std::string text;
    size_t line = 1;
    size_t column = 1;
};

#endif // __TOKEN_H
