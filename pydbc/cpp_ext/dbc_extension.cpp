#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <sstream>
#include <iomanip>
#include "dbc_parser.h"
#include "dbc_ast.h"
#include "diagnostic.h"

namespace py = pybind11;

template<typename T>
std::string to_string_with_precision(const T a_value, const int n = 6) {
    std::ostringstream out;
    out.precision(n);
    out << std::fixed << a_value;
    std::string str = out.str();
    str.erase(str.find_last_not_of('0') + 1, std::string::npos);
    if (str.back() == '.') str.pop_back();
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

PYBIND11_MODULE(dbc_extension, m) {
    m.doc() = "C++ DBC Parser extension for Python";

    // Diagnostic
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

    // ValueDescription
    py::class_<ValueDescription>(m, "ValueDescription")
        .def(py::init<>())
        .def_readonly("value", &ValueDescription::value)
        .def_readonly("description", &ValueDescription::description)
        .def("__repr__", [](const ValueDescription& v) {
            std::ostringstream oss;
            oss << "ValueDescription(value=" << v.value << ", description='" << v.description << "')";
            return oss.str();
        })
        .def("__str__", [](const ValueDescription& v) {
            return py::repr(py::cast(v));
        });

    // ValueTable
    py::class_<ValueTable>(m, "ValueTable")
        .def(py::init<>())
        .def_readonly("name", &ValueTable::name)
        .def_readonly("descriptions", &ValueTable::descriptions)
        .def("__repr__", [](const ValueTable& v) {
            return "ValueTable(name='" + v.name + "', descriptions=" + list_to_string(v.descriptions) + ")";
        })
        .def("__str__", [](const ValueTable& v) {
            return py::repr(py::cast(v));
        });

    // Signal
    py::class_<Signal>(m, "Signal")
        .def(py::init<>())
        .def_readonly("name", &Signal::name)
        .def_readonly("multiplexer_indicator", &Signal::multiplexerIndicator)
        .def_readonly("start_bit", &Signal::startBit)
        .def_readonly("size", &Signal::size)
        .def_readonly("byte_order", &Signal::byteOrder)
        .def_readonly("sign", &Signal::sign)
        .def_readonly("factor", &Signal::factor)
        .def_readonly("offset", &Signal::offset)
        .def_readonly("minimum", &Signal::minimum)
        .def_readonly("maximum", &Signal::maximum)
        .def_readonly("unit", &Signal::unit)
        .def_readonly("receivers", &Signal::receivers)
        .def("__repr__", [](const Signal& s) {
            std::ostringstream oss;
            oss << "Signal(name='" << s.name << "', multiplexer_indicator='" << s.multiplexerIndicator 
                << "', start_bit=" << s.startBit << ", size=" << s.size << ", byte_order=" << s.byteOrder 
                << ", sign='" << s.sign << "', factor=" << s.factor << ", offset=" << s.offset 
                << ", minimum=" << s.minimum << ", maximum=" << s.maximum << ", unit='" << s.unit 
                << "', receivers=" << list_to_string(s.receivers) << ")";
            return oss.str();
        })
        .def("__str__", [](const Signal& s) {
            return py::repr(py::cast(s));
        });

    // Message
    py::class_<Message>(m, "Message")
        .def(py::init<>())
        .def_readonly("id", &Message::id)
        .def_readonly("name", &Message::name)
        .def_readonly("size", &Message::size)
        .def_readonly("transmitter", &Message::transmitter)
        .def_readonly("signals", &Message::signals)
        .def("__repr__", [](const Message& m) {
            std::ostringstream oss;
            oss << "Message(id=" << m.id << ", name='" << m.name << "', size=" << m.size 
                << ", transmitter='" << m.transmitter << "', signals=" << list_to_string(m.signals) << ")";
            return oss.str();
        })
        .def("__str__", [](const Message& m) {
            return py::repr(py::cast(m));
        });

    // Comment
    py::class_<Comment> comment(m, "Comment");
    comment.def(py::init<>())
           .def_readonly("type", &Comment::type)
           .def_readonly("id", &Comment::id)
           .def_readonly("name", &Comment::name)
           .def_readonly("comment", &Comment::comment)
           .def("__repr__", [](const Comment& c) {
               std::ostringstream oss;
               oss << "Comment(type=" << py::repr(py::cast(c.type)) << ", id=" << c.id 
                   << ", name='" << c.name << "', comment='" << c.comment << "')";
               return oss.str();
           })
           .def("__str__", [](const Comment& c) {
               return py::repr(py::cast(c));
           });

    py::enum_<Comment::Type>(comment, "Type")
        .value("Node", Comment::Type::Node)
        .value("Message", Comment::Type::Message)
        .value("Signal", Comment::Type::Signal)
        .value("EnvVar", Comment::Type::EnvVar)
        .value("Generic", Comment::Type::Generic)
        .export_values();

    // AttributeDefinition
    py::class_<AttributeDefinition> attr_def(m, "AttributeDefinition");
    attr_def.def(py::init<>())
            .def_readonly("object_type", &AttributeDefinition::objectType)
            .def_readonly("name", &AttributeDefinition::name)
            .def_readonly("value_type", &AttributeDefinition::valueType)
            .def_readonly("enum_values", &AttributeDefinition::enumValues)
            .def_readonly("min", &AttributeDefinition::min)
            .def_readonly("max", &AttributeDefinition::max)
            .def("__repr__", [](const AttributeDefinition& a) {
                std::ostringstream oss;
                oss << "AttributeDefinition(object_type=" << py::repr(py::cast(a.objectType)) 
                    << ", name='" << a.name << "', value_type='" << a.valueType 
                    << "', enum_values=" << list_to_string(a.enumValues) 
                    << ", min=" << a.min << ", max=" << a.max << ")";
                return oss.str();
            })
            .def("__str__", [](const AttributeDefinition& a) {
                return py::repr(py::cast(a));
            });

    py::enum_<AttributeDefinition::ObjectType>(attr_def, "ObjectType")
        .value("Node", AttributeDefinition::ObjectType::Node)
        .value("Message", AttributeDefinition::ObjectType::Message)
        .value("Signal", AttributeDefinition::ObjectType::Signal)
        .value("EnvVar", AttributeDefinition::ObjectType::EnvVar)
        .value("NodeSignalRel", AttributeDefinition::ObjectType::NodeSignalRel)
        .value("NodeEvRel", AttributeDefinition::ObjectType::NodeEvRel)
        .value("NodeBoRel", AttributeDefinition::ObjectType::NodeBoRel)
        .value("None", AttributeDefinition::ObjectType::None)
        .export_values();

    // AttributeValue
    py::class_<AttributeValue> attr_val(m, "AttributeValue");
    attr_val.def(py::init<>())
            .def_readonly("name", &AttributeValue::name)
            .def_readonly("object_type", &AttributeValue::objectType)
            .def_readonly("object_name", &AttributeValue::objectName)
            .def_readonly("message_id", &AttributeValue::messageId)
            .def_readonly("second_object_name", &AttributeValue::secondObjectName)
            .def_readonly("value", &AttributeValue::value)
            .def("__repr__", [](const AttributeValue& a) {
                std::ostringstream oss;
                oss << "AttributeValue(name='" << a.name << "', object_type=" << py::repr(py::cast(a.objectType)) 
                    << ", object_name='" << a.objectName << "', message_id=" << a.messageId 
                    << ", second_object_name='" << a.secondObjectName << "', value='" << a.value << "')";
                return oss.str();
            })
            .def("__str__", [](const AttributeValue& a) {
                return py::repr(py::cast(a));
            });

    py::enum_<AttributeValue::ObjectType>(attr_val, "ObjectType")
        .value("Node", AttributeValue::ObjectType::Node)
        .value("Message", AttributeValue::ObjectType::Message)
        .value("Signal", AttributeValue::ObjectType::Signal)
        .value("EnvVar", AttributeValue::ObjectType::EnvVar)
        .value("NodeSignalRel", AttributeValue::ObjectType::NodeSignalRel)
        .value("NodeEvRel", AttributeValue::ObjectType::NodeEvRel)
        .value("NodeBoRel", AttributeValue::ObjectType::NodeBoRel)
        .value("None", AttributeValue::ObjectType::None)
        .export_values();

    // EnvironmentVariable
    py::class_<EnvironmentVariable>(m, "EnvironmentVariable")
        .def(py::init<>())
        .def_readonly("name", &EnvironmentVariable::name)
        .def_readonly("type", &EnvironmentVariable::type)
        .def_readonly("min", &EnvironmentVariable::min)
        .def_readonly("max", &EnvironmentVariable::max)
        .def_readonly("unit", &EnvironmentVariable::unit)
        .def_readonly("initial_value", &EnvironmentVariable::initialValue)
        .def_readonly("id", &EnvironmentVariable::id)
        .def_readonly("access_nodes", &EnvironmentVariable::accessNodes)
        .def("__repr__", [](const EnvironmentVariable& e) {
            std::ostringstream oss;
            oss << "EnvironmentVariable(name='" << e.name << "', type=" << e.type 
                << ", min=" << e.min << ", max=" << e.max << ", unit='" << e.unit 
                << "', initial_value=" << e.initialValue << ", id=" << e.id 
                << ", access_nodes=" << list_to_string(e.accessNodes) << ")";
            return oss.str();
        })
        .def("__str__", [](const EnvironmentVariable& e) {
            return py::repr(py::cast(e));
        });

    // SignalGroup
    py::class_<SignalGroup>(m, "SignalGroup")
        .def(py::init<>())
        .def_readonly("message_id", &SignalGroup::messageId)
        .def_readonly("name", &SignalGroup::name)
        .def_readonly("value", &SignalGroup::value)
        .def_readonly("signals", &SignalGroup::signals)
        .def("__repr__", [](const SignalGroup& s) {
            std::ostringstream oss;
            oss << "SignalGroup(message_id=" << s.messageId << ", name='" << s.name 
                << "', value=" << s.value << ", signals=" << list_to_string(s.signals) << ")";
            return oss.str();
        })
        .def("__str__", [](const SignalGroup& s) {
            return py::repr(py::cast(s));
        });

    // SignalExtendedValueType
    py::class_<SignalExtendedValueType>(m, "SignalExtendedValueType")
        .def(py::init<>())
        .def_readonly("message_id", &SignalExtendedValueType::messageId)
        .def_readonly("signal_name", &SignalExtendedValueType::signalName)
        .def_readonly("value_type", &SignalExtendedValueType::valueType)
        .def("__repr__", [](const SignalExtendedValueType& s) {
            std::ostringstream oss;
            oss << "SignalExtendedValueType(message_id=" << s.messageId 
                << ", signal_name='" << s.signalName << "', value_type=" << s.valueType << ")";
            return oss.str();
        })
        .def("__str__", [](const SignalExtendedValueType& s) {
            return py::repr(py::cast(s));
        });

    // MessageTransmitter
    py::class_<MessageTransmitter>(m, "MessageTransmitter")
        .def(py::init<>())
        .def_readonly("message_id", &MessageTransmitter::messageId)
        .def_readonly("transmitters", &MessageTransmitter::transmitters)
        .def("__repr__", [](const MessageTransmitter& m) {
            std::ostringstream oss;
            oss << "MessageTransmitter(message_id=" << m.messageId 
                << ", transmitters=" << list_to_string(m.transmitters) << ")";
            return oss.str();
        })
        .def("__str__", [](const MessageTransmitter& m) {
            return py::repr(py::cast(m));
        });

    // DbcFile
    py::class_<DbcFile> dbc_file(m, "DbcFile");
    dbc_file.def(py::init<>())
            .def_readonly("filename", &DbcFile::filename)
            .def_readonly("version", &DbcFile::version)
            .def_readonly("new_symbols", &DbcFile::newSymbols)
            .def_readonly("nodes", &DbcFile::nodes)
            .def_readonly("value_tables", &DbcFile::valueTables)
            .def_readonly("messages", &DbcFile::messages)
            .def_readonly("comments", &DbcFile::comments)
            .def_readonly("attribute_definitions", &DbcFile::attributeDefinitions)
            .def_readonly("attribute_defaults", &DbcFile::attributeDefaults)
            .def_readonly("attribute_values", &DbcFile::attributeValues)
            .def_readonly("environment_variables", &DbcFile::environmentVariables)
            .def_readonly("signal_groups", &DbcFile::signalGroups)
            .def_readonly("signal_extended_value_types", &DbcFile::signalExtendedValueTypes)
            .def_readonly("message_transmitters", &DbcFile::messageTransmitters)
            .def("__repr__", [](const DbcFile& d) {
                std::ostringstream oss;
                oss << "DbcFile(filename='" << d.filename << "', version='" << d.version 
                    << "', nodes=" << list_to_string(d.nodes) 
                    << ", messages_count=" << d.messages.size() << ")";
                return oss.str();
            })
            .def("__str__", [](const DbcFile& d) {
                return py::repr(py::cast(d));
            });

    // DbcParser
    py::class_<DbcParser>(m, "DbcParser")
        .def(py::init<const std::string&>(), py::arg("filename") = "")
        .def("parse", &DbcParser::parse)
        .def("set_trace", &DbcParser::setTrace)
        .def("get_diagnostics", &DbcParser::getDiagnostics);
}
