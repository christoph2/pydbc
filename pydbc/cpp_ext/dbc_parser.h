
#if !defined(__DBC_PARSER_H)
#define __DBC_PARSER_H

#include "lexer.h"
#include "dbc_ast.h"
#include <memory>
#include <unordered_set>
#include <iostream>
#include <fstream>

class DbcParser {
public:
    DbcParser(const std::string& filename = {})
    : lexer(filename), file(filename) {
        advance();
    }

    void setTrace(bool enable) { traceEnabled = enable; }

    DbcFile parse() {
        DbcFile out;
        out.filename = file;
        diagnostics.clear();
        // top-level: loop until EOF
        while (cur.type != TokenType::EndOfFile) {
            trace("Top-level: " + cur.text);
            if (cur.type == TokenType::KW_VERSION) {
                parseVersion(out);
            } else if (cur.type == TokenType::KW_NS) {
                parseNewSymbols(out);
            } else if (cur.type == TokenType::KW_BS) {
                parseBitTiming(out);
            } else if (cur.type == TokenType::KW_BU) {
                parseNodes(out);
            } else if (cur.type == TokenType::KW_VAL_TABLE) {
                parseValueTable(out);
            } else if (cur.type == TokenType::KW_BO) {
                parseMessage(out);
            } else if (cur.type == TokenType::KW_CM) {
                parseComment(out);
            } else if (cur.type == TokenType::KW_BA_DEF_) {
                parseAttributeDefinition(out);
            } else if (cur.type == TokenType::KW_BA_DEF_REL_) {
                parseRelationAttributeDefinition(out);
            } else if (cur.type == TokenType::KW_BA_DEF_DEF_) {
                parseAttributeDefault(out);
            } else if (cur.type == TokenType::KW_BA_DEF_DEF_REL_) {
                parseAttributeDefault(out);
            } else if (cur.type == TokenType::KW_BA_) {
                parseAttributeValue(out);
            } else if (cur.type == TokenType::KW_BA_REL_) {
                parseRelationAttributeValue(out);
            } else if (cur.type == TokenType::KW_VAL) {
                parseObjectValueTable(out);
            } else if (cur.type == TokenType::KW_EV) {
                parseEnvironmentVariable(out);
            } else if (cur.type == TokenType::KW_SIG_VALTYPE) {
                parseSignalExtendedValueType(out);
            } else if (cur.type == TokenType::KW_BO_TX_BU) {
                parseMessageTransmitter(out);
            } else if (cur.type == TokenType::KW_SIG_GROUP) {
                parseSignalGroup(out);
            } else if (cur.type == TokenType::KW_SG_MUL_VAL) {
                parseSignalMultiplexValue(out);
            } else if (cur.type == TokenType::Semicolon) {
                // Ignore stray semicolons at top level
                advance();
            } else {
                error("Unexpected token at top-level: " + cur.text);
                recoverTopLevel();
            }
        }
        // append lexer diagnostics
        for (auto &d: lexer.diagnostics()) diagnostics.push_back(d);
        return out;
    }

    const std::vector<Diagnostic>& getDiagnostics() const { return diagnostics; }

private:
    Lexer lexer;
    Token cur;
    std::string file;
    std::vector<Diagnostic> diagnostics;
    bool traceEnabled = false;
    int traceIndent = 0;

    struct TraceGuard {
        DbcParser& p;
        TraceGuard(DbcParser& p, const std::string& msg) : p(p) {
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

    bool match(TokenType t) {
        if (cur.type == t) { advance(); return true; }
        return false;
    }

    void expect(TokenType t, const std::string& errMsg) {
        if (cur.type == t) { advance(); return; }
        error(errMsg + " (got '" + cur.text + "')");
    }

    void error(const std::string& msg) {
        Diagnostic d; d.severity = Diagnostic::Severity::Error; d.file = file; d.line = cur.line; d.column = cur.column;
        d.message = msg;
        diagnostics.push_back(d);
    }

    long long toInt(const std::string& s) {
        try {
            return std::stoll(s);
        } catch (const std::exception& e) {
            error("Numeric value out of range or invalid: " + s);
            return 0;
        }
    }

    unsigned long long toUInt(const std::string& s) {
        try {
            return std::stoull(s);
        } catch (const std::exception& e) {
            error("Numeric value out of range or invalid: " + s);
            return 0;
        }
    }

    double toDouble(const std::string& s) {
        try {
            return std::stod(s);
        } catch (const std::exception& e) {
            error("Numeric value out of range or invalid: " + s);
            return 0.0;
        }
    }

    void recoverTopLevel() {
        recoverTo({TokenType::KW_VERSION, TokenType::KW_NS, TokenType::KW_BS, TokenType::KW_BU, 
                   TokenType::KW_VAL_TABLE, TokenType::KW_BO, TokenType::KW_CM, TokenType::KW_BA_DEF_,
                   TokenType::KW_BA_DEF_DEF_, TokenType::KW_BA_, TokenType::KW_VAL, TokenType::KW_EV,
                   TokenType::KW_SIG_VALTYPE, TokenType::KW_BO_TX_BU, TokenType::KW_SIG_GROUP,
                   TokenType::EndOfFile});
    }

    void recoverTo(const std::unordered_set<TokenType>& sync) {
        while (cur.type != TokenType::EndOfFile) {
            if (sync.find(cur.type) != sync.end()) return;
            advance();
        }
    }

    void parseVersion(DbcFile& out) {
        TraceGuard tg(*this, "parseVersion");
        advance(); // VERSION
        if (cur.type == TokenType::String) { out.version = cur.text; advance(); }
        else error("Expected version string after VERSION");
    }

    void parseNewSymbols(DbcFile& out) {
        TraceGuard tg(*this, "parseNewSymbols");
        advance(); // NS_
        expect(TokenType::Colon, "Expected ':' after NS_");
        // In some DBCs, NS_ block is empty or followed by other things.
        // We read until we hit another known top-level keyword or a colon that doesn't make sense.
        while (cur.type == TokenType::Identifier || (int)cur.type >= (int)TokenType::KW_VERSION) {
            // If it's a known keyword, but we are inside NS_, we might want to stop 
            // if it's not one of the typical NS_ symbols. 
            // But usually NS_ is just a list of names.
            if (cur.type == TokenType::KW_BS || cur.type == TokenType::KW_BU || cur.type == TokenType::KW_BO) break;
            out.newSymbols.push_back(cur.text);
            advance();
        }
    }

    void parseBitTiming(DbcFile& out) {
        TraceGuard tg(*this, "parseBitTiming");
        advance(); // BS_
        expect(TokenType::Colon, "Expected ':' after BS_");
        if (cur.type == TokenType::Int) {
            out.bitTiming.baudrate = (uint32_t)toUInt(cur.text); advance();
            expect(TokenType::Colon, "Expected ':' after baudrate");
            if (cur.type == TokenType::Int) { out.bitTiming.btr1 = (int)toInt(cur.text); advance(); }
            expect(TokenType::Comma, "Expected ',' after btr1");
            if (cur.type == TokenType::Int) { out.bitTiming.btr2 = (int)toInt(cur.text); advance(); }
        }
        // BitTiming often ends without semicolon, but sometimes people add it.
        // The grammar doesn't show a semicolon for BS_.
    }

    void parseNodes(DbcFile& out) {
        TraceGuard tg(*this, "parseNodes");
        advance(); // BU_
        expect(TokenType::Colon, "Expected ':' after BU_");
        while (cur.type == TokenType::Identifier) {
            out.nodes.push_back(cur.text);
            advance();
        }
    }

    void parseValueTable(DbcFile& out) {
        TraceGuard tg(*this, "parseValueTable");
        advance(); // VAL_TABLE_
        ValueTable vt;
        if (cur.type == TokenType::Identifier) { vt.name = cur.text; advance(); }
        while (cur.type == TokenType::Int || cur.type == TokenType::Float) {
            ValueDescription vd;
            vd.value = toDouble(cur.text); advance();
            if (cur.type == TokenType::String) { vd.description = cur.text; advance(); }
            vt.descriptions.push_back(vd);
        }
        expect(TokenType::Semicolon, "Expected ';' after VAL_TABLE_");
        out.valueTables.push_back(vt);
    }

    void parseMessage(DbcFile& out) {
        TraceGuard tg(*this, "parseMessage");
        advance(); // BO_
        Message m;
        if (cur.type == TokenType::Int) { m.id = (uint32_t)toUInt(cur.text); advance(); }
        if (cur.type == TokenType::Identifier) { m.name = cur.text; advance(); }
        expect(TokenType::Colon, "Expected ':' after message name");
        if (cur.type == TokenType::Int) { m.size = (int)toInt(cur.text); advance(); }
        if (cur.type == TokenType::Identifier) { m.transmitter = cur.text; advance(); }

        while (cur.type == TokenType::KW_SG) {
            m.signals.push_back(parseSignal());
        }
        out.messages.push_back(m);
    }

    Signal parseSignal() {
        TraceGuard tg(*this, "parseSignal");
        advance(); // SG_
        Signal s;
        if (cur.type == TokenType::Identifier) { s.name = cur.text; advance(); }
        // check for multiplexer indicator
        // Multiplexer indicator can be 'M' or 'm<number>'
        // The lexer might have read 'm123' as a single identifier.
        if (cur.type == TokenType::Identifier) {
            if (cur.text == "M") {
                s.multiplexerIndicator = "M";
                advance();
            } else if (cur.text[0] == 'm') {
                if (cur.text.size() > 1) {
                    // Check if the rest is a number (e.g., "m123") or "m123M"
                    bool allDigits = true;
                    size_t last = cur.text.size();
                    bool endsWithM = (cur.text.back() == 'M');
                    if (endsWithM) last--;

                    for (size_t i = 1; i < last; ++i) {
                        if (!std::isdigit((unsigned char)cur.text[i])) {
                            allDigits = false;
                            break;
                        }
                    }
                    if (allDigits && last > 1) {
                        s.multiplexerIndicator = cur.text;
                        advance();
                    }
                } else {
                    // Just "m". Check if next token is an integer (e.g., "m 123")
                    s.multiplexerIndicator = "m";
                    advance();
                    if (cur.type == TokenType::Int) {
                        s.multiplexerIndicator += cur.text;
                        advance();
                    }
                }
            }
        }
        expect(TokenType::Colon, "Expected ':' after signal name");
        if (cur.type == TokenType::Int) { s.startBit = (int)toInt(cur.text); advance(); }
        expect(TokenType::Pipe, "Expected '|'");
        if (cur.type == TokenType::Int) { s.size = (int)toInt(cur.text); advance(); }
        expect(TokenType::At, "Expected '@'");
        if (cur.type == TokenType::Int) { s.byteOrder = (int)toInt(cur.text); advance(); }
        if (cur.type == TokenType::Plus || cur.type == TokenType::Minus) {
            s.sign = (cur.type == TokenType::Plus) ? '+' : '-';
            advance();
        }
        expect(TokenType::LParen, "Expected '('");
        if (cur.type == TokenType::Int || cur.type == TokenType::Float) { s.factor = toDouble(cur.text); advance(); }
        expect(TokenType::Comma, "Expected ','");
        if (cur.type == TokenType::Int || cur.type == TokenType::Float) { s.offset = toDouble(cur.text); advance(); }
        expect(TokenType::RParen, "Expected ')'");
        expect(TokenType::LBracket, "Expected '['");
        if (cur.type == TokenType::Int || cur.type == TokenType::Float) { s.minimum = toDouble(cur.text); advance(); }
        expect(TokenType::Pipe, "Expected '|'");
        if (cur.type == TokenType::Int || cur.type == TokenType::Float) { s.maximum = toDouble(cur.text); advance(); }
        expect(TokenType::RBracket, "Expected ']'");
        if (cur.type == TokenType::String) { s.unit = cur.text; advance(); }
        
        if (cur.type == TokenType::Identifier) {
            s.receivers.push_back(cur.text); advance();
            while (match(TokenType::Comma)) {
                if (cur.type == TokenType::Identifier) { s.receivers.push_back(cur.text); advance(); }
            }
        }
        return s;
    }

    void parseSignalMultiplexValue(DbcFile& out) {
        TraceGuard tg(*this, "parseSignalMultiplexValue");
        advance(); // SG_MUL_VAL_
        // SG_MUL_VAL_ <message_id> <signal_name> <multiplexer_name> <range>;
        if (cur.type == TokenType::Int) advance(); // message id
        if (cur.type == TokenType::Identifier) advance(); // signal name
        if (cur.type == TokenType::Identifier) advance(); // multiplexer name
        // range: 0-0
        if (cur.type == TokenType::Int) advance();
        if (cur.type == TokenType::Minus) advance();
        if (cur.type == TokenType::Int) advance();
        expect(TokenType::Semicolon, "Expected ';' after SG_MUL_VAL_");
    }

    void parseComment(DbcFile& out) {
        TraceGuard tg(*this, "parseComment");
        advance(); // CM_
        Comment c;
        if (match(TokenType::KW_BU)) {
            c.type = Comment::Type::Node;
            if (cur.type == TokenType::Identifier) { c.name = cur.text; advance(); }
        } else if (match(TokenType::KW_BO)) {
            c.type = Comment::Type::Message;
            if (cur.type == TokenType::Int) { c.id = (uint32_t)toUInt(cur.text); advance(); }
        } else if (match(TokenType::KW_SG)) {
            c.type = Comment::Type::Signal;
            if (cur.type == TokenType::Int) { c.id = (uint32_t)toUInt(cur.text); advance(); }
            if (cur.type == TokenType::Identifier) { c.name = cur.text; advance(); }
        } else if (match(TokenType::KW_EV)) {
            c.type = Comment::Type::EnvVar;
            if (cur.type == TokenType::Identifier) { c.name = cur.text; advance(); }
        }
        if (cur.type == TokenType::String) { c.comment = cur.text; advance(); }
        expect(TokenType::Semicolon, "Expected ';' after comment");
        out.comments.push_back(c);
    }

    void parseAttributeDefinition(DbcFile& out) {
        TraceGuard tg(*this, "parseAttributeDefinition");
        advance(); // BA_DEF_
        AttributeDefinition ad;
        if (match(TokenType::KW_BU)) ad.objectType = AttributeDefinition::ObjectType::Node;
        else if (match(TokenType::KW_BO)) ad.objectType = AttributeDefinition::ObjectType::Message;
        else if (match(TokenType::KW_SG)) ad.objectType = AttributeDefinition::ObjectType::Signal;
        else if (match(TokenType::KW_EV)) ad.objectType = AttributeDefinition::ObjectType::EnvVar;

        if (cur.type == TokenType::String) { ad.name = cur.text; advance(); }
        if (cur.type == TokenType::KW_INT || cur.type == TokenType::KW_HEX || cur.type == TokenType::KW_FLOAT) {
            ad.valueType = cur.text; advance();
            if (cur.type == TokenType::Int || cur.type == TokenType::Float) { ad.min = toDouble(cur.text); advance(); }
            if (cur.type == TokenType::Int || cur.type == TokenType::Float) { ad.max = toDouble(cur.text); advance(); }
        } else if (match(TokenType::KW_STRING)) {
            ad.valueType = "STRING";
        } else if (match(TokenType::KW_ENUM)) {
            ad.valueType = "ENUM";
            if (cur.type == TokenType::String) { ad.enumValues.push_back(cur.text); advance(); }
            while (match(TokenType::Comma)) {
                if (cur.type == TokenType::String) { ad.enumValues.push_back(cur.text); advance(); }
            }
        }
        expect(TokenType::Semicolon, "Expected ';' after BA_DEF_");
        out.attributeDefinitions.push_back(ad);
    }

    void parseAttributeDefault(DbcFile& out) {
        TraceGuard tg(*this, "parseAttributeDefault");
        bool isRel = (cur.type == TokenType::KW_BA_DEF_DEF_REL_);
        advance(); // BA_DEF_DEF_ or BA_DEF_DEF_REL_
        AttributeValue av;
        if (cur.type == TokenType::String) { av.name = cur.text; advance(); }
        if (cur.type == TokenType::String || cur.type == TokenType::Int || cur.type == TokenType::Float) {
            av.value = cur.text; advance();
        }
        expect(TokenType::Semicolon, "Expected ';' after attribute default");
        if (isRel) out.attributeDefaults.push_back(av); // We could have a separate vector if needed
        else out.attributeDefaults.push_back(av);
    }

    void parseAttributeValue(DbcFile& out) {
        TraceGuard tg(*this, "parseAttributeValue");
        advance(); // BA_
        AttributeValue av;
        if (cur.type == TokenType::String) { av.name = cur.text; advance(); }
        if (match(TokenType::KW_BU)) {
            av.objectType = AttributeValue::ObjectType::Node;
            if (cur.type == TokenType::Identifier) { av.objectName = cur.text; advance(); }
        } else if (match(TokenType::KW_BO)) {
            av.objectType = AttributeValue::ObjectType::Message;
            if (cur.type == TokenType::Int) { av.messageId = (uint32_t)toUInt(cur.text); advance(); }
        } else if (match(TokenType::KW_SG)) {
            av.objectType = AttributeValue::ObjectType::Signal;
            if (cur.type == TokenType::Int) { av.messageId = (uint32_t)toUInt(cur.text); advance(); }
            if (cur.type == TokenType::Identifier) { av.secondObjectName = cur.text; advance(); }
        } else if (match(TokenType::KW_EV)) {
            av.objectType = AttributeValue::ObjectType::EnvVar;
            if (cur.type == TokenType::Identifier) { av.objectName = cur.text; advance(); }
        }

        if (cur.type == TokenType::String || cur.type == TokenType::Int || cur.type == TokenType::Float) {
            av.value = cur.text; advance();
        }
        expect(TokenType::Semicolon, "Expected ';' after BA_");
        out.attributeValues.push_back(av);
    }

    void parseRelationAttributeDefinition(DbcFile& out) {
        TraceGuard tg(*this, "parseRelationAttributeDefinition");
        advance(); // BA_DEF_REL_
        AttributeDefinition ad;
        if (match(TokenType::KW_BU_SG_REL)) ad.objectType = AttributeDefinition::ObjectType::NodeSignalRel;
        else if (match(TokenType::KW_BU_EV_REL)) ad.objectType = AttributeDefinition::ObjectType::NodeEvRel;
        else if (match(TokenType::KW_BU_BO_REL)) ad.objectType = AttributeDefinition::ObjectType::NodeBoRel;

        if (cur.type == TokenType::String) { ad.name = cur.text; advance(); }
        if (cur.type == TokenType::KW_INT || cur.type == TokenType::KW_HEX || cur.type == TokenType::KW_FLOAT) {
            ad.valueType = cur.text; advance();
            if (cur.type == TokenType::Int || cur.type == TokenType::Float) { ad.min = toDouble(cur.text); advance(); }
            if (cur.type == TokenType::Int || cur.type == TokenType::Float) { ad.max = toDouble(cur.text); advance(); }
        } else if (match(TokenType::KW_STRING)) {
            ad.valueType = "STRING";
        } else if (match(TokenType::KW_ENUM)) {
            ad.valueType = "ENUM";
            if (cur.type == TokenType::String) { ad.enumValues.push_back(cur.text); advance(); }
            while (match(TokenType::Comma)) {
                if (cur.type == TokenType::String) { ad.enumValues.push_back(cur.text); advance(); }
            }
        }
        expect(TokenType::Semicolon, "Expected ';' after BA_DEF_REL_");
        out.attributeDefinitions.push_back(ad);
    }

    void parseRelationAttributeValue(DbcFile& out) {
        TraceGuard tg(*this, "parseRelationAttributeValue");
        advance(); // BA_REL_
        AttributeValue av;
        if (cur.type == TokenType::String) { av.name = cur.text; advance(); }
        
        if (match(TokenType::KW_BU_SG_REL)) {
            av.objectType = AttributeValue::ObjectType::NodeSignalRel;
            if (cur.type == TokenType::Identifier) { av.objectName = cur.text; advance(); } // Node
            if (match(TokenType::KW_SG)) {
                if (cur.type == TokenType::Int) { av.messageId = (uint32_t)toUInt(cur.text); advance(); } // Message ID
                if (cur.type == TokenType::Identifier) { av.secondObjectName = cur.text; advance(); } // Signal Name
            }
        } else if (match(TokenType::KW_BU_EV_REL)) {
            av.objectType = AttributeValue::ObjectType::NodeEvRel;
            if (cur.type == TokenType::Identifier) { av.objectName = cur.text; advance(); } // Node
            if (match(TokenType::KW_EV)) {
                if (cur.type == TokenType::Identifier) { av.secondObjectName = cur.text; advance(); } // Ev Name
            }
        } else if (match(TokenType::KW_BU_BO_REL)) {
            av.objectType = AttributeValue::ObjectType::NodeBoRel;
            if (cur.type == TokenType::Identifier) { av.objectName = cur.text; advance(); } // Node
            if (match(TokenType::KW_BO)) {
                if (cur.type == TokenType::Int) { av.messageId = (uint32_t)toUInt(cur.text); advance(); } // Message ID
            }
        }

        if (cur.type == TokenType::String || cur.type == TokenType::Int || cur.type == TokenType::Float) {
            av.value = cur.text; advance();
        }
        expect(TokenType::Semicolon, "Expected ';' after BA_REL_");
        out.attributeValues.push_back(av);
    }

    void parseObjectValueTable(DbcFile& out) {
        TraceGuard tg(*this, "parseObjectValueTable");
        advance(); // VAL_
        ValueTable vt;
        if (cur.type == TokenType::Int) {
            uint32_t msgId = (uint32_t)toUInt(cur.text); advance();
            if (cur.type == TokenType::Identifier) {
                vt.name = std::to_string(msgId) + " " + cur.text; advance();
            }
        } else if (cur.type == TokenType::Identifier) {
            vt.name = cur.text; advance();
        }

        while (cur.type == TokenType::Int || cur.type == TokenType::Float) {
            ValueDescription vd;
            vd.value = toDouble(cur.text); advance();
            if (cur.type == TokenType::String) { vd.description = cur.text; advance(); }
            vt.descriptions.push_back(vd);
        }
        expect(TokenType::Semicolon, "Expected ';' after VAL_");
        out.valueTables.push_back(vt);
    }

    void parseEnvironmentVariable(DbcFile& out) {
        TraceGuard tg(*this, "parseEnvironmentVariable");
        advance(); // EV_
        EnvironmentVariable ev;
        if (cur.type == TokenType::Identifier) { ev.name = cur.text; advance(); }
        expect(TokenType::Colon, "Expected ':' after EV_ name");
        if (cur.type == TokenType::Int) { ev.type = (int)toInt(cur.text); advance(); }
        expect(TokenType::LBracket, "Expected '['");
        if (cur.type == TokenType::Int || cur.type == TokenType::Float) { ev.min = toDouble(cur.text); advance(); }
        expect(TokenType::Pipe, "Expected '|'");
        if (cur.type == TokenType::Int || cur.type == TokenType::Float) { ev.max = toDouble(cur.text); advance(); }
        expect(TokenType::RBracket, "Expected ']'");
        if (cur.type == TokenType::String) { ev.unit = cur.text; advance(); }
        if (cur.type == TokenType::Int || cur.type == TokenType::Float) { ev.initialValue = toDouble(cur.text); advance(); }
        if (cur.type == TokenType::Int) { ev.id = (int)toInt(cur.text); advance(); }
        if (cur.type == TokenType::Identifier) { /* DUMMY_NODE_VECTOR */ advance(); }
        // The DUMMY_NODE_VECTOR is usually followed by a number (access type/node id)
        if (cur.type == TokenType::Int) { advance(); } 
        
        if (cur.type == TokenType::Identifier) {
            ev.accessNodes.push_back(cur.text); advance();
            while (match(TokenType::Comma)) {
                if (cur.type == TokenType::Identifier) { ev.accessNodes.push_back(cur.text); advance(); }
            }
        }
        expect(TokenType::Semicolon, "Expected ';' after EV_");
        out.environmentVariables.push_back(ev);
    }

    void parseSignalExtendedValueType(DbcFile& out) {
        TraceGuard tg(*this, "parseSignalExtendedValueType");
        advance(); // SIG_VALTYPE_
        SignalExtendedValueType sev;
        if (cur.type == TokenType::Int) { sev.messageId = (uint32_t)toUInt(cur.text); advance(); }
        if (cur.type == TokenType::Identifier) { sev.signalName = cur.text; advance(); }
        expect(TokenType::Colon, "Expected ':' after signal name");
        if (cur.type == TokenType::Int) { sev.valueType = (int)toInt(cur.text); advance(); }
        expect(TokenType::Semicolon, "Expected ';' after SIG_VALTYPE_");
        out.signalExtendedValueTypes.push_back(sev);
    }

    void parseMessageTransmitter(DbcFile& out) {
        TraceGuard tg(*this, "parseMessageTransmitter");
        advance(); // BO_TX_BU_
        MessageTransmitter mt;
        if (cur.type == TokenType::Int) { mt.messageId = (uint32_t)toUInt(cur.text); advance(); }
        expect(TokenType::Colon, "Expected ':' after message id");
        if (cur.type == TokenType::Identifier) {
            mt.transmitters.push_back(cur.text); advance();
            while (match(TokenType::Comma)) {
                if (cur.type == TokenType::Identifier) { mt.transmitters.push_back(cur.text); advance(); }
            }
        }
        expect(TokenType::Semicolon, "Expected ';' after BO_TX_BU_");
        out.messageTransmitters.push_back(mt);
    }

    void parseSignalGroup(DbcFile& out) {
        TraceGuard tg(*this, "parseSignalGroup");
        advance(); // SIG_GROUP_
        SignalGroup sg;
        if (cur.type == TokenType::Int) { sg.messageId = (uint32_t)toUInt(cur.text); advance(); }
        if (cur.type == TokenType::Identifier) { sg.name = cur.text; advance(); }
        if (cur.type == TokenType::Int) { sg.value = (int)toInt(cur.text); advance(); }
        expect(TokenType::Colon, "Expected ':' after signal group value");
        while (cur.type == TokenType::Identifier) {
            sg.signals.push_back(cur.text); advance();
        }
        expect(TokenType::Semicolon, "Expected ';' after SIG_GROUP_");
        out.signalGroups.push_back(sg);
    }
};

#endif // __DBC_PARSER_H
