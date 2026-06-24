#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <sstream>
#include "ncf_parser.h"
#include "ncf_ast.h"
#include "diagnostic.h"

namespace py = pybind11;

template<typename T>
std::string list_to_string(const std::vector<T>& vec) {
    std::ostringstream oss;
    oss << "[";
    for (size_t i = 0; i < vec.size(); ++i) {
        if constexpr (std::is_same_v<T, std::string>) {
            oss << "'" << vec[i] << "'";
        } else {
            oss << py::repr(py::cast(vec[i]));
        }
        if (i < vec.size() - 1) oss << ", ";
    }
    oss << "]";
    return oss.str();
}

PYBIND11_MODULE(ncf_extension, m) {
    m.doc() = "C++ NCF Parser extension for Python";

    py::class_<Diagnostic> diag(m, "Diagnostic");
    diag.def_readonly("severity", &Diagnostic::severity)
        .def_readonly("file", &Diagnostic::file)
        .def_readonly("line", &Diagnostic::line)
        .def_readonly("column", &Diagnostic::column)
        .def_readonly("message", &Diagnostic::message)
        .def("__repr__", [](const Diagnostic& d) {
            std::ostringstream oss;
            oss << "Diagnostic(severity=" << py::repr(py::cast(d.severity))
                << ", file='" << d.file << "', line=" << d.line
                << ", column=" << d.column << ", message='" << d.message << "')";
            return oss.str();
        })
        .def("__str__", [](const Diagnostic& d) { return py::repr(py::cast(d)); });

    py::enum_<Diagnostic::Severity>(diag, "Severity")
        .value("Error",   Diagnostic::Severity::Error)
        .value("Warning", Diagnostic::Severity::Warning)
        .value("Info",    Diagnostic::Severity::Info)
        .export_values();

    py::class_<NcfInitValue>(m, "NcfInitValue")
        .def_readonly("is_array",     &NcfInitValue::isArray)
        .def_readonly("scalar",       &NcfInitValue::scalar)
        .def_readonly("array_values", &NcfInitValue::arrayValues)
        .def("__repr__", [](const NcfInitValue& v) {
            std::ostringstream oss;
            oss << "NcfInitValue(is_array=" << (v.isArray ? "True" : "False")
                << ", scalar=" << v.scalar
                << ", array_values=" << list_to_string(v.arrayValues) << ")";
            return oss.str();
        })
        .def("__str__", [](const NcfInitValue& v) { return py::repr(py::cast(v)); });

    py::class_<NcfBitrateDefinition>(m, "NcfBitrateDefinition")
        .def_readonly("type",       &NcfBitrateDefinition::type)
        .def_readonly("min_br",     &NcfBitrateDefinition::minBr)
        .def_readonly("max_br",     &NcfBitrateDefinition::maxBr)
        .def_readonly("rates",      &NcfBitrateDefinition::rates)
        .def_readonly("fixed_rate", &NcfBitrateDefinition::fixedRate)
        .def("__repr__", [](const NcfBitrateDefinition& b) {
            std::ostringstream oss;
            oss << "NcfBitrateDefinition(type='" << b.type
                << "', min_br=" << py::repr(py::cast(b.minBr))
                << ", max_br=" << py::repr(py::cast(b.maxBr))
                << ", rates=" << list_to_string(b.rates)
                << ", fixed_rate=" << py::repr(py::cast(b.fixedRate)) << ")";
            return oss.str();
        })
        .def("__str__", [](const NcfBitrateDefinition& b) { return py::repr(py::cast(b)); });

    py::class_<NcfGeneralDef>(m, "NcfGeneralDef")
        .def_readonly("protocol_version",     &NcfGeneralDef::protocolVersion)
        .def_readonly("supplier_id",          &NcfGeneralDef::supplierId)
        .def_readonly("function_id",          &NcfGeneralDef::functionId)
        .def_readonly("variant_id",           &NcfGeneralDef::variantId)
        .def_readonly("bitrate",              &NcfGeneralDef::bitrate)
        .def_readonly("sends_wake_up_signal", &NcfGeneralDef::sendsWakeUpSignal)
        .def_readonly("volt_from",            &NcfGeneralDef::voltFrom)
        .def_readonly("volt_to",              &NcfGeneralDef::voltTo)
        .def_readonly("temp_from",            &NcfGeneralDef::tempFrom)
        .def_readonly("temp_to",              &NcfGeneralDef::tempTo)
        .def_readonly("conformance",          &NcfGeneralDef::conformance)
        .def("__repr__", [](const NcfGeneralDef& g) {
            std::ostringstream oss;
            oss << "NcfGeneralDef(protocol_version='" << g.protocolVersion
                << "', supplier_id=" << g.supplierId
                << ", function_id=" << g.functionId
                << ", variant_id=" << g.variantId << ")";
            return oss.str();
        })
        .def("__str__", [](const NcfGeneralDef& g) { return py::repr(py::cast(g)); });

    py::class_<NcfDiagnosticDef>(m, "NcfDiagnosticDef")
        .def_readonly("nad_lhs",             &NcfDiagnosticDef::nadLhs)
        .def_readonly("nad_rhs",             &NcfDiagnosticDef::nadRhs)
        .def_readonly("nad_list",            &NcfDiagnosticDef::nadList)
        .def_readonly("diagnostic_class",    &NcfDiagnosticDef::diagnosticClass)
        .def_readonly("p2_min",              &NcfDiagnosticDef::p2Min)
        .def_readonly("st_min",              &NcfDiagnosticDef::stMin)
        .def_readonly("n_as_timeout",        &NcfDiagnosticDef::nAsTimeout)
        .def_readonly("n_cr_timeout",        &NcfDiagnosticDef::nCrTimeout)
        .def_readonly("support_sids",        &NcfDiagnosticDef::supportSids)
        .def_readonly("max_message_length",  &NcfDiagnosticDef::maxMessageLength)
        .def("__repr__", [](const NcfDiagnosticDef& d) {
            std::ostringstream oss;
            oss << "NcfDiagnosticDef(nad_lhs=" << d.nadLhs
                << ", nad_rhs=" << py::repr(py::cast(d.nadRhs)) << ")";
            return oss.str();
        })
        .def("__str__", [](const NcfDiagnosticDef& d) { return py::repr(py::cast(d)); });

    py::class_<NcfSignalProperties>(m, "NcfSignalProperties")
        .def_readonly("init_value",    &NcfSignalProperties::initValue)
        .def_readonly("size",          &NcfSignalProperties::size)
        .def_readonly("offset",        &NcfSignalProperties::offset)
        .def_readonly("encoding_name", &NcfSignalProperties::encodingName)
        .def("__repr__", [](const NcfSignalProperties& p) {
            std::ostringstream oss;
            oss << "NcfSignalProperties(size=" << p.size
                << ", offset=" << p.offset
                << ", encoding_name=" << py::repr(py::cast(p.encodingName)) << ")";
            return oss.str();
        })
        .def("__str__", [](const NcfSignalProperties& p) { return py::repr(py::cast(p)); });

    py::class_<NcfSignalDef>(m, "NcfSignalDef")
        .def_readonly("name",       &NcfSignalDef::name)
        .def_readonly("properties", &NcfSignalDef::properties)
        .def("__repr__", [](const NcfSignalDef& s) {
            std::ostringstream oss;
            oss << "NcfSignalDef(name='" << s.name << "', properties=" << py::repr(py::cast(s.properties)) << ")";
            return oss.str();
        })
        .def("__str__", [](const NcfSignalDef& s) { return py::repr(py::cast(s)); });

    py::class_<NcfFrameProperties>(m, "NcfFrameProperties")
        .def_readonly("length",               &NcfFrameProperties::length)
        .def_readonly("min_period",           &NcfFrameProperties::minPeriod)
        .def_readonly("max_period",           &NcfFrameProperties::maxPeriod)
        .def_readonly("event_triggered_frame",&NcfFrameProperties::eventTriggeredFrame)
        .def("__repr__", [](const NcfFrameProperties& p) {
            std::ostringstream oss;
            oss << "NcfFrameProperties(length=" << p.length << ")";
            return oss.str();
        })
        .def("__str__", [](const NcfFrameProperties& p) { return py::repr(py::cast(p)); });

    py::class_<NcfSingleFrame>(m, "NcfSingleFrame")
        .def_readonly("kind",       &NcfSingleFrame::kind)
        .def_readonly("name",       &NcfSingleFrame::name)
        .def_readonly("properties", &NcfSingleFrame::properties)
        .def_readonly("signals",    &NcfSingleFrame::signals)
        .def("__repr__", [](const NcfSingleFrame& f) {
            std::ostringstream oss;
            oss << "NcfSingleFrame(kind='" << f.kind << "', name='" << f.name << "')";
            return oss.str();
        })
        .def("__str__", [](const NcfSingleFrame& f) { return py::repr(py::cast(f)); });

    py::class_<NcfLogicalValue>(m, "NcfLogicalValue")
        .def_readonly("signal_value", &NcfLogicalValue::signalValue)
        .def_readonly("text_info",    &NcfLogicalValue::textInfo)
        .def("__repr__", [](const NcfLogicalValue& v) {
            std::ostringstream oss;
            oss << "NcfLogicalValue(signal_value=" << v.signalValue
                << ", text_info=" << py::repr(py::cast(v.textInfo)) << ")";
            return oss.str();
        })
        .def("__str__", [](const NcfLogicalValue& v) { return py::repr(py::cast(v)); });

    py::class_<NcfPhysicalRange>(m, "NcfPhysicalRange")
        .def_readonly("min_value",  &NcfPhysicalRange::minValue)
        .def_readonly("max_value",  &NcfPhysicalRange::maxValue)
        .def_readonly("scale",      &NcfPhysicalRange::scale)
        .def_readonly("offset_val", &NcfPhysicalRange::offsetVal)
        .def_readonly("text_info",  &NcfPhysicalRange::textInfo)
        .def("__repr__", [](const NcfPhysicalRange& r) {
            std::ostringstream oss;
            oss << "NcfPhysicalRange(min_value=" << r.minValue
                << ", max_value=" << r.maxValue
                << ", scale=" << r.scale
                << ", offset_val=" << r.offsetVal << ")";
            return oss.str();
        })
        .def("__str__", [](const NcfPhysicalRange& r) { return py::repr(py::cast(r)); });

    py::class_<NcfEncodingValue>(m, "NcfEncodingValue")
        .def_readonly("type",          &NcfEncodingValue::type)
        .def_readonly("logical_value", &NcfEncodingValue::logicalValue)
        .def_readonly("physical_range",&NcfEncodingValue::physicalRange)
        .def("__repr__", [](const NcfEncodingValue& v) {
            std::ostringstream oss;
            oss << "NcfEncodingValue(type='" << v.type << "')";
            return oss.str();
        })
        .def("__str__", [](const NcfEncodingValue& v) { return py::repr(py::cast(v)); });

    py::class_<NcfEncodingEntry>(m, "NcfEncodingEntry")
        .def_readonly("name",   &NcfEncodingEntry::name)
        .def_readonly("values", &NcfEncodingEntry::values)
        .def("__repr__", [](const NcfEncodingEntry& e) {
            std::ostringstream oss;
            oss << "NcfEncodingEntry(name='" << e.name << "')";
            return oss.str();
        })
        .def("__str__", [](const NcfEncodingEntry& e) { return py::repr(py::cast(e)); });

    py::class_<NcfStatusManagement>(m, "NcfStatusManagement")
        .def_readonly("response_error",       &NcfStatusManagement::responseError)
        .def_readonly("fault_state_signals",  &NcfStatusManagement::faultStateSignals)
        .def("__repr__", [](const NcfStatusManagement& s) {
            std::ostringstream oss;
            oss << "NcfStatusManagement(response_error='" << s.responseError << "')";
            return oss.str();
        })
        .def("__str__", [](const NcfStatusManagement& s) { return py::repr(py::cast(s)); });

    py::class_<NcfNodeDef>(m, "NcfNodeDef")
        .def_readonly("name",      &NcfNodeDef::name)
        .def_readonly("general",   &NcfNodeDef::general)
        .def_readonly("diagnostic",&NcfNodeDef::diagnostic)
        .def_readonly("frames",    &NcfNodeDef::frames)
        .def_readonly("encodings", &NcfNodeDef::encodings)
        .def_readonly("status",    &NcfNodeDef::status)
        .def_readonly("free_text", &NcfNodeDef::freeText)
        .def("__repr__", [](const NcfNodeDef& n) {
            std::ostringstream oss;
            oss << "NcfNodeDef(name='" << n.name << "')";
            return oss.str();
        })
        .def("__str__", [](const NcfNodeDef& n) { return py::repr(py::cast(n)); });

    py::class_<NcfFile>(m, "NcfFile")
        .def_readonly("filename",         &NcfFile::filename)
        .def_readonly("language_version", &NcfFile::languageVersion)
        .def_readonly("nodes",            &NcfFile::nodes)
        .def("__repr__", [](const NcfFile& f) {
            std::ostringstream oss;
            oss << "NcfFile(filename='" << f.filename
                << "', language_version='" << f.languageVersion
                << "', nodes=" << list_to_string(f.nodes) << ")";
            return oss.str();
        })
        .def("__str__", [](const NcfFile& f) { return py::repr(py::cast(f)); });

    py::class_<NcfParser>(m, "NcfParser")
        .def(py::init<const std::string&, const std::string&>(), 
             py::arg("filename") = "", py::arg("content") = "")
        .def("parse",            &NcfParser::parse)
        .def("set_trace",        &NcfParser::setTrace)
        .def("get_diagnostics",  &NcfParser::getDiagnostics);
}
