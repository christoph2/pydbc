#ifndef __LDF_AST_H
#define __LDF_AST_H

#include <string>
#include <vector>
#include <optional>

struct LdfProductId {
    int supplierId = 0;
    int functionId = 0;
    std::optional<int> variant;
};

struct LdfNodeDefinition {
    std::string master;
    double timeBase = 0.0;
    double jitter = 0.0;
    std::optional<double> bitLength;
    std::optional<double> tolerant;
    std::vector<std::string> slaves;
};

struct LdfConfigurableFrame {
    std::string frameName;
    std::optional<int> messageId;
};

struct LdfNodeAttribute {
    std::string name;
    std::string version;
    int configuredNad = 0;
    std::optional<int> initialNad;
    LdfProductId productId;
    std::string responseErrorSignal;
    std::vector<std::string> faultStateSignals;
    std::optional<double> p2Min;
    std::optional<double> stMin;
    std::optional<double> nAsTimeout;
    std::optional<double> nCrTimeout;
    std::optional<double> responseTolerance;
    std::vector<LdfConfigurableFrame> configurableFrames;
};

struct LdfConfigurationItem {
    std::string compositeNode;
    std::vector<std::string> logicalNodes;
};

struct LdfConfiguration {
    std::string name;
    std::vector<LdfConfigurationItem> items;
};

struct LdfNodeComposition {
    std::vector<LdfConfiguration> configurations;
};

struct LdfInitValue {
    bool isArray = false;
    int scalar = 0;
    std::vector<int> arrayValues;
};

struct LdfSignal {
    std::string name;
    int size = 0;
    LdfInitValue initValue;
    std::string publishedBy;
    std::vector<std::string> subscribedBy;
};

struct LdfDiagnosticSignal {
    std::string name;
    int size = 0;
    LdfInitValue initValue;
};

struct LdfSignalGroupItem {
    std::string signalName;
    int groupOffset = 0;
};

struct LdfSignalGroup {
    std::string name;
    int groupSize = 0;
    std::vector<LdfSignalGroupItem> items;
};

struct LdfFrameSignal {
    std::string signalName;
    int signalOffset = 0;
};

struct LdfFrame {
    std::string name;
    int frameId = 0;
    std::string publishedBy;
    int frameSize = 0;
    std::vector<LdfFrameSignal> signals;
};

struct LdfSporadicFrame {
    std::string name;
    std::vector<std::string> frameNames;
};

struct LdfEventTriggeredFrame {
    std::string name;
    std::string scheduleTable;
    int frameId = 0;
    std::vector<std::string> frameNames;
};

struct LdfDiagnosticFrameSignal {
    std::string signalName;
    int signalOffset = 0;
};

struct LdfDiagnosticFrame {
    int masterId = 0;
    int slaveId = 0;
    std::vector<LdfDiagnosticFrameSignal> masterSignals;
    std::vector<LdfDiagnosticFrameSignal> slaveSignals;
};

struct LdfScheduleTableCommand {
    std::string type;
    double frameTime = 0.0;
    std::string frameName;
    std::string nodeName;
    int nad = 0;
    int id = 0;
    int byte = 0;
    int mask = 0;
    int inv = 0;
    int newNad = 0;
    int frameIndex = 0;
    std::optional<int> pid1;
    std::optional<int> pid2;
    std::optional<int> pid3;
    std::optional<int> pid4;
    std::vector<int> data;
};

struct LdfScheduleTable {
    std::string name;
    std::vector<LdfScheduleTableCommand> commands;
};

struct LdfSignalEncodingValue {
    std::string valueType;
    double signalValue = 0.0;
    std::string text;
    int minValue = 0;
    int maxValue = 0;
    double scale = 0.0;
    double offset = 0.0;
};

struct LdfSignalEncodingType {
    std::string name;
    std::vector<LdfSignalEncodingValue> values;
};

struct LdfSignalRepresentation {
    std::string encodingName;
    std::vector<std::string> signalNames;
};

struct LdfFile {
    std::string filename;
    std::string protocolVersion;
    std::string languageVersion;
    std::optional<std::string> fileRevision;
    double speed = 0.0;
    std::optional<std::string> channelName;
    LdfNodeDefinition nodes;
    std::optional<LdfNodeComposition> nodeComposition;
    std::vector<LdfSignal> signals;
    std::vector<LdfDiagnosticSignal> diagnosticSignals;
    std::vector<LdfFrame> frames;
    std::vector<LdfSporadicFrame> sporadicFrames;
    std::vector<LdfEventTriggeredFrame> eventTriggeredFrames;
    std::vector<LdfDiagnosticFrame> diagnosticFrames;
    std::vector<LdfNodeAttribute> nodeAttributes;
    std::vector<LdfScheduleTable> scheduleTables;
    std::vector<LdfSignalGroup> signalGroups;
    std::vector<LdfSignalEncodingType> signalEncodingTypes;
    std::vector<LdfSignalRepresentation> signalRepresentations;
};

#endif // __LDF_AST_H