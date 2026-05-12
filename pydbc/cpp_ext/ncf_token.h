#ifndef __NCF_TOKEN_H
#define __NCF_TOKEN_H

#include <string>

enum class NcfTokenType {
    Identifier,
    Int,
    Float,
    String,
    // punctuation
    Colon,
    Semicolon,
    Comma,
    LBrace,
    RBrace,
    LParen,
    RParen,
    LBracket,
    RBracket,
    Equals,
    Plus,
    Minus,
    EndOfFile,
    Unknown,
    // keywords
    KW_NODE_CAPABILITY_FILE,
    KW_LIN_LANGUAGE_VERSION,
    KW_NODE,
    KW_GENERAL,
    KW_LIN_PROTOCOL_VERSION,
    KW_SUPPLIER,
    KW_FUNCTION,
    KW_VARIANT,
    KW_BITRATE,
    KW_AUTOMATIC,
    KW_MIN,
    KW_MAX,
    KW_SELECT,
    KW_KBPS,
    KW_SENDS_WAKE_UP_SIGNAL,
    KW_YES,
    KW_NO,
    KW_VOLT_RANGE,
    KW_TEMP_RANGE,
    KW_CONFORMANCE,
    KW_DIAGNOSTIC,
    KW_NAD,
    KW_TO,
    KW_DIAGNOSTIC_CLASS,
    KW_P2_MIN,
    KW_ST_MIN,
    KW_N_AS_TIMEOUT,
    KW_N_CR_TIMEOUT,
    KW_SUPPORT_SID,
    KW_MAX_MESSAGE_LENGTH,
    KW_MS,
    KW_FRAMES,
    KW_PUBLISH,
    KW_SUBSCRIBE,
    KW_LENGTH,
    KW_MIN_PERIOD,
    KW_MAX_PERIOD,
    KW_EVENT_TRIGGERED_FRAME,
    KW_SIGNALS,
    KW_SIZE,
    KW_INIT_VALUE,
    KW_OFFSET,
    KW_ENCODING,
    KW_LOGICAL_VALUE,
    KW_PHYSICAL_VALUE,
    KW_BCD_VALUE,
    KW_ASCII_VALUE,
    KW_STATUS_MANAGEMENT,
    KW_RESPONSE_ERROR,
    KW_FAULT_STATE_SIGNALS,
    KW_FREE_TEXT
};

struct NcfToken {
    NcfTokenType type = NcfTokenType::Unknown;
    std::string text;
    size_t line = 1;
    size_t column = 1;
};

#endif // __NCF_TOKEN_H
