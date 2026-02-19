#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <sstream>
#include <iomanip>
#include "ldf_parser.h"
#include "ldf_ast.h"
#include "diagnostic.h"

namespace py = pybind11;

template<typename T>
std::string to_string_with_precision(const T a_value, const int n = 6) {
    std::ostringstream out;
    out.precision(n);
    out << std::fixed << a_value;
    std::string str = out.str();
    str.erase(str.find_last_not_of('0') + 1, std::string::npos);
    if (!str.empty() && str.back() == '.') str.pop_back();
    return str;
}

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

PYBIND11_MODULE(ldf_extension, m) {
    m.doc() = "C++ LDF Parser extension for Python";

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
        .def("__str__", [](const Diagnostic& d) {
            return py::repr(py::cast(d));
        });

    py::enum_<Diagnostic::Severity>(diag, "Severity")
        .value("Error", Diagnostic::Severity::Error)
        .value("Warning", Diagnostic::Severity::Warning)
        .value("Info", Diagnostic::Severity::Info)
        .export_values();

    py::class_<LdfProductId>(m, "LdfProductId")
        .def_readonly("supplier_id", &LdfProductId::supplierId)
        .def_readonly("function_id", &LdfProductId::functionId)
        .def_readonly("variant", &LdfProductId::variant)
        .def("__repr__", [](const LdfProductId& p) {
            std::ostringstream oss;
            oss << "LdfProductId(supplier_id=" << p.supplierId
                << ", function_id=" << p.functionId
                << ", variant=" << py::repr(py::cast(p.variant)) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfProductId& p) {
            return py::repr(py::cast(p));
        });

    py::class_<LdfNodeDefinition>(m, "LdfNodeDefinition")
        .def_readonly("master", &LdfNodeDefinition::master)
        .def_readonly("time_base", &LdfNodeDefinition::timeBase)
        .def_readonly("jitter", &LdfNodeDefinition::jitter)
        .def_readonly("bit_length", &LdfNodeDefinition::bitLength)
        .def_readonly("tolerant", &LdfNodeDefinition::tolerant)
        .def_readonly("slaves", &LdfNodeDefinition::slaves)
        .def("__repr__", [](const LdfNodeDefinition& n) {
            std::ostringstream oss;
            oss << "LdfNodeDefinition(master='" << n.master
                << "', time_base=" << n.timeBase
                << ", jitter=" << n.jitter
                << ", bit_length=" << py::repr(py::cast(n.bitLength))
                << ", tolerant=" << py::repr(py::cast(n.tolerant))
                << ", slaves=" << list_to_string(n.slaves) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfNodeDefinition& n) {
            return py::repr(py::cast(n));
        });

    py::class_<LdfConfigurableFrame>(m, "LdfConfigurableFrame")
        .def_readonly("frame_name", &LdfConfigurableFrame::frameName)
        .def_readonly("message_id", &LdfConfigurableFrame::messageId)
        .def("__repr__", [](const LdfConfigurableFrame& f) {
            std::ostringstream oss;
            oss << "LdfConfigurableFrame(frame_name='" << f.frameName
                << "', message_id=" << py::repr(py::cast(f.messageId)) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfConfigurableFrame& f) {
            return py::repr(py::cast(f));
        });

    py::class_<LdfNodeAttribute>(m, "LdfNodeAttribute")
        .def_readonly("name", &LdfNodeAttribute::name)
        .def_readonly("version", &LdfNodeAttribute::version)
        .def_readonly("configured_nad", &LdfNodeAttribute::configuredNad)
        .def_readonly("initial_nad", &LdfNodeAttribute::initialNad)
        .def_readonly("product_id", &LdfNodeAttribute::productId)
        .def_readonly("response_error_signal", &LdfNodeAttribute::responseErrorSignal)
        .def_readonly("fault_state_signals", &LdfNodeAttribute::faultStateSignals)
        .def_readonly("p2_min", &LdfNodeAttribute::p2Min)
        .def_readonly("st_min", &LdfNodeAttribute::stMin)
        .def_readonly("n_as_timeout", &LdfNodeAttribute::nAsTimeout)
        .def_readonly("n_cr_timeout", &LdfNodeAttribute::nCrTimeout)
        .def_readonly("response_tolerance", &LdfNodeAttribute::responseTolerance)
        .def_readonly("configurable_frames", &LdfNodeAttribute::configurableFrames)
        .def("__repr__", [](const LdfNodeAttribute& a) {
            std::ostringstream oss;
            oss << "LdfNodeAttribute(name='" << a.name
                << "', version='" << a.version
                << "', configured_nad=" << a.configuredNad
                << ", initial_nad=" << py::repr(py::cast(a.initialNad))
                << ", product_id=" << py::repr(py::cast(a.productId))
                << ", response_error_signal='" << a.responseErrorSignal
                << "', fault_state_signals=" << list_to_string(a.faultStateSignals)
                << ", p2_min=" << py::repr(py::cast(a.p2Min))
                << ", st_min=" << py::repr(py::cast(a.stMin))
                << ", n_as_timeout=" << py::repr(py::cast(a.nAsTimeout))
                << ", n_cr_timeout=" << py::repr(py::cast(a.nCrTimeout))
                << ", response_tolerance=" << py::repr(py::cast(a.responseTolerance))
                << ", configurable_frames=" << list_to_string(a.configurableFrames) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfNodeAttribute& a) {
            return py::repr(py::cast(a));
        });

    py::class_<LdfConfigurationItem>(m, "LdfConfigurationItem")
        .def_readonly("composite_node", &LdfConfigurationItem::compositeNode)
        .def_readonly("logical_nodes", &LdfConfigurationItem::logicalNodes)
        .def("__repr__", [](const LdfConfigurationItem& i) {
            std::ostringstream oss;
            oss << "LdfConfigurationItem(composite_node='" << i.compositeNode
                << "', logical_nodes=" << list_to_string(i.logicalNodes) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfConfigurationItem& i) {
            return py::repr(py::cast(i));
        });

    py::class_<LdfConfiguration>(m, "LdfConfiguration")
        .def_readonly("name", &LdfConfiguration::name)
        .def_readonly("items", &LdfConfiguration::items)
        .def("__repr__", [](const LdfConfiguration& c) {
            std::ostringstream oss;
            oss << "LdfConfiguration(name='" << c.name
                << "', items=" << list_to_string(c.items) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfConfiguration& c) {
            return py::repr(py::cast(c));
        });

    py::class_<LdfNodeComposition>(m, "LdfNodeComposition")
        .def_readonly("configurations", &LdfNodeComposition::configurations)
        .def("__repr__", [](const LdfNodeComposition& c) {
            std::ostringstream oss;
            oss << "LdfNodeComposition(configurations=" << list_to_string(c.configurations) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfNodeComposition& c) {
            return py::repr(py::cast(c));
        });

    py::class_<LdfInitValue>(m, "LdfInitValue")
        .def_readonly("is_array", &LdfInitValue::isArray)
        .def_readonly("scalar", &LdfInitValue::scalar)
        .def_readonly("array_values", &LdfInitValue::arrayValues)
        .def("__repr__", [](const LdfInitValue& v) {
            std::ostringstream oss;
            oss << "LdfInitValue(is_array=" << (v.isArray ? "True" : "False")
                << ", scalar=" << v.scalar
                << ", array_values=" << list_to_string(v.arrayValues) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfInitValue& v) {
            return py::repr(py::cast(v));
        });

    py::class_<LdfSignal>(m, "LdfSignal")
        .def_readonly("name", &LdfSignal::name)
        .def_readonly("size", &LdfSignal::size)
        .def_readonly("init_value", &LdfSignal::initValue)
        .def_readonly("published_by", &LdfSignal::publishedBy)
        .def_readonly("subscribed_by", &LdfSignal::subscribedBy)
        .def("__repr__", [](const LdfSignal& s) {
            std::ostringstream oss;
            oss << "LdfSignal(name='" << s.name
                << "', size=" << s.size
                << ", init_value=" << py::repr(py::cast(s.initValue))
                << ", published_by='" << s.publishedBy
                << "', subscribed_by=" << list_to_string(s.subscribedBy) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfSignal& s) {
            return py::repr(py::cast(s));
        });

    py::class_<LdfDiagnosticSignal>(m, "LdfDiagnosticSignal")
        .def_readonly("name", &LdfDiagnosticSignal::name)
        .def_readonly("size", &LdfDiagnosticSignal::size)
        .def_readonly("init_value", &LdfDiagnosticSignal::initValue)
        .def("__repr__", [](const LdfDiagnosticSignal& s) {
            std::ostringstream oss;
            oss << "LdfDiagnosticSignal(name='" << s.name
                << "', size=" << s.size
                << ", init_value=" << py::repr(py::cast(s.initValue)) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfDiagnosticSignal& s) {
            return py::repr(py::cast(s));
        });

    py::class_<LdfSignalGroupItem>(m, "LdfSignalGroupItem")
        .def_readonly("signal_name", &LdfSignalGroupItem::signalName)
        .def_readonly("group_offset", &LdfSignalGroupItem::groupOffset)
        .def("__repr__", [](const LdfSignalGroupItem& i) {
            std::ostringstream oss;
            oss << "LdfSignalGroupItem(signal_name='" << i.signalName
                << "', group_offset=" << i.groupOffset << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfSignalGroupItem& i) {
            return py::repr(py::cast(i));
        });

    py::class_<LdfSignalGroup>(m, "LdfSignalGroup")
        .def_readonly("name", &LdfSignalGroup::name)
        .def_readonly("group_size", &LdfSignalGroup::groupSize)
        .def_readonly("items", &LdfSignalGroup::items)
        .def("__repr__", [](const LdfSignalGroup& g) {
            std::ostringstream oss;
            oss << "LdfSignalGroup(name='" << g.name
                << "', group_size=" << g.groupSize
                << ", items=" << list_to_string(g.items) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfSignalGroup& g) {
            return py::repr(py::cast(g));
        });

    py::class_<LdfFrameSignal>(m, "LdfFrameSignal")
        .def_readonly("signal_name", &LdfFrameSignal::signalName)
        .def_readonly("signal_offset", &LdfFrameSignal::signalOffset)
        .def("__repr__", [](const LdfFrameSignal& s) {
            std::ostringstream oss;
            oss << "LdfFrameSignal(signal_name='" << s.signalName
                << "', signal_offset=" << s.signalOffset << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfFrameSignal& s) {
            return py::repr(py::cast(s));
        });

    py::class_<LdfFrame>(m, "LdfFrame")
        .def_readonly("name", &LdfFrame::name)
        .def_readonly("frame_id", &LdfFrame::frameId)
        .def_readonly("published_by", &LdfFrame::publishedBy)
        .def_readonly("frame_size", &LdfFrame::frameSize)
        .def_readonly("signals", &LdfFrame::signals)
        .def("__repr__", [](const LdfFrame& f) {
            std::ostringstream oss;
            oss << "LdfFrame(name='" << f.name
                << "', frame_id=" << f.frameId
                << ", published_by='" << f.publishedBy
                << "', frame_size=" << f.frameSize
                << ", signals=" << list_to_string(f.signals) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfFrame& f) {
            return py::repr(py::cast(f));
        });

    py::class_<LdfSporadicFrame>(m, "LdfSporadicFrame")
        .def_readonly("name", &LdfSporadicFrame::name)
        .def_readonly("frame_names", &LdfSporadicFrame::frameNames)
        .def("__repr__", [](const LdfSporadicFrame& f) {
            std::ostringstream oss;
            oss << "LdfSporadicFrame(name='" << f.name
                << "', frame_names=" << list_to_string(f.frameNames) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfSporadicFrame& f) {
            return py::repr(py::cast(f));
        });

    py::class_<LdfEventTriggeredFrame>(m, "LdfEventTriggeredFrame")
        .def_readonly("name", &LdfEventTriggeredFrame::name)
        .def_readonly("schedule_table", &LdfEventTriggeredFrame::scheduleTable)
        .def_readonly("frame_id", &LdfEventTriggeredFrame::frameId)
        .def_readonly("frame_names", &LdfEventTriggeredFrame::frameNames)
        .def("__repr__", [](const LdfEventTriggeredFrame& f) {
            std::ostringstream oss;
            oss << "LdfEventTriggeredFrame(name='" << f.name
                << "', schedule_table='" << f.scheduleTable
                << "', frame_id=" << f.frameId
                << ", frame_names=" << list_to_string(f.frameNames) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfEventTriggeredFrame& f) {
            return py::repr(py::cast(f));
        });

    py::class_<LdfDiagnosticFrameSignal>(m, "LdfDiagnosticFrameSignal")
        .def_readonly("signal_name", &LdfDiagnosticFrameSignal::signalName)
        .def_readonly("signal_offset", &LdfDiagnosticFrameSignal::signalOffset)
        .def("__repr__", [](const LdfDiagnosticFrameSignal& s) {
            std::ostringstream oss;
            oss << "LdfDiagnosticFrameSignal(signal_name='" << s.signalName
                << "', signal_offset=" << s.signalOffset << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfDiagnosticFrameSignal& s) {
            return py::repr(py::cast(s));
        });

    py::class_<LdfDiagnosticFrame>(m, "LdfDiagnosticFrame")
        .def_readonly("master_id", &LdfDiagnosticFrame::masterId)
        .def_readonly("slave_id", &LdfDiagnosticFrame::slaveId)
        .def_readonly("master_signals", &LdfDiagnosticFrame::masterSignals)
        .def_readonly("slave_signals", &LdfDiagnosticFrame::slaveSignals)
        .def("__repr__", [](const LdfDiagnosticFrame& f) {
            std::ostringstream oss;
            oss << "LdfDiagnosticFrame(master_id=" << f.masterId
                << ", slave_id=" << f.slaveId
                << ", master_signals=" << list_to_string(f.masterSignals)
                << ", slave_signals=" << list_to_string(f.slaveSignals) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfDiagnosticFrame& f) {
            return py::repr(py::cast(f));
        });

    py::class_<LdfScheduleTableCommand>(m, "LdfScheduleTableCommand")
        .def_readonly("type", &LdfScheduleTableCommand::type)
        .def_readonly("frame_time", &LdfScheduleTableCommand::frameTime)
        .def_readonly("frame_name", &LdfScheduleTableCommand::frameName)
        .def_readonly("node_name", &LdfScheduleTableCommand::nodeName)
        .def_readonly("nad", &LdfScheduleTableCommand::nad)
        .def_readonly("id", &LdfScheduleTableCommand::id)
        .def_readonly("byte", &LdfScheduleTableCommand::byte)
        .def_readonly("mask", &LdfScheduleTableCommand::mask)
        .def_readonly("inv", &LdfScheduleTableCommand::inv)
        .def_readonly("new_nad", &LdfScheduleTableCommand::newNad)
        .def_readonly("frame_index", &LdfScheduleTableCommand::frameIndex)
        .def_readonly("pid1", &LdfScheduleTableCommand::pid1)
        .def_readonly("pid2", &LdfScheduleTableCommand::pid2)
        .def_readonly("pid3", &LdfScheduleTableCommand::pid3)
        .def_readonly("pid4", &LdfScheduleTableCommand::pid4)
        .def_readonly("data", &LdfScheduleTableCommand::data)
        .def("__repr__", [](const LdfScheduleTableCommand& c) {
            std::ostringstream oss;
            oss << "LdfScheduleTableCommand(type='" << c.type
                << "', frame_time=" << c.frameTime
                << ", frame_name='" << c.frameName
                << "', node_name='" << c.nodeName
                << "', nad=" << c.nad
                << ", id=" << c.id
                << ", byte=" << c.byte
                << ", mask=" << c.mask
                << ", inv=" << c.inv
                << ", new_nad=" << c.newNad
                << ", frame_index=" << c.frameIndex
                << ", pid1=" << py::repr(py::cast(c.pid1))
                << ", pid2=" << py::repr(py::cast(c.pid2))
                << ", pid3=" << py::repr(py::cast(c.pid3))
                << ", pid4=" << py::repr(py::cast(c.pid4))
                << ", data=" << list_to_string(c.data) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfScheduleTableCommand& c) {
            return py::repr(py::cast(c));
        });

    py::class_<LdfScheduleTable>(m, "LdfScheduleTable")
        .def_readonly("name", &LdfScheduleTable::name)
        .def_readonly("commands", &LdfScheduleTable::commands)
        .def("__repr__", [](const LdfScheduleTable& t) {
            std::ostringstream oss;
            oss << "LdfScheduleTable(name='" << t.name
                << "', commands=" << list_to_string(t.commands) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfScheduleTable& t) {
            return py::repr(py::cast(t));
        });

    py::class_<LdfSignalEncodingValue>(m, "LdfSignalEncodingValue")
        .def_readonly("value_type", &LdfSignalEncodingValue::valueType)
        .def_readonly("signal_value", &LdfSignalEncodingValue::signalValue)
        .def_readonly("text", &LdfSignalEncodingValue::text)
        .def_readonly("min_value", &LdfSignalEncodingValue::minValue)
        .def_readonly("max_value", &LdfSignalEncodingValue::maxValue)
        .def_readonly("scale", &LdfSignalEncodingValue::scale)
        .def_readonly("offset", &LdfSignalEncodingValue::offset)
        .def("__repr__", [](const LdfSignalEncodingValue& v) {
            std::ostringstream oss;
            oss << "LdfSignalEncodingValue(value_type='" << v.valueType
                << "', signal_value=" << v.signalValue
                << ", text='" << v.text
                << "', min_value=" << v.minValue
                << ", max_value=" << v.maxValue
                << ", scale=" << v.scale
                << ", offset=" << v.offset << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfSignalEncodingValue& v) {
            return py::repr(py::cast(v));
        });

    py::class_<LdfSignalEncodingType>(m, "LdfSignalEncodingType")
        .def_readonly("name", &LdfSignalEncodingType::name)
        .def_readonly("values", &LdfSignalEncodingType::values)
        .def("__repr__", [](const LdfSignalEncodingType& t) {
            std::ostringstream oss;
            oss << "LdfSignalEncodingType(name='" << t.name
                << "', values=" << list_to_string(t.values) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfSignalEncodingType& t) {
            return py::repr(py::cast(t));
        });

    py::class_<LdfSignalRepresentation>(m, "LdfSignalRepresentation")
        .def_readonly("encoding_name", &LdfSignalRepresentation::encodingName)
        .def_readonly("signal_names", &LdfSignalRepresentation::signalNames)
        .def("__repr__", [](const LdfSignalRepresentation& r) {
            std::ostringstream oss;
            oss << "LdfSignalRepresentation(encoding_name='" << r.encodingName
                << "', signal_names=" << list_to_string(r.signalNames) << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfSignalRepresentation& r) {
            return py::repr(py::cast(r));
        });

    py::class_<LdfFile>(m, "LdfFile")
        .def_readonly("filename", &LdfFile::filename)
        .def_readonly("protocol_version", &LdfFile::protocolVersion)
        .def_readonly("language_version", &LdfFile::languageVersion)
        .def_readonly("file_revision", &LdfFile::fileRevision)
        .def_readonly("speed", &LdfFile::speed)
        .def_readonly("channel_name", &LdfFile::channelName)
        .def_readonly("nodes", &LdfFile::nodes)
        .def_readonly("node_composition", &LdfFile::nodeComposition)
        .def_readonly("signals", &LdfFile::signals)
        .def_readonly("diagnostic_signals", &LdfFile::diagnosticSignals)
        .def_readonly("frames", &LdfFile::frames)
        .def_readonly("sporadic_frames", &LdfFile::sporadicFrames)
        .def_readonly("event_triggered_frames", &LdfFile::eventTriggeredFrames)
        .def_readonly("diagnostic_frames", &LdfFile::diagnosticFrames)
        .def_readonly("node_attributes", &LdfFile::nodeAttributes)
        .def_readonly("schedule_tables", &LdfFile::scheduleTables)
        .def_readonly("signal_groups", &LdfFile::signalGroups)
        .def_readonly("signal_encoding_types", &LdfFile::signalEncodingTypes)
        .def_readonly("signal_representations", &LdfFile::signalRepresentations)
        .def("__repr__", [](const LdfFile& f) {
            std::ostringstream oss;
            oss << "LdfFile(filename='" << f.filename
                << "', protocol_version='" << f.protocolVersion
                << "', language_version='" << f.languageVersion
                << "', file_revision=" << py::repr(py::cast(f.fileRevision))
                << ", speed=" << f.speed
                << ", channel_name=" << py::repr(py::cast(f.channelName))
                << ", nodes=" << py::repr(py::cast(f.nodes))
                << ", node_composition=" << py::repr(py::cast(f.nodeComposition))
                << ", signals=" << list_to_string(f.signals)
                << ", diagnostic_signals=" << list_to_string(f.diagnosticSignals)
                << ", frames=" << list_to_string(f.frames)
                << ", sporadic_frames=" << list_to_string(f.sporadicFrames)
                << ", event_triggered_frames=" << list_to_string(f.eventTriggeredFrames)
                << ", diagnostic_frames=" << list_to_string(f.diagnosticFrames)
                << ", node_attributes=" << list_to_string(f.nodeAttributes)
                << ", schedule_tables=" << list_to_string(f.scheduleTables)
                << ", signal_groups=" << list_to_string(f.signalGroups)
                << ", signal_encoding_types=" << list_to_string(f.signalEncodingTypes)
                << ", signal_representations=" << list_to_string(f.signalRepresentations)
                << ")";
            return oss.str();
        })
        .def("__str__", [](const LdfFile& f) {
            return py::repr(py::cast(f));
        });

    py::class_<LdfParser>(m, "LdfParser")
        .def(py::init<const std::string&>(), py::arg("filename"))
        .def("parse", &LdfParser::parse)
        .def("set_trace", &LdfParser::setTrace)
        .def("get_diagnostics", &LdfParser::getDiagnostics);
}