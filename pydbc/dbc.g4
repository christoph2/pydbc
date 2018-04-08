
grammar dbc;

/*
tokens {
    VERSION,
    NEW_SYMBOLS,
    BIT_TIMING,
    NODES,
    VALUE_TABLES,
    MESSAGE,
    MESSAGES,
    MESSAGE_TRANSMITTER,
    MESSAGE_TRANSMITTERS,
    ENVIRONMENT_VARIABLES,
    ENVIRONMENT_VARIABLES_DATA,
    SIGNAL,
    SIGNAL_TYPES,
    COMMENTS,
    COMMENT,
    ATTRIBUTE_DEFINITION,
    ATTRIBUTE_DEFINITIONS,
    ATTRIBUTE_DEFAULTS,
    ATTRIBUTE_DEFAULT,
    ATTRIBUTE_VALUE_TYPE,
    ATTRIBUTE_VALUE_FOR_OBJECT,
    ATTRIBUTE_VALUES,
    SIGTYPE_ATTR_LIST,
    VALUE_DESCRIPTIONS,
    CATEGORY_DEFINITIONS,
    CATEGORIES,
    FILTER,
    SIGNAL_TYPE_REFS,
    SIGNAL_GROUPS,
    SIGNAL_EXTENDED_VALUE_TYPE_LIST,
    ACCESS_NODES
}
*/

dbcfile:
    version
    newSymbols
    bitTiming
    nodes
    valueTables
    messages
    messageTransmitters
    environmentVariables
    environmentVariablesData
    signalTypes
    comments
    attributeDefinitions
    attributeDefaults
    attributeValues
/*
    sigtypeAttrList

    valueDescriptions
    categoryDefinitions
    categories
    filter
    signalTypeRefs
    signalGroups
*/
    signalExtendedValueTypeList
    ;

messageTransmitters:
    messageTransmitter*
    ;

messageTransmitter:
    'BO_TX_BU_' messageID = INT ':' transmitter* ';'
    ;

signalExtendedValueTypeList:
     'SIG_VALTYPE_' messageID = INT signalName = ID valType = ('0' | '1' | '2' | '3') ';'
    ;

messages:
    message*
    ;

message :
    ma = 'BO_' messageID = INT messageName = ID ':' messageSize = INT
    transmt = (ID | VECTOR_XXX)  // gültiger Node-Name!? -- ID { isDefined($ID.text) }
    signal*
    ;

signal:
    ma = 'SG_' signalName = ID multiplexerIndicator? ':' startBit = INT '|' signalSize = INT '@'
    byteOrder valueType
    '(' factor = FLOAT ',' offset = FLOAT ')'
    '[' minimum = FLOAT '|' maximum = FLOAT ']'
    unit = STRING receiver
    ;

receiver:
    (ID | VECTOR_XXX) (',' ID)*
    ;

transmitter:
    (ID) (',' ID)*
    ;

valueType:
    '+' | '-'
    ;

byteOrder:
    '0' | '1'
    ;

multiplexerIndicator:
    ('M' | ('m' INT))
    ;

valueTables:
    valueTable*
    ;

valueTable:
    'VAL_TABLE_' ID valueDescription* ';'
    ;

valueDescription:
    number STRING
    ;

nodes:
    'BU_' ':' ID*
    ;

bitTiming:
    'BS_' ':' (baudrate = INT ':' btr1 = INT ',' btr2 = INT)?
    ;

newSymbols:
    'NS_' ':'
    (ids += ('NS_DESC_'| 'CM_'| 'BA_DEF_'| 'BA_'| 'VAL_'| 'CAT_DEF_'| 'CAT_'|
    'FILTER'| 'BA_DEF_DEF_'| 'EV_DATA_'| 'ENVVAR_DATA_'| 'SGTYPE_'|
    'SGTYPE_VAL_'| 'BA_DEF_SGTYPE_'| 'BA_SGTYPE_'| 'SIG_TYPE_REF_'|
    'VAL_TABLE_'| 'SIG_GROUP_'| 'SIG_VALTYPE_'| 'SIGTYPE_VALTYPE_'|
    'BO_TX_BU_'| 'BA_DEF_REL_'| 'BA_REL_'| 'BA_DEF_DEF_REL_'|
    'BU_SG_REL_'| 'BU_EV_REL_'| 'BU_BO_REL_'| 'SG_MUL_VAL_'))*
    ;

version:
    'VERSION' STRING
    ;

environmentVariables:
    environmentVariable*
    ;

environmentVariable:
    'EV_' ID ':' varType = ('0' | '1' | '2') '[' minimum  = FLOAT '|' maximum = FLOAT ']'
    unit = STRING initialValue = FLOAT envId = INT 'DUMMY_NODE_VECTOR'
    accessType = ('0' | '1' | '2' | '3' | '8000') accessNodes ';'
    ;

accessNodes:
      id_ = VECTOR_XXX
    | ids += ID (',' ids += ID)*
    ;

environmentVariablesData:
    environmentVariableData*
    ;

environmentVariableData:
    'ENVVAR_DATA_' ID ':' INT ';'
    ;

/*
    SIGNAL_TYPES;
*/

signalTypes:
    ;

comments:
    comment*
    ;

comment:
    'CM_'   (('BU_' ID) | ('BO_' INT) | ('SG_' INT) | ('EV_' ID))? STRING ';'
    ;

attributeDefinitions:
    attributeDefinition*
    ;

attributeDefinition:        // FEHLERHAFT!!!
    'BA_DEF_' objectType = ('BU_' | 'BO_' | 'SG_' | 'EV')? attributeName = STRING attributeValueType ';'
    ;

attributeValueType:
      'INT' l = INT r = INT
    | 'HEX' l = INT r = INT
    | 'FLOAT' l = FLOAT r = FLOAT
    | 'STRING'
    | 'ENUM' values += STRING (',' values += STRING)*
    ;

attributeDefaults:
    attributeDefault*
    ;

attributeDefault:
    'BA_DEF_DEF' ID attributeValue ';'
    ;

attributeValue:
      INT
    | FLOAT
    | STRING
    ;

attributeValues:
    attributeValueForObject*
    ;

attributeValueForObject:
      'BA_' attributeName = ID (('BU_' additional = ID)
    | ('BO_' additional = INT)
    | ('SG_' additional = INT)
    | ('EV_' additional = ID))?
    attributeValue ';'
    ;

number:
      FLOAT
    | INT
    ;

//
//      Lexer.
//
VECTOR_XXX:
    'Vector__XXX'
    ;

ID:
    ('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')*
    ;

INT:
    ('-' | '+')? '0'..'9'+
    ;

FLOAT:
      ('0'..'9')+ '.' ('0'..'9')* EXPONENT?
    | '.' ('0'..'9')+ EXPONENT?
    | ('0'..'9')+ EXPONENT
    ;

WS:
      ( ' '
    | '\t'
    | '\r'
    | '\n'
      )-> channel(HIDDEN)
    ;

STRING:
    '"' ( ESC_SEQ | ~('\\'|'"') )* '"'
    ;

CHAR:
    '\'' ( ESC_SEQ | ~('\''|'\\') ) '\''
    ;

fragment
EXPONENT:
    ('e'|'E') ('+'|'-')? ('0'..'9')+
    ;

fragment
HEX_DIGIT:
    ('0'..'9'|'a'..'f'|'A'..'F')
    ;

fragment
ESC_SEQ:
      '\\' ('b'|'t'|'n'|'f'|'r'|'\"'|'\''|'\\')
    | UNICODE_ESC
    | OCTAL_ESC
    ;

fragment
OCTAL_ESC:
      '\\' ('0'..'3') ('0'..'7') ('0'..'7')
    | '\\' ('0'..'7') ('0'..'7')
    | '\\' ('0'..'7')
    ;

fragment
UNICODE_ESC:
    '\\' 'u' HEX_DIGIT HEX_DIGIT HEX_DIGIT HEX_DIGIT
    ;

