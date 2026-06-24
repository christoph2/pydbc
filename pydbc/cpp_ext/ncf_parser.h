#ifndef __NCF_PARSER_H
#define __NCF_PARSER_H

#include "ncf_lexer.h"
#include "ncf_ast.h"
#include <memory>
#include <iostream>

class NcfParser {
public:
    NcfParser(const std::string& filename = {}, const std::string& content = {})
        : lexer(filename, content), file(filename) {
        advance();
    }

    void setTrace(bool enable) { traceEnabled = enable; }

    NcfFile parse() {
        NcfFile out;
        out.filename = file;
        diagnostics.clear();
        parseNcfFile(out);
        for (auto& d : lexer.diagnostics()) diagnostics.push_back(d);
        return out;
    }

    const std::vector<Diagnostic>& getDiagnostics() const { return diagnostics; }

private:
    NcfLexer lexer;
    NcfToken cur;
    std::string file;
    std::vector<Diagnostic> diagnostics;
    bool traceEnabled = false;
    int traceIndent = 0;

    struct TraceGuard {
        NcfParser& p;
        TraceGuard(NcfParser& p, const std::string& msg) : p(p) {
            p.trace("ENTER " + msg);
            p.traceIndent++;
        }
        ~TraceGuard() {
            p.traceIndent--;
            p.trace("EXIT");
        }
    };

    void trace(const std::string& msg) {
        if (traceEnabled) {
            for (int i = 0; i < traceIndent; ++i) std::cout << "  ";
            std::cout << "[TRACE] " << msg << " at " << cur.line << ":" << cur.column << " ('" << cur.text << "')\n";
        }
    }

    void advance() { cur = lexer.next(); }

    bool match(NcfTokenType t) {
        if (cur.type == t) { advance(); return true; }
        return false;
    }

    void expect(NcfTokenType t, const std::string& what) {
        if (!match(t)) {
            error("Expected " + what + ", found '" + cur.text + "'");
        }
    }

    void error(const std::string& msg) {
        Diagnostic d;
        d.severity = Diagnostic::Severity::Error;
        d.file = file;
        d.line = cur.line;
        d.column = cur.column;
        d.message = msg;
        diagnostics.push_back(d);
    }

    bool isIntToken() const {
        return cur.type == NcfTokenType::Int;
    }

    bool isNumberToken() const {
        return cur.type == NcfTokenType::Int || cur.type == NcfTokenType::Float;
    }

    std::string parseIdentifier() {
        if (cur.type == NcfTokenType::Identifier) {
            std::string value = cur.text;
            advance();
            return value;
        }
        // Some keywords can also be used as identifiers (e.g. node names)
        std::string value = cur.text;
        error("Expected identifier, found '" + cur.text + "'");
        advance();
        return value;
    }

    std::string parseString() {
        if (cur.type == NcfTokenType::String) {
            std::string value = cur.text;
            advance();
            return value;
        }
        error("Expected string literal");
        std::string fallback = cur.text;
        advance();
        return fallback;
    }

    int parseIntValue() {
        if (cur.type == NcfTokenType::Int) {
            std::string txt = cur.text;
            advance();
            return parseIntString(txt);
        }
        error("Expected integer, found '" + cur.text + "'");
        std::string fallback = cur.text;
        advance();
        return 0;
    }

    double parseNumber() {
        if (cur.type == NcfTokenType::Int || cur.type == NcfTokenType::Float) {
            std::string txt = cur.text;
            advance();
            try { return std::stod(txt); } catch (...) { return 0.0; }
        }
        error("Expected number, found '" + cur.text + "'");
        advance();
        return 0.0;
    }

    bool isHexLiteral(const std::string& s) const {
        return s.size() > 2 && s[0] == '0' && (s[1] == 'x' || s[1] == 'X');
    }

    int parseIntString(const std::string& s) const {
        try {
            if (isHexLiteral(s)) return std::stoi(s, nullptr, 16);
            return std::stoi(s);
        } catch (...) { return 0; }
    }

    // -----------------------------------------------------------------------
    // Top-level
    // -----------------------------------------------------------------------

    void parseNcfFile(NcfFile& out) {
        TraceGuard guard(*this, "ncf_file");
        expect(NcfTokenType::KW_NODE_CAPABILITY_FILE, "node_capability_file");
        expect(NcfTokenType::Semicolon, ";");
        out.languageVersion = parseLanguageVersion();
        while (cur.type == NcfTokenType::KW_NODE) {
            out.nodes.push_back(parseNodeDefinition());
        }
        if (cur.type != NcfTokenType::EndOfFile) {
            error("Unexpected token at top level: '" + cur.text + "'");
        }
    }

    std::string parseLanguageVersion() {
        TraceGuard guard(*this, "language_version");
        expect(NcfTokenType::KW_LIN_LANGUAGE_VERSION, "LIN_language_version");
        expect(NcfTokenType::Equals, "=");
        std::string v = parseString();
        expect(NcfTokenType::Semicolon, ";");
        return v;
    }

    // -----------------------------------------------------------------------
    // Node definition
    // -----------------------------------------------------------------------

    NcfNodeDef parseNodeDefinition() {
        TraceGuard guard(*this, "node_definition");
        NcfNodeDef out;
        expect(NcfTokenType::KW_NODE, "node");
        out.name = parseNodeName();
        expect(NcfTokenType::LBrace, "{");
        out.general    = parseGeneralDef();
        out.diagnostic = parseDiagnosticDef();
        out.frames     = parseFrameDef();
        if (cur.type == NcfTokenType::KW_ENCODING) {
            out.encodings = parseEncodingDef();
        }
        out.status = parseStatusManagement();
        if (cur.type == NcfTokenType::KW_FREE_TEXT) {
            out.freeText = parseFreeText();
        }
        expect(NcfTokenType::RBrace, "}");
        return out;
    }

    std::string parseNodeName() {
        // The node name is an identifier
        if (cur.type == NcfTokenType::Identifier) {
            std::string n = cur.text;
            advance();
            return n;
        }
        // Allow keywords to also be node names (rare but possible)
        std::string n = cur.text;
        advance();
        return n;
    }

    // -----------------------------------------------------------------------
    // General definition
    // -----------------------------------------------------------------------

    NcfGeneralDef parseGeneralDef() {
        TraceGuard guard(*this, "general_definition");
        NcfGeneralDef out;
        expect(NcfTokenType::KW_GENERAL, "general");
        expect(NcfTokenType::LBrace, "{");

        expect(NcfTokenType::KW_LIN_PROTOCOL_VERSION, "LIN_protocol_version");
        expect(NcfTokenType::Equals, "=");
        out.protocolVersion = parseString();
        expect(NcfTokenType::Semicolon, ";");

        expect(NcfTokenType::KW_SUPPLIER, "supplier");
        expect(NcfTokenType::Equals, "=");
        out.supplierId = parseIntValue();
        expect(NcfTokenType::Semicolon, ";");

        expect(NcfTokenType::KW_FUNCTION, "function");
        expect(NcfTokenType::Equals, "=");
        out.functionId = parseIntValue();
        expect(NcfTokenType::Semicolon, ";");

        expect(NcfTokenType::KW_VARIANT, "variant");
        expect(NcfTokenType::Equals, "=");
        out.variantId = parseIntValue();
        expect(NcfTokenType::Semicolon, ";");

        expect(NcfTokenType::KW_BITRATE, "bitrate");
        expect(NcfTokenType::Equals, "=");
        out.bitrate = parseBitrateDefinition();
        expect(NcfTokenType::Semicolon, ";");

        if (cur.type == NcfTokenType::KW_SENDS_WAKE_UP_SIGNAL) {
            advance();
            expect(NcfTokenType::Equals, "=");
            if (cur.type == NcfTokenType::KW_YES) {
                out.sendsWakeUpSignal = true; advance();
            } else if (cur.type == NcfTokenType::KW_NO) {
                out.sendsWakeUpSignal = false; advance();
            } else if (cur.type == NcfTokenType::String) {
                // Some tools write "yes"/"no" as a quoted string
                out.sendsWakeUpSignal = (cur.text == "yes"); advance();
            } else {
                error("Expected 'yes' or 'no'");
            }
            expect(NcfTokenType::Semicolon, ";");
        }

        if (cur.type == NcfTokenType::KW_VOLT_RANGE) {
            advance();
            expect(NcfTokenType::Equals, "=");
            out.voltFrom = parseNumber();
            expect(NcfTokenType::Comma, ",");
            out.voltTo = parseNumber();
            expect(NcfTokenType::Semicolon, ";");
        }

        if (cur.type == NcfTokenType::KW_TEMP_RANGE) {
            advance();
            expect(NcfTokenType::Equals, "=");
            out.tempFrom = parseNumber();
            expect(NcfTokenType::Comma, ",");
            out.tempTo = parseNumber();
            expect(NcfTokenType::Semicolon, ";");
        }

        if (cur.type == NcfTokenType::KW_CONFORMANCE) {
            advance();
            expect(NcfTokenType::Equals, "=");
            out.conformance = parseString();
            expect(NcfTokenType::Semicolon, ";");
        }

        expect(NcfTokenType::RBrace, "}");
        return out;
    }

    NcfBitrateDefinition parseBitrateDefinition() {
        TraceGuard guard(*this, "bitrate_definition");
        NcfBitrateDefinition out;
        if (cur.type == NcfTokenType::KW_AUTOMATIC) {
            out.type = "automatic";
            advance();
            if (cur.type == NcfTokenType::KW_MIN) {
                advance();
                out.minBr = parseBitrate();
            }
            if (cur.type == NcfTokenType::KW_MAX) {
                advance();
                out.maxBr = parseBitrate();
            }
        } else if (cur.type == NcfTokenType::KW_SELECT) {
            out.type = "select";
            advance();
            expect(NcfTokenType::LBrace, "{");
            out.rates.push_back(parseBitrate());
            while (match(NcfTokenType::Comma)) {
                out.rates.push_back(parseBitrate());
            }
            expect(NcfTokenType::RBrace, "}");
        } else {
            out.type = "fixed";
            out.fixedRate = parseBitrate();
        }
        return out;
    }

    double parseBitrate() {
        double n = parseNumber();
        expect(NcfTokenType::KW_KBPS, "kbps");
        return n;
    }

    // -----------------------------------------------------------------------
    // Diagnostic definition
    // -----------------------------------------------------------------------

    NcfDiagnosticDef parseDiagnosticDef() {
        TraceGuard guard(*this, "diagnostic_definition");
        NcfDiagnosticDef out;
        expect(NcfTokenType::KW_DIAGNOSTIC, "diagnostic");
        expect(NcfTokenType::LBrace, "{");

        expect(NcfTokenType::KW_NAD, "NAD");
        expect(NcfTokenType::Equals, "=");
        out.nadLhs = parseIntValue();
        if (cur.type == NcfTokenType::KW_TO) {
            advance();
            out.nadRhs = parseIntValue();
        } else {
            while (match(NcfTokenType::Comma)) {
                out.nadList.push_back(parseIntValue());
            }
        }
        expect(NcfTokenType::Semicolon, ";");

        if (cur.type == NcfTokenType::KW_DIAGNOSTIC_CLASS) {
            advance();
            expect(NcfTokenType::Equals, "=");
            out.diagnosticClass = parseIntValue();
            expect(NcfTokenType::Semicolon, ";");
        }

        if (cur.type == NcfTokenType::KW_P2_MIN) {
            advance();
            expect(NcfTokenType::Equals, "=");
            out.p2Min = parseNumber();
            expect(NcfTokenType::KW_MS, "ms");
            expect(NcfTokenType::Semicolon, ";");
        }

        if (cur.type == NcfTokenType::KW_ST_MIN) {
            advance();
            expect(NcfTokenType::Equals, "=");
            out.stMin = parseNumber();
            expect(NcfTokenType::KW_MS, "ms");
            expect(NcfTokenType::Semicolon, ";");
        }

        if (cur.type == NcfTokenType::KW_N_AS_TIMEOUT) {
            advance();
            expect(NcfTokenType::Equals, "=");
            out.nAsTimeout = parseNumber();
            expect(NcfTokenType::KW_MS, "ms");
            expect(NcfTokenType::Semicolon, ";");
        }

        if (cur.type == NcfTokenType::KW_N_CR_TIMEOUT) {
            advance();
            expect(NcfTokenType::Equals, "=");
            out.nCrTimeout = parseNumber();
            expect(NcfTokenType::KW_MS, "ms");
            expect(NcfTokenType::Semicolon, ";");
        }

        if (cur.type == NcfTokenType::KW_SUPPORT_SID) {
            advance();
            expect(NcfTokenType::LBrace, "{");
            out.supportSids.push_back(parseIntValue());
            while (match(NcfTokenType::Comma)) {
                out.supportSids.push_back(parseIntValue());
            }
            expect(NcfTokenType::RBrace, "}");
            expect(NcfTokenType::Semicolon, ";");
        }

        if (cur.type == NcfTokenType::KW_MAX_MESSAGE_LENGTH) {
            advance();
            expect(NcfTokenType::Equals, "=");
            out.maxMessageLength = parseIntValue();
            expect(NcfTokenType::Semicolon, ";");
        }

        expect(NcfTokenType::RBrace, "}");
        return out;
    }

    // -----------------------------------------------------------------------
    // Frame definition
    // -----------------------------------------------------------------------

    std::vector<NcfSingleFrame> parseFrameDef() {
        TraceGuard guard(*this, "frame_definition");
        std::vector<NcfSingleFrame> out;
        expect(NcfTokenType::KW_FRAMES, "frames");
        expect(NcfTokenType::LBrace, "{");
        while (cur.type == NcfTokenType::KW_PUBLISH || cur.type == NcfTokenType::KW_SUBSCRIBE) {
            out.push_back(parseSingleFrame());
        }
        expect(NcfTokenType::RBrace, "}");
        return out;
    }

    NcfSingleFrame parseSingleFrame() {
        TraceGuard guard(*this, "single_frame");
        NcfSingleFrame out;
        if (cur.type == NcfTokenType::KW_PUBLISH) {
            out.kind = "publish"; advance();
        } else {
            out.kind = "subscribe"; advance();
        }
        // frame name – identifier
        out.name = cur.text; advance();
        expect(NcfTokenType::LBrace, "{");
        out.properties = parseFrameProperties();
        if (cur.type == NcfTokenType::KW_SIGNALS) {
            out.signals = parseSignalDef();
        }
        expect(NcfTokenType::RBrace, "}");
        return out;
    }

    NcfFrameProperties parseFrameProperties() {
        TraceGuard guard(*this, "frame_properties");
        NcfFrameProperties out;

        expect(NcfTokenType::KW_LENGTH, "length");
        expect(NcfTokenType::Equals, "=");
        out.length = parseIntValue();
        expect(NcfTokenType::Semicolon, ";");

        if (cur.type == NcfTokenType::KW_MIN_PERIOD) {
            advance();
            expect(NcfTokenType::Equals, "=");
            out.minPeriod = parseIntValue();
            expect(NcfTokenType::KW_MS, "ms");
            expect(NcfTokenType::Semicolon, ";");
        }

        if (cur.type == NcfTokenType::KW_MAX_PERIOD) {
            advance();
            expect(NcfTokenType::Equals, "=");
            out.maxPeriod = parseIntValue();
            expect(NcfTokenType::KW_MS, "ms");
            expect(NcfTokenType::Semicolon, ";");
        }

        if (cur.type == NcfTokenType::KW_EVENT_TRIGGERED_FRAME) {
            advance();
            expect(NcfTokenType::Equals, "=");
            out.eventTriggeredFrame = cur.text;
            advance();
            // no semicolon after event_triggered_frame in grammar
        }

        return out;
    }

    // -----------------------------------------------------------------------
    // Signal definitions
    // -----------------------------------------------------------------------

    std::vector<NcfSignalDef> parseSignalDef() {
        TraceGuard guard(*this, "signal_definition");
        std::vector<NcfSignalDef> out;
        expect(NcfTokenType::KW_SIGNALS, "signals");
        expect(NcfTokenType::LBrace, "{");
        while (cur.type == NcfTokenType::Identifier) {
            out.push_back(parseSignalEntry());
        }
        expect(NcfTokenType::RBrace, "}");
        return out;
    }

    NcfSignalDef parseSignalEntry() {
        TraceGuard guard(*this, "signal_entry");
        NcfSignalDef out;
        out.name = cur.text; advance();
        expect(NcfTokenType::LBrace, "{");
        out.properties = parseSignalProperties();
        expect(NcfTokenType::RBrace, "}");
        return out;
    }

    NcfSignalProperties parseSignalProperties() {
        TraceGuard guard(*this, "signal_properties");
        NcfSignalProperties out;
        // Properties can appear in any order (grammar says init_value first, then size,
        // then offset, then optional encoding name, but be lenient)
        bool gotInit = false, gotSize = false, gotOffset = false;
        while (cur.type != NcfTokenType::RBrace && cur.type != NcfTokenType::EndOfFile) {
            if (cur.type == NcfTokenType::KW_INIT_VALUE && !gotInit) {
                advance();
                expect(NcfTokenType::Equals, "=");
                if (cur.type == NcfTokenType::LBrace) {
                    out.initValue = parseInitValueArray();
                } else {
                    out.initValue = parseInitValueScalar();
                }
                expect(NcfTokenType::Semicolon, ";");
                gotInit = true;
            } else if (cur.type == NcfTokenType::KW_SIZE && !gotSize) {
                advance();
                expect(NcfTokenType::Equals, "=");
                out.size = parseIntValue();
                expect(NcfTokenType::Semicolon, ";");
                gotSize = true;
            } else if (cur.type == NcfTokenType::KW_OFFSET && !gotOffset) {
                advance();
                expect(NcfTokenType::Equals, "=");
                out.offset = parseIntValue();
                expect(NcfTokenType::Semicolon, ";");
                gotOffset = true;
            } else if (cur.type == NcfTokenType::Identifier) {
                // encoding name (bare identifier followed by ';')
                out.encodingName = cur.text;
                advance();
                expect(NcfTokenType::Semicolon, ";");
                break;
            } else {
                break;
            }
        }
        return out;
    }

    NcfInitValue parseInitValueScalar() {
        NcfInitValue out;
        out.isArray = false;
        out.scalar = parseIntValue();
        return out;
    }

    NcfInitValue parseInitValueArray() {
        NcfInitValue out;
        out.isArray = true;
        expect(NcfTokenType::LBrace, "{");
        out.arrayValues.push_back(parseIntValue());
        while (match(NcfTokenType::Comma)) {
            out.arrayValues.push_back(parseIntValue());
        }
        expect(NcfTokenType::RBrace, "}");
        return out;
    }

    // -----------------------------------------------------------------------
    // Encoding definition
    // -----------------------------------------------------------------------

    std::vector<NcfEncodingEntry> parseEncodingDef() {
        TraceGuard guard(*this, "encoding_definition");
        std::vector<NcfEncodingEntry> out;
        expect(NcfTokenType::KW_ENCODING, "encoding");
        expect(NcfTokenType::LBrace, "{");
        while (cur.type == NcfTokenType::Identifier) {
            out.push_back(parseEncodingEntry());
        }
        expect(NcfTokenType::RBrace, "}");
        return out;
    }

    NcfEncodingEntry parseEncodingEntry() {
        TraceGuard guard(*this, "encoding_entry");
        NcfEncodingEntry out;
        out.name = cur.text; advance();
        expect(NcfTokenType::LBrace, "{");
        while (cur.type == NcfTokenType::KW_LOGICAL_VALUE ||
               cur.type == NcfTokenType::KW_PHYSICAL_VALUE ||
               cur.type == NcfTokenType::KW_BCD_VALUE ||
               cur.type == NcfTokenType::KW_ASCII_VALUE) {
            out.values.push_back(parseEncodingValue());
        }
        expect(NcfTokenType::RBrace, "}");
        return out;
    }

    NcfEncodingValue parseEncodingValue() {
        TraceGuard guard(*this, "encoding_value");
        NcfEncodingValue out;
        if (cur.type == NcfTokenType::KW_LOGICAL_VALUE) {
            out.type = "logical";
            advance();
            expect(NcfTokenType::Comma, ",");
            NcfLogicalValue lv;
            lv.signalValue = parseIntValue();
            if (match(NcfTokenType::Comma)) {
                lv.textInfo = parseString();
            }
            expect(NcfTokenType::Semicolon, ";");
            out.logicalValue = lv;
        } else if (cur.type == NcfTokenType::KW_PHYSICAL_VALUE) {
            out.type = "physical";
            advance();
            expect(NcfTokenType::Comma, ",");
            NcfPhysicalRange pr;
            pr.minValue = parseIntValue();
            expect(NcfTokenType::Comma, ",");
            pr.maxValue = parseIntValue();
            expect(NcfTokenType::Comma, ",");
            pr.scale = parseNumber();
            expect(NcfTokenType::Comma, ",");
            pr.offsetVal = parseNumber();
            if (match(NcfTokenType::Comma)) {
                pr.textInfo = parseString();
            }
            expect(NcfTokenType::Semicolon, ";");
            out.physicalRange = pr;
        } else if (cur.type == NcfTokenType::KW_BCD_VALUE) {
            out.type = "bcd";
            advance();
            expect(NcfTokenType::Semicolon, ";");
        } else if (cur.type == NcfTokenType::KW_ASCII_VALUE) {
            out.type = "ascii";
            advance();
            expect(NcfTokenType::Semicolon, ";");
        } else {
            error("Unexpected encoding value token: '" + cur.text + "'");
            advance();
        }
        return out;
    }

    // -----------------------------------------------------------------------
    // Status management
    // -----------------------------------------------------------------------

    NcfStatusManagement parseStatusManagement() {
        TraceGuard guard(*this, "status_management");
        NcfStatusManagement out;
        expect(NcfTokenType::KW_STATUS_MANAGEMENT, "status_management");
        expect(NcfTokenType::LBrace, "{");

        expect(NcfTokenType::KW_RESPONSE_ERROR, "response_error");
        expect(NcfTokenType::Equals, "=");
        out.responseError = cur.text; advance();
        expect(NcfTokenType::Semicolon, ";");

        if (cur.type == NcfTokenType::KW_FAULT_STATE_SIGNALS) {
            advance();
            expect(NcfTokenType::Equals, "=");
            out.faultStateSignals.push_back(cur.text); advance();
            while (match(NcfTokenType::Comma)) {
                out.faultStateSignals.push_back(cur.text); advance();
            }
            expect(NcfTokenType::Semicolon, ";");
        }

        expect(NcfTokenType::RBrace, "}");
        return out;
    }

    // -----------------------------------------------------------------------
    // Free text
    // -----------------------------------------------------------------------

    std::string parseFreeText() {
        TraceGuard guard(*this, "free_text");
        expect(NcfTokenType::KW_FREE_TEXT, "free_text");
        expect(NcfTokenType::LBrace, "{");
        std::string t = parseString();
        expect(NcfTokenType::RBrace, "}");
        return t;
    }
};

#endif // __NCF_PARSER_H
