#if !defined(__LDF_PARSER_H)
#define __LDF_PARSER_H

#include "ldf_lexer.h"
#include "ldf_ast.h"
#include <memory>
#include <unordered_set>
#include <iostream>
#include <fstream>

class LdfParser {
public:
    LdfParser(const std::string& filename = {})
        : lexer(filename), file(filename) {
        advance();
    }

    void setTrace(bool enable) { traceEnabled = enable; }

    LdfFile parse() {
        LdfFile out;
        out.filename = file;
        diagnostics.clear();
        parseLinDescriptionFile(out);
        for (auto& d : lexer.diagnostics()) diagnostics.push_back(d);
        return out;
    }

    const std::vector<Diagnostic>& getDiagnostics() const { return diagnostics; }

private:
    LdfLexer lexer;
    LdfToken cur;
    std::string file;
    std::vector<Diagnostic> diagnostics;
    bool traceEnabled = false;
    int traceIndent = 0;

    struct TraceGuard {
        LdfParser& p;
        TraceGuard(LdfParser& p, const std::string& msg) : p(p) {
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

    bool match(LdfTokenType t) {
        if (cur.type == t) { advance(); return true; }
        return false;
    }

    void expect(LdfTokenType t, const std::string& what) {
        if (!match(t)) {
            error("Expected " + what + ", found " + cur.text);
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

    bool isNumberToken() const {
        return cur.type == LdfTokenType::Int || cur.type == LdfTokenType::Float;
    }

    std::string parseIdentifier() {
        if (cur.type == LdfTokenType::Identifier) {
            std::string value = cur.text;
            advance();
            return value;
        }
        error("Expected identifier");
        std::string fallback = cur.text;
        advance();
        return fallback;
    }

    std::string parseString() {
        if (cur.type == LdfTokenType::String) {
            std::string value = cur.text;
            advance();
            return value;
        }
        error("Expected string");
        std::string fallback = cur.text;
        advance();
        return fallback;
    }

    int parseIntValue() {
        if (cur.type == LdfTokenType::Int) {
            std::string txt = cur.text;
            advance();
            return parseIntString(txt);
        }
        if (cur.type == LdfTokenType::Identifier && isHexLiteral(cur.text)) {
            std::string txt = cur.text;
            advance();
            return parseIntString(txt);
        }
        error("Expected integer");
        std::string fallback = cur.text;
        advance();
        return parseIntString(fallback);
    }

    double parseNumber() {
        if (cur.type == LdfTokenType::Int || cur.type == LdfTokenType::Float) {
            std::string txt = cur.text;
            advance();
            return std::stod(txt);
        }
        if (cur.type == LdfTokenType::Identifier && isHexLiteral(cur.text)) {
            std::string txt = cur.text;
            advance();
            return static_cast<double>(parseIntString(txt));
        }
        error("Expected number");
        std::string fallback = cur.text;
        advance();
        return 0.0;
    }

    bool isHexLiteral(const std::string& text) const {
        return text.size() > 2 && text[0] == '0' && (text[1] == 'x' || text[1] == 'X');
    }

    int parseIntString(const std::string& text) const {
        if (isHexLiteral(text)) {
            return std::stoi(text, nullptr, 16);
        }
        return std::stoi(text);
    }

    void parseLinDescriptionFile(LdfFile& out) {
        TraceGuard guard(*this, "lin_description_file");
        expect(LdfTokenType::KW_LIN_DESCRIPTION_FILE, "LIN_description_file");
        expect(LdfTokenType::Semicolon, ";");
        out.protocolVersion = parseProtocolVersion();
        out.languageVersion = parseLanguageVersion();
        if (cur.type == LdfTokenType::KW_LDF_FILE_REVISION) {
            out.fileRevision = parseFileRevision();
        }
        out.speed = parseSpeed();
        if (cur.type == LdfTokenType::KW_CHANNEL_NAME) {
            out.channelName = parseChannelName();
        }
        out.nodes = parseNodes();
        if (cur.type == LdfTokenType::KW_COMPOSITE) {
            out.nodeComposition = parseNodeComposition();
        }
        out.signals = parseSignals();
        if (cur.type == LdfTokenType::KW_DIAGNOSTIC_SIGNALS) {
            out.diagnosticSignals = parseDiagnosticSignals();
        }
        out.frames = parseFrames();
        if (cur.type == LdfTokenType::KW_SPORADIC_FRAMES) {
            out.sporadicFrames = parseSporadicFrames();
        }
        if (cur.type == LdfTokenType::KW_EVENT_TRIGGERED_FRAMES) {
            out.eventTriggeredFrames = parseEventTriggeredFrames();
        }
        if (cur.type == LdfTokenType::KW_DIAGNOSTIC_FRAMES) {
            out.diagnosticFrames = parseDiagnosticFrames();
        }
        out.nodeAttributes = parseNodeAttributes();
        out.scheduleTables = parseScheduleTables();
        if (cur.type == LdfTokenType::KW_SIGNAL_GROUPS) {
            out.signalGroups = parseSignalGroups();
        }
        if (cur.type == LdfTokenType::KW_SIGNAL_ENCODING_TYPES) {
            out.signalEncodingTypes = parseSignalEncodingTypes();
        }
        if (cur.type == LdfTokenType::KW_SIGNAL_REPRESENTATION) {
            out.signalRepresentations = parseSignalRepresentations();
        }
    }

    std::string parseProtocolVersion() {
        TraceGuard guard(*this, "lin_protocol_version_def");
        expect(LdfTokenType::KW_LIN_PROTOCOL_VERSION, "LIN_protocol_version");
        expect(LdfTokenType::Equals, "=");
        std::string value = parseString();
        expect(LdfTokenType::Semicolon, ";");
        return value;
    }

    std::string parseLanguageVersion() {
        TraceGuard guard(*this, "lin_language_version_def");
        expect(LdfTokenType::KW_LIN_LANGUAGE_VERSION, "LIN_language_version");
        expect(LdfTokenType::Equals, "=");
        std::string value = parseString();
        expect(LdfTokenType::Semicolon, ";");
        return value;
    }

    std::string parseFileRevision() {
        TraceGuard guard(*this, "lin_file_revision_def");
        expect(LdfTokenType::KW_LDF_FILE_REVISION, "LDF_file_revision");
        expect(LdfTokenType::Equals, "=");
        std::string value = parseString();
        expect(LdfTokenType::Semicolon, ";");
        return value;
    }

    double parseSpeed() {
        TraceGuard guard(*this, "lin_speed_def");
        expect(LdfTokenType::KW_LIN_SPEED, "LIN_speed");
        expect(LdfTokenType::Equals, "=");
        double speed = parseNumber();
        expect(LdfTokenType::KW_KBPS, "kbps");
        expect(LdfTokenType::Semicolon, ";");
        return speed;
    }

    std::string parseChannelName() {
        TraceGuard guard(*this, "channel_name_def");
        expect(LdfTokenType::KW_CHANNEL_NAME, "Channel_name");
        expect(LdfTokenType::Equals, "=");
        std::string value = parseIdentifier();
        expect(LdfTokenType::Semicolon, ";");
        return value;
    }

    LdfNodeDefinition parseNodes() {
        TraceGuard guard(*this, "node_def");
        LdfNodeDefinition out;
        expect(LdfTokenType::KW_NODES, "Nodes");
        expect(LdfTokenType::LBrace, "{");
        expect(LdfTokenType::KW_MASTER, "Master");
        expect(LdfTokenType::Colon, ":");
        out.master = parseIdentifier();
        expect(LdfTokenType::Comma, ",");
        out.timeBase = parseNumber();
        expect(LdfTokenType::KW_MS, "ms");
        expect(LdfTokenType::Comma, ",");
        out.jitter = parseNumber();
        expect(LdfTokenType::KW_MS, "ms");
        if (match(LdfTokenType::Comma)) {
            out.bitLength = parseNumber();
            expect(LdfTokenType::KW_BITS, "bits");
            expect(LdfTokenType::Comma, ",");
            out.tolerant = parseNumber();
            expect(LdfTokenType::Percent, "%");
        }
        expect(LdfTokenType::Semicolon, ";");
        expect(LdfTokenType::KW_SLAVES, "Slaves");
        expect(LdfTokenType::Colon, ":");
        out.slaves.push_back(parseIdentifier());
        while (match(LdfTokenType::Comma)) {
            out.slaves.push_back(parseIdentifier());
        }
        expect(LdfTokenType::Semicolon, ";");
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfNodeComposition parseNodeComposition() {
        TraceGuard guard(*this, "node_composition_def");
        LdfNodeComposition out;
        expect(LdfTokenType::KW_COMPOSITE, "composite");
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::KW_CONFIGURATION) {
            out.configurations.push_back(parseConfiguration());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfConfiguration parseConfiguration() {
        TraceGuard guard(*this, "configuration");
        LdfConfiguration out;
        expect(LdfTokenType::KW_CONFIGURATION, "configuration");
        out.name = parseIdentifier();
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.items.push_back(parseConfigurationItem());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfConfigurationItem parseConfigurationItem() {
        TraceGuard guard(*this, "configuration_item");
        LdfConfigurationItem out;
        out.compositeNode = parseIdentifier();
        expect(LdfTokenType::LBrace, "{");
        out.logicalNodes.push_back(parseIdentifier());
        while (match(LdfTokenType::Comma)) {
            out.logicalNodes.push_back(parseIdentifier());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    std::vector<LdfSignal> parseSignals() {
        TraceGuard guard(*this, "signal_def");
        std::vector<LdfSignal> out;
        expect(LdfTokenType::KW_SIGNALS, "Signals");
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.push_back(parseSignalItem());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfSignal parseSignalItem() {
        TraceGuard guard(*this, "signal_item");
        LdfSignal out;
        out.name = parseIdentifier();
        expect(LdfTokenType::Colon, ":");
        out.size = parseIntValue();
        expect(LdfTokenType::Comma, ",");
        out.initValue = parseInitValue();
        expect(LdfTokenType::Comma, ",");
        out.publishedBy = parseIdentifier();
        while (match(LdfTokenType::Comma)) {
            out.subscribedBy.push_back(parseIdentifier());
        }
        expect(LdfTokenType::Semicolon, ";");
        return out;
    }

    LdfInitValue parseInitValue() {
        TraceGuard guard(*this, "init_value");
        if (cur.type == LdfTokenType::LBrace) {
            return parseInitValueArray();
        }
        return parseInitValueScalar();
    }

    LdfInitValue parseInitValueScalar() {
        TraceGuard guard(*this, "init_value_scalar");
        LdfInitValue out;
        out.isArray = false;
        out.scalar = parseIntValue();
        return out;
    }

    LdfInitValue parseInitValueArray() {
        TraceGuard guard(*this, "init_value_array");
        LdfInitValue out;
        out.isArray = true;
        expect(LdfTokenType::LBrace, "{");
        out.arrayValues.push_back(parseIntValue());
        while (match(LdfTokenType::Comma)) {
            out.arrayValues.push_back(parseIntValue());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    std::vector<LdfDiagnosticSignal> parseDiagnosticSignals() {
        TraceGuard guard(*this, "diagnostic_signal_def");
        std::vector<LdfDiagnosticSignal> out;
        expect(LdfTokenType::KW_DIAGNOSTIC_SIGNALS, "Diagnostic_signals");
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.push_back(parseDiagnosticItem());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfDiagnosticSignal parseDiagnosticItem() {
        TraceGuard guard(*this, "diagnostic_item");
        LdfDiagnosticSignal out;
        out.name = parseIdentifier();
        expect(LdfTokenType::Colon, ":");
        out.size = parseIntValue();
        expect(LdfTokenType::Comma, ",");
        out.initValue = parseInitValue();
        expect(LdfTokenType::Semicolon, ";");
        return out;
    }

    std::vector<LdfSignalGroup> parseSignalGroups() {
        TraceGuard guard(*this, "signal_groups_def");
        std::vector<LdfSignalGroup> out;
        expect(LdfTokenType::KW_SIGNAL_GROUPS, "Signal_groups");
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.push_back(parseSignalGroup());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfSignalGroup parseSignalGroup() {
        TraceGuard guard(*this, "signal_group");
        LdfSignalGroup out;
        out.name = parseIdentifier();
        expect(LdfTokenType::Colon, ":");
        out.groupSize = parseIntValue();
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.items.push_back(parseSignalGroupItem());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfSignalGroupItem parseSignalGroupItem() {
        TraceGuard guard(*this, "signal_group_item");
        LdfSignalGroupItem out;
        out.signalName = parseIdentifier();
        expect(LdfTokenType::Comma, ",");
        out.groupOffset = parseIntValue();
        expect(LdfTokenType::Semicolon, ";");
        return out;
    }

    std::vector<LdfFrame> parseFrames() {
        TraceGuard guard(*this, "frame_def");
        std::vector<LdfFrame> out;
        expect(LdfTokenType::KW_FRAMES, "Frames");
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.push_back(parseFrameItem());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfFrame parseFrameItem() {
        TraceGuard guard(*this, "frame_item");
        LdfFrame out;
        out.name = parseIdentifier();
        expect(LdfTokenType::Colon, ":");
        out.frameId = parseIntValue();
        expect(LdfTokenType::Comma, ",");
        out.publishedBy = parseIdentifier();
        expect(LdfTokenType::Comma, ",");
        out.frameSize = parseIntValue();
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.signals.push_back(parseFrameSignal());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfFrameSignal parseFrameSignal() {
        TraceGuard guard(*this, "frame_signal");
        LdfFrameSignal out;
        out.signalName = parseIdentifier();
        expect(LdfTokenType::Comma, ",");
        out.signalOffset = parseIntValue();
        expect(LdfTokenType::Semicolon, ";");
        return out;
    }

    std::vector<LdfSporadicFrame> parseSporadicFrames() {
        TraceGuard guard(*this, "sporadic_frame_def");
        std::vector<LdfSporadicFrame> out;
        expect(LdfTokenType::KW_SPORADIC_FRAMES, "Sporadic_frames");
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.push_back(parseSporadicFrameItem());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfSporadicFrame parseSporadicFrameItem() {
        TraceGuard guard(*this, "sporadic_frame_item");
        LdfSporadicFrame out;
        out.name = parseIdentifier();
        expect(LdfTokenType::Colon, ":");
        out.frameNames.push_back(parseIdentifier());
        while (match(LdfTokenType::Comma)) {
            out.frameNames.push_back(parseIdentifier());
        }
        expect(LdfTokenType::Semicolon, ";");
        return out;
    }

    std::vector<LdfEventTriggeredFrame> parseEventTriggeredFrames() {
        TraceGuard guard(*this, "event_triggered_frame_def");
        std::vector<LdfEventTriggeredFrame> out;
        expect(LdfTokenType::KW_EVENT_TRIGGERED_FRAMES, "Event_triggered_frames");
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.push_back(parseEventTriggeredFrameItem());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfEventTriggeredFrame parseEventTriggeredFrameItem() {
        TraceGuard guard(*this, "event_triggered_frame_item");
        LdfEventTriggeredFrame out;
        out.name = parseIdentifier();
        expect(LdfTokenType::Colon, ":");
        out.scheduleTable = parseIdentifier();
        expect(LdfTokenType::Comma, ",");
        out.frameId = parseIntValue();
        while (match(LdfTokenType::Comma)) {
            out.frameNames.push_back(parseIdentifier());
        }
        expect(LdfTokenType::Semicolon, ";");
        return out;
    }

    std::vector<LdfDiagnosticFrame> parseDiagnosticFrames() {
        TraceGuard guard(*this, "diag_frame_def");
        std::vector<LdfDiagnosticFrame> out;
        expect(LdfTokenType::KW_DIAGNOSTIC_FRAMES, "Diagnostic_frames");
        expect(LdfTokenType::LBrace, "{");
        out.push_back(parseDiagnosticFrame());
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfDiagnosticFrame parseDiagnosticFrame() {
        TraceGuard guard(*this, "diag_frame");
        LdfDiagnosticFrame out;
        expect(LdfTokenType::KW_MASTER_REQ, "MasterReq");
        expect(LdfTokenType::Colon, ":");
        out.masterId = parseIntValue();
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.masterSignals.push_back(parseDiagnosticFrameItem());
        }
        expect(LdfTokenType::RBrace, "}");
        expect(LdfTokenType::KW_SLAVE_RESP, "SlaveResp");
        expect(LdfTokenType::Colon, ":");
        out.slaveId = parseIntValue();
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.slaveSignals.push_back(parseDiagnosticFrameItem());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfDiagnosticFrameSignal parseDiagnosticFrameItem() {
        TraceGuard guard(*this, "diag_frame_item");
        LdfDiagnosticFrameSignal out;
        out.signalName = parseIdentifier();
        expect(LdfTokenType::Comma, ",");
        out.signalOffset = parseIntValue();
        expect(LdfTokenType::Semicolon, ";");
        return out;
    }

    std::vector<LdfNodeAttribute> parseNodeAttributes() {
        TraceGuard guard(*this, "node_attributes_def");
        std::vector<LdfNodeAttribute> out;
        expect(LdfTokenType::KW_NODE_ATTRIBUTES, "Node_attributes");
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.push_back(parseNodeAttribute());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfNodeAttribute parseNodeAttribute() {
        TraceGuard guard(*this, "node_attribute");
        LdfNodeAttribute out;
        out.name = parseIdentifier();
        expect(LdfTokenType::LBrace, "{");
        expect(LdfTokenType::KW_LIN_PROTOCOL, "LIN_protocol");
        expect(LdfTokenType::Equals, "=");
        out.version = parseString();
        expect(LdfTokenType::Semicolon, ";");
        expect(LdfTokenType::KW_CONFIGURED_NAD, "configured_NAD");
        expect(LdfTokenType::Equals, "=");
        out.configuredNad = parseIntValue();
        expect(LdfTokenType::Semicolon, ";");
        if (cur.type == LdfTokenType::KW_INITIAL_NAD) {
            advance();
            expect(LdfTokenType::Equals, "=");
            out.initialNad = parseIntValue();
            expect(LdfTokenType::Semicolon, ";");
        }
        parseAttributesDef(out);
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    void parseAttributesDef(LdfNodeAttribute& out) {
        TraceGuard guard(*this, "attributes_def");
        expect(LdfTokenType::KW_PRODUCT_ID, "product_id");
        expect(LdfTokenType::Equals, "=");
        out.productId.supplierId = parseIntValue();
        expect(LdfTokenType::Comma, ",");
        out.productId.functionId = parseIntValue();
        if (match(LdfTokenType::Comma)) {
            out.productId.variant = parseIntValue();
        }
        expect(LdfTokenType::Semicolon, ";");
        expect(LdfTokenType::KW_RESPONSE_ERROR, "response_error");
        expect(LdfTokenType::Equals, "=");
        out.responseErrorSignal = parseIdentifier();
        expect(LdfTokenType::Semicolon, ";");
        if (cur.type == LdfTokenType::KW_FAULT_STATE_SIGNALS) {
            advance();
            expect(LdfTokenType::Equals, "=");
            out.faultStateSignals.push_back(parseIdentifier());
            while (match(LdfTokenType::Comma)) {
                out.faultStateSignals.push_back(parseIdentifier());
            }
            expect(LdfTokenType::Semicolon, ";");
        }
        if (cur.type == LdfTokenType::KW_P2_MIN) {
            advance();
            expect(LdfTokenType::Equals, "=");
            out.p2Min = parseNumber();
            expect(LdfTokenType::KW_MS, "ms");
            expect(LdfTokenType::Semicolon, ";");
        }
        if (cur.type == LdfTokenType::KW_ST_MIN) {
            advance();
            expect(LdfTokenType::Equals, "=");
            out.stMin = parseNumber();
            expect(LdfTokenType::KW_MS, "ms");
            expect(LdfTokenType::Semicolon, ";");
        }
        if (cur.type == LdfTokenType::KW_N_AS_TIMEOUT) {
            advance();
            expect(LdfTokenType::Equals, "=");
            out.nAsTimeout = parseNumber();
            expect(LdfTokenType::KW_MS, "ms");
            expect(LdfTokenType::Semicolon, ";");
        }
        if (cur.type == LdfTokenType::KW_N_CR_TIMEOUT) {
            advance();
            expect(LdfTokenType::Equals, "=");
            out.nCrTimeout = parseNumber();
            expect(LdfTokenType::KW_MS, "ms");
            expect(LdfTokenType::Semicolon, ";");
        }
        if (cur.type == LdfTokenType::KW_CONFIGURABLE_FRAMES) {
            out.configurableFrames = parseConfigurableFrames();
        }
        if (cur.type == LdfTokenType::KW_RESPONSE_TOLERANCE) {
            advance();
            expect(LdfTokenType::Equals, "=");
            out.responseTolerance = parseNumber();
            expect(LdfTokenType::Percent, "%");
            expect(LdfTokenType::Semicolon, ";");
        }
    }

    std::vector<LdfConfigurableFrame> parseConfigurableFrames() {
        TraceGuard guard(*this, "configurable_frames");
        std::vector<LdfConfigurableFrame> out;
        expect(LdfTokenType::KW_CONFIGURABLE_FRAMES, "configurable_frames");
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.push_back(parseConfigurableFrame());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfConfigurableFrame parseConfigurableFrame() {
        TraceGuard guard(*this, "configurable_frame");
        LdfConfigurableFrame out;
        out.frameName = parseIdentifier();
        if (match(LdfTokenType::Equals)) {
            out.messageId = parseIntValue();
        }
        expect(LdfTokenType::Semicolon, ";");
        return out;
    }

    std::vector<LdfScheduleTable> parseScheduleTables() {
        TraceGuard guard(*this, "schedule_table_def");
        std::vector<LdfScheduleTable> out;
        expect(LdfTokenType::KW_SCHEDULE_TABLES, "Schedule_tables");
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.push_back(parseScheduleTable());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfScheduleTable parseScheduleTable() {
        TraceGuard guard(*this, "schedule_table_entry");
        LdfScheduleTable out;
        out.name = parseIdentifier();
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier || cur.type == LdfTokenType::KW_MASTER_REQ || cur.type == LdfTokenType::KW_SLAVE_RESP || cur.type == LdfTokenType::KW_ASSIGN_NAD || cur.type == LdfTokenType::KW_CONDITIONAL_CHANGE_NAD || cur.type == LdfTokenType::KW_DATA_DUMP || cur.type == LdfTokenType::KW_SAVE_CONFIGURATION || cur.type == LdfTokenType::KW_ASSIGN_FRAME_ID_RANGE || cur.type == LdfTokenType::KW_FREE_FORMAT || cur.type == LdfTokenType::KW_ASSIGN_FRAME_ID) {
            out.commands.push_back(parseScheduleCommand());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfScheduleTableCommand parseScheduleCommand() {
        TraceGuard guard(*this, "schedule_table_command");
        LdfScheduleTableCommand out;
        out = parseCommand();
        expect(LdfTokenType::KW_DELAY, "delay");
        out.frameTime = parseNumber();
        expect(LdfTokenType::KW_MS, "ms");
        expect(LdfTokenType::Semicolon, ";");
        return out;
    }

    LdfScheduleTableCommand parseCommand() {
        TraceGuard guard(*this, "command");
        LdfScheduleTableCommand out;
        if (cur.type == LdfTokenType::Identifier) {
            out.type = "Frame";
            out.frameName = parseIdentifier();
            return out;
        }
        switch (cur.type) {
            case LdfTokenType::KW_MASTER_REQ:
                out.type = "MasterReq";
                advance();
                return out;
            case LdfTokenType::KW_SLAVE_RESP:
                out.type = "SlaveResp";
                advance();
                return out;
            case LdfTokenType::KW_ASSIGN_NAD:
                out.type = "AssignNAD";
                advance();
                expect(LdfTokenType::LBrace, "{");
                out.nodeName = parseIdentifier();
                expect(LdfTokenType::RBrace, "}");
                return out;
            case LdfTokenType::KW_CONDITIONAL_CHANGE_NAD:
                out.type = "ConditionalChangeNAD";
                advance();
                expect(LdfTokenType::LBrace, "{");
                out.nad = parseIntValue();
                expect(LdfTokenType::Comma, ",");
                out.id = parseIntValue();
                expect(LdfTokenType::Comma, ",");
                out.byte = parseIntValue();
                expect(LdfTokenType::Comma, ",");
                out.mask = parseIntValue();
                expect(LdfTokenType::Comma, ",");
                out.inv = parseIntValue();
                expect(LdfTokenType::Comma, ",");
                out.newNad = parseIntValue();
                expect(LdfTokenType::RBrace, "}");
                return out;
            case LdfTokenType::KW_DATA_DUMP:
                out.type = "DataDump";
                advance();
                expect(LdfTokenType::LBrace, "{");
                out.nodeName = parseIdentifier();
                expect(LdfTokenType::Comma, ",");
                for (int i = 0; i < 5; ++i) {
                    out.data.push_back(parseIntValue());
                    if (i < 4) {
                        expect(LdfTokenType::Comma, ",");
                    }
                }
                expect(LdfTokenType::RBrace, "}");
                return out;
            case LdfTokenType::KW_SAVE_CONFIGURATION:
                out.type = "SaveConfiguration";
                advance();
                expect(LdfTokenType::LBrace, "{");
                out.nodeName = parseIdentifier();
                expect(LdfTokenType::RBrace, "}");
                return out;
            case LdfTokenType::KW_ASSIGN_FRAME_ID_RANGE:
                out.type = "AssignFrameIdRange";
                advance();
                expect(LdfTokenType::LBrace, "{");
                out.nodeName = parseIdentifier();
                expect(LdfTokenType::Comma, ",");
                out.frameIndex = parseIntValue();
                if (match(LdfTokenType::Comma)) {
                    out.pid1 = parseIntValue();
                    expect(LdfTokenType::Comma, ",");
                    out.pid2 = parseIntValue();
                    expect(LdfTokenType::Comma, ",");
                    out.pid3 = parseIntValue();
                    expect(LdfTokenType::Comma, ",");
                    out.pid4 = parseIntValue();
                }
                expect(LdfTokenType::RBrace, "}");
                return out;
            case LdfTokenType::KW_FREE_FORMAT:
                out.type = "FreeFormat";
                advance();
                expect(LdfTokenType::LBrace, "{");
                for (int i = 0; i < 8; ++i) {
                    out.data.push_back(parseIntValue());
                    if (i < 7) {
                        expect(LdfTokenType::Comma, ",");
                    }
                }
                expect(LdfTokenType::RBrace, "}");
                return out;
            case LdfTokenType::KW_ASSIGN_FRAME_ID:
                out.type = "AssignFrameId";
                advance();
                expect(LdfTokenType::LBrace, "{");
                out.nodeName = parseIdentifier();
                expect(LdfTokenType::Comma, ",");
                out.frameName = parseIdentifier();
                expect(LdfTokenType::RBrace, "}");
                return out;
            default:
                error("Unexpected schedule command: " + cur.text);
                advance();
                return out;
        }
    }

    std::vector<LdfSignalEncodingType> parseSignalEncodingTypes() {
        TraceGuard guard(*this, "signal_encoding_type_def");
        std::vector<LdfSignalEncodingType> out;
        expect(LdfTokenType::KW_SIGNAL_ENCODING_TYPES, "Signal_encoding_types");
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.push_back(parseSignalEncodingEntry());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfSignalEncodingType parseSignalEncodingEntry() {
        TraceGuard guard(*this, "signal_encoding_entry");
        LdfSignalEncodingType out;
        out.name = parseIdentifier();
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::KW_LOGICAL_VALUE || cur.type == LdfTokenType::KW_PHYSICAL_VALUE || cur.type == LdfTokenType::KW_BCD_VALUE || cur.type == LdfTokenType::KW_ASCII_VALUE) {
            out.values.push_back(parseSignalEncodingValue());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfSignalEncodingValue parseSignalEncodingValue() {
        TraceGuard guard(*this, "signal_encoding_value");
        LdfSignalEncodingValue out;
        if (cur.type == LdfTokenType::KW_LOGICAL_VALUE) {
            out.valueType = "logical";
            advance();
            expect(LdfTokenType::Comma, ",");
            out.signalValue = static_cast<double>(parseIntValue());
            if (match(LdfTokenType::Comma)) {
                out.text = parseString();
            }
            expect(LdfTokenType::Semicolon, ";");
            return out;
        }
        if (cur.type == LdfTokenType::KW_PHYSICAL_VALUE) {
            out.valueType = "range";
            advance();
            expect(LdfTokenType::Comma, ",");
            out.minValue = parseIntValue();
            expect(LdfTokenType::Comma, ",");
            out.maxValue = parseIntValue();
            expect(LdfTokenType::Comma, ",");
            out.scale = parseNumber();
            expect(LdfTokenType::Comma, ",");
            out.offset = parseNumber();
            if (match(LdfTokenType::Comma)) {
                out.text = parseString();
            }
            expect(LdfTokenType::Semicolon, ";");
            return out;
        }
        if (cur.type == LdfTokenType::KW_BCD_VALUE) {
            out.valueType = "bcd";
            advance();
            expect(LdfTokenType::Semicolon, ";");
            return out;
        }
        if (cur.type == LdfTokenType::KW_ASCII_VALUE) {
            out.valueType = "ascii";
            advance();
            expect(LdfTokenType::Semicolon, ";");
            return out;
        }
        error("Unexpected signal encoding value");
        advance();
        return out;
    }

    std::vector<LdfSignalRepresentation> parseSignalRepresentations() {
        TraceGuard guard(*this, "signal_representation_def");
        std::vector<LdfSignalRepresentation> out;
        expect(LdfTokenType::KW_SIGNAL_REPRESENTATION, "Signal_representation");
        expect(LdfTokenType::LBrace, "{");
        while (cur.type == LdfTokenType::Identifier) {
            out.push_back(parseSignalRepresentationEntry());
        }
        expect(LdfTokenType::RBrace, "}");
        return out;
    }

    LdfSignalRepresentation parseSignalRepresentationEntry() {
        TraceGuard guard(*this, "signal_representation_entry");
        LdfSignalRepresentation out;
        out.encodingName = parseIdentifier();
        expect(LdfTokenType::Colon, ":");
        out.signalNames.push_back(parseIdentifier());
        while (match(LdfTokenType::Comma)) {
            out.signalNames.push_back(parseIdentifier());
        }
        expect(LdfTokenType::Semicolon, ";");
        return out;
    }
};

#endif // __LDF_PARSER_H