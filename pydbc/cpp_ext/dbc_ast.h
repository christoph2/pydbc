
#if !defined(__DBC_AST_H)
#define __DBC_AST_H

#include <string>
#include <vector>
#include <variant>
#include <cstdint>

struct ValueDescription {
    double value = 0;
    std::string description;
};

struct ValueTable {
    std::string name;
    std::vector<ValueDescription> descriptions;
};

struct Signal {
    std::string name;
    std::string multiplexerIndicator;
    int startBit = 0;
    int size = 0;
    int byteOrder = 0; // 0 Motorola, 1 Intel per DBC
    char sign = '+'; // '+' or '-'
    double factor = 1.0;
    double offset = 0.0;
    double minimum = 0.0;
    double maximum = 0.0;
    std::string unit;
    std::vector<std::string> receivers;
};

struct Message {
    uint32_t id = 0;
    std::string name;
    int size = 0;
    std::string transmitter;
    std::vector<Signal> signals;
};

struct Comment {
    enum class Type { Node, Message, Signal, EnvVar, Generic } type = Type::Generic;
    uint32_t id = 0; // Message ID or ID for Signal
    std::string name; // Node name, Signal name, or EnvVar name
    std::string comment;
};

struct AttributeDefinition {
    enum class ObjectType { Node, Message, Signal, EnvVar, NodeSignalRel, NodeEvRel, NodeBoRel, None } objectType = ObjectType::None;
    std::string name;
    std::string valueType; // e.g., "INT", "ENUM", etc.
    // Simplified value storage
    std::vector<std::string> enumValues;
    double min = 0;
    double max = 0;
};

struct AttributeValue {
    std::string name;
    enum class ObjectType { Node, Message, Signal, EnvVar, NodeSignalRel, NodeEvRel, NodeBoRel, None } objectType = ObjectType::None;
    std::string objectName; // Used for Node, EnvVar, and first part of Relation (Node name)
    uint32_t messageId = 0; // Used for Message, Signal, and second part of Relation (Message ID)
    std::string secondObjectName; // Used for Signal (Signal name) and second part of Relation (Signal/Ev/Bo name)
    std::string value; // Stored as string for simplicity
};

struct EnvironmentVariable {
    std::string name;
    int type = 0;
    double min = 0;
    double max = 0;
    std::string unit;
    double initialValue = 0;
    int id = 0;
    std::vector<std::string> accessNodes;
};

struct SignalGroup {
    uint32_t messageId = 0;
    std::string name;
    int value = 0;
    std::vector<std::string> signals;
};

struct SignalExtendedValueType {
    uint32_t messageId = 0;
    std::string signalName;
    int valueType = 0;
};

struct MessageTransmitter {
    uint32_t messageId = 0;
    std::vector<std::string> transmitters;
};

struct DbcFile {
    std::string filename;
    std::string version;
    std::vector<std::string> newSymbols;
    struct {
        uint32_t baudrate = 0;
        int btr1 = 0;
        int btr2 = 0;
    } bitTiming;
    std::vector<std::string> nodes;
    std::vector<ValueTable> valueTables;
    std::vector<Message> messages;
    std::vector<Comment> comments;
    std::vector<AttributeDefinition> attributeDefinitions;
    std::vector<AttributeValue> attributeDefaults;
    std::vector<AttributeValue> attributeValues;
    std::vector<EnvironmentVariable> environmentVariables;
    std::vector<SignalGroup> signalGroups;
    std::vector<SignalExtendedValueType> signalExtendedValueTypes;
    std::vector<MessageTransmitter> messageTransmitters;
};

#endif // __DBC_AST_H
