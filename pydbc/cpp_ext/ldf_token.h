#ifndef __LDF_TOKEN_H
#define __LDF_TOKEN_H

#include <string>

enum class LdfTokenType {
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
    Percent,
    Plus,
    Minus,
    EndOfFile,
    Unknown,
    // keywords
    KW_LIN_DESCRIPTION_FILE,
    KW_LIN_PROTOCOL_VERSION,
    KW_LIN_LANGUAGE_VERSION,
    KW_LDF_FILE_REVISION,
    KW_LIN_SPEED,
    KW_CHANNEL_NAME,
    KW_NODES,
    KW_MASTER,
    KW_SLAVES,
    KW_NODE_ATTRIBUTES,
    KW_LIN_PROTOCOL,
    KW_CONFIGURED_NAD,
    KW_INITIAL_NAD,
    KW_PRODUCT_ID,
    KW_RESPONSE_ERROR,
    KW_FAULT_STATE_SIGNALS,
    KW_P2_MIN,
    KW_ST_MIN,
    KW_N_AS_TIMEOUT,
    KW_N_CR_TIMEOUT,
    KW_RESPONSE_TOLERANCE,
    KW_CONFIGURABLE_FRAMES,
    KW_COMPOSITE,
    KW_CONFIGURATION,
    KW_SIGNALS,
    KW_DIAGNOSTIC_SIGNALS,
    KW_FRAMES,
    KW_SPORADIC_FRAMES,
    KW_EVENT_TRIGGERED_FRAMES,
    KW_DIAGNOSTIC_FRAMES,
    KW_SCHEDULE_TABLES,
    KW_SIGNAL_GROUPS,
    KW_SIGNAL_ENCODING_TYPES,
    KW_SIGNAL_REPRESENTATION,
    KW_LOGICAL_VALUE,
    KW_PHYSICAL_VALUE,
    KW_BCD_VALUE,
    KW_ASCII_VALUE,
    KW_MASTER_REQ,
    KW_SLAVE_RESP,
    KW_ASSIGN_NAD,
    KW_CONDITIONAL_CHANGE_NAD,
    KW_DATA_DUMP,
    KW_SAVE_CONFIGURATION,
    KW_ASSIGN_FRAME_ID_RANGE,
    KW_FREE_FORMAT,
    KW_ASSIGN_FRAME_ID,
    KW_DELAY,
    KW_KBPS,
    KW_MS,
    KW_BITS
};

struct LdfToken {
    LdfTokenType type = LdfTokenType::Unknown;
    std::string text;
    size_t line = 1;
    size_t column = 1;
};

#endif // __LDF_TOKEN_H