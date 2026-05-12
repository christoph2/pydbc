#ifndef __NCF_AST_H
#define __NCF_AST_H

#include <string>
#include <vector>
#include <optional>

struct NcfInitValue {
    bool isArray = false;
    int scalar = 0;
    std::vector<int> arrayValues;
};

struct NcfBitrateDefinition {
    std::string type;  // "automatic", "select", "fixed"
    std::optional<double> minBr;
    std::optional<double> maxBr;
    std::vector<double> rates;
    std::optional<double> fixedRate;
};

struct NcfGeneralDef {
    std::string protocolVersion;
    int supplierId = 0;
    int functionId = 0;
    int variantId = 0;
    NcfBitrateDefinition bitrate;
    std::optional<bool> sendsWakeUpSignal;
    std::optional<double> voltFrom;
    std::optional<double> voltTo;
    std::optional<double> tempFrom;
    std::optional<double> tempTo;
    std::optional<std::string> conformance;
};

struct NcfDiagnosticDef {
    int nadLhs = 0;
    std::optional<int> nadRhs;
    std::vector<int> nadList;
    std::optional<int> diagnosticClass;
    std::optional<double> p2Min;
    std::optional<double> stMin;
    std::optional<double> nAsTimeout;
    std::optional<double> nCrTimeout;
    std::vector<int> supportSids;
    std::optional<int> maxMessageLength;
};

struct NcfSignalProperties {
    NcfInitValue initValue;
    int size = 0;
    int offset = 0;
    std::optional<std::string> encodingName;
};

struct NcfSignalDef {
    std::string name;
    NcfSignalProperties properties;
};

struct NcfFrameProperties {
    int length = 0;
    std::optional<int> minPeriod;
    std::optional<int> maxPeriod;
    std::optional<std::string> eventTriggeredFrame;
};

struct NcfSingleFrame {
    std::string kind;  // "publish" or "subscribe"
    std::string name;
    NcfFrameProperties properties;
    std::vector<NcfSignalDef> signals;
};

struct NcfLogicalValue {
    int signalValue = 0;
    std::optional<std::string> textInfo;
};

struct NcfPhysicalRange {
    int minValue = 0;
    int maxValue = 0;
    double scale = 0.0;
    double offsetVal = 0.0;
    std::optional<std::string> textInfo;
};

struct NcfEncodingValue {
    std::string type;  // "logical", "physical", "bcd", "ascii"
    std::optional<NcfLogicalValue> logicalValue;
    std::optional<NcfPhysicalRange> physicalRange;
};

struct NcfEncodingEntry {
    std::string name;
    std::vector<NcfEncodingValue> values;
};

struct NcfStatusManagement {
    std::string responseError;
    std::vector<std::string> faultStateSignals;
};

struct NcfNodeDef {
    std::string name;
    NcfGeneralDef general;
    NcfDiagnosticDef diagnostic;
    std::vector<NcfSingleFrame> frames;
    std::vector<NcfEncodingEntry> encodings;
    NcfStatusManagement status;
    std::optional<std::string> freeText;
};

struct NcfFile {
    std::string filename;
    std::string languageVersion;
    std::vector<NcfNodeDef> nodes;
};

#endif // __NCF_AST_H
