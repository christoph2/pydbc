/*
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2021 by Christoph Schueler <cpu12.gems.googlemail.com>

   All Rights Reserved

   This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License along
   with this program; if not, write to the Free Software Foundation, Inc.,
   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

   s. FLOSS-EXCEPTION.txt
*/

grammar dbc;

dbcfile:
    version                         // VERSION
    newSymbols                      // NS_
    bitTiming                       // BS_
    nodes                           // BU_
    valueTables                     // VAL_TABLE_
    messages                        // BO_
    messageTransmitters             // BO_TX_BU_
    environmentVariables            // EV_
    environmentVariablesData        // ENVVAR_DATA_
    signalTypes                     // SGTYPE_
                                    // SGTYPE_VAL_
                                    // BA_DEF_SGTYPE_
                                    // BA_SGTYPE_
                                    // SIG_TYPE_REF_
    comments                        // CM_
    attributeDefinitions            // BA_DEF_
    relativeAttributeDefinitions    // BA_DEF_REL_
    attributeDefaults               // BA_DEF_DEF_
    relativeAttributeDefaults       // BA_DEF_DEF_REL_
    attributeValues                 // BA_
    relativeAttributeValues         // BA_REL_
    objectValueTables               // VAL_
    signalGroups                    // SIG_GROUP_
    categoryDefinitions             // CAT_DEF_
    categories                      // CAT_
    //filter
    //signalTypeRefs
    //signalGroups

    signalExtendedValueTypeList // SIG_VALTYPE_
    ;

messageTransmitters:
    (items += messageTransmitter)*
    ;

messageTransmitter:
    'BO_TX_BU_' messageID = intValue ':' tx = transmitter ';'
    ;

signalExtendedValueTypeList:
     (items += signalExtendedValueType)*
    ;

signalExtendedValueType:
    'SIG_VALTYPE_' messageID = intValue signalName = identifierValue ':' valType = intValue /*('0' | '1' | '2' | '3')*/ ';'
    ;

messages:
    (items  += message)*
    ;

message :
    ma = 'BO_' messageID = intValue messageName = identifierValue ':' messageSize = intValue
    transmt = C_IDENTIFIER (sgs += signal)*
    ;

signal:
    ma = 'SG_' signalName = identifierValue mind = multiplexerIndicator? ':' startBit = intValue '|' signalSize = intValue '@'
    byteOrder = intValue /*('0' | '1')*/ sign = SIGN
    '(' factor = number ',' offset = number ')'
    '[' minimum = number '|' maximum = number ']'
    unit = stringValue rcv = receiver
    ;

receiver:
    fid = C_IDENTIFIER  (',' ids += identifierValue)*
    ;

transmitter:
    ids += identifierValue (',' ids += identifierValue)*
    ;

multiplexerIndicator:
    mind = identifierValue
    //('M' | ('m' intValue))
    ;

valueTables:
    (items += valueTable)*
    ;

valueTable:
    'VAL_TABLE_' name = identifierValue (desc += valueDescription)* ';'
    ;

valueDescription:
    val = number name = stringValue
    ;

nodes:
    'BU_' ':' (ids += identifierValue)*
    ;

bitTiming:
    'BS_' ':' (baudrate = intValue ':' btr1 = intValue ',' btr2 = intValue)?
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
    'VERSION' vs = stringValue
    ;

objectValueTables:
    (items += objectValueTable)*
    ;

objectValueTable:
    'VAL_'  (
      messageID = intValue signalName = identifierValue (items += valueDescription)*
    |
      envVarName = identifierValue (items += valueDescription)*
    )
    ';'
    ;

environmentVariables:
    (evs += environmentVariable)*
    ;

environmentVariable:
    'EV_' name = identifierValue ':' varType = intValue/*('0' | '1' | '2')*/ '[' minimum  = number '|' maximum = number ']'
    unit = stringValue initialValue = number envId = intValue DUMMY_NODE_VECTOR
    accNodes = accessNodes ';'
    ;

accessNodes:
    items += identifierValue (',' items += identifierValue)*
    ;

environmentVariablesData:
    (evars += environmentVariableData)*
    ;

environmentVariableData:
    'ENVVAR_DATA_' varname = identifierValue ':' value = intValue ';'
    ;

signalTypes:
    (sigTypes += signalType)*
    ;

signalType:
    'SGTYPE_' signalTypeName = identifierValue ':' signalSize = number '@' byteOrder = intValue valueType = SIGN
    '(' factor = number ',' offset = number ')' '[' minimum = number '|' maximum = number ']'
    unit = stringValue defaultValue = number ',' valTable = identifierValue ';'
    ;

comments:
    (items += comment)*
    ;

comment:
    'CM_'
    (
          ( 'BU_' c0 = identifierValue)
        | ('BO_' i1 = intValue)
        | ('SG_' i2 = intValue c2= identifierValue)
        | ('EV_' c3 = identifierValue)
    )? s = stringValue ';'
    ;

attributeDefinitions:
    (items += attributeDefinition)*
    ;

attributeDefinition:
    'BA_DEF_' objectType = ('BU_' | 'BO_' | 'SG_' | 'EV_')?   attrName = stringValue  attrValue = attributeValueType ';'
    ;

relativeAttributeDefinitions:
    (items += relativeAttributeDefinition)*
    ;

relativeAttributeDefinition:
    'BA_DEF_REL_' objectType = ('BU_SG_REL_'| 'BU_EV_REL_'| 'BU_BO_REL_')?   attrName = stringValue  attrValue = attributeValueType ';'
    ;

attributeValueType:
      'INT' i00 = intValue i01 = intValue
    | 'HEX' i10 = intValue i11 = intValue
    | 'FLOAT' f0 = number  f1 = number
    | s0 = 'STRING'
    | 'ENUM' efirst = stringValue (',' eitems += stringValue)*
    ;

attributeDefaults:
    (items += attributeDefault)*
    ;

attributeDefault:
    'BA_DEF_DEF_' n = stringValue v = attributeValue ';'
    ;

relativeAttributeDefaults:
    (items += relativeAttributeDefault)*
    ;

relativeAttributeDefault:
    'BA_DEF_DEF_REL_' n = stringValue v = attributeValue ';'
    ;

attributeValue:
      n = number
    | s = stringValue
    ;

attributeValues:
    (items += attributeValueForObject)*
    ;

attributeValueForObject:
      'BA_' attributeName = stringValue (
          attrValue = attributeValue
        | ('BU_' nodeName = identifierValue buValue = attributeValue)
        | ('BO_' mid1 = intValue boValue = attributeValue)
        | ('SG_' mid2 = intValue signalName = identifierValue sgValue = attributeValue)
        | ('EV_' evName = identifierValue evValue = attributeValue)
      ) ';'
    ;

///
relativeAttributeValues:
    (items += relativeAttributeValueForObject)*
    ;

relativeAttributeValueForObject:
      'BA_REL_' attributeName = stringValue (
        (  attrType = 'BU_BO_REL_' nodeName = identifierValue nodeAddress = intValue attrValue = attributeValue)
        | (attrType = 'BU_SG_REL_' nodeName = identifierValue 'SG_' messageID = intValue signalName = identifierValue attrValue = attributeValue)
        | (attrType = 'BU_EV_REL_' nodeName = identifierValue evName = identifierValue evValue = attributeValue)  // ???
      ) ';'
    ;

signalGroups:
    (items += signalGroup)*
    ;

signalGroup:
    'SIG_GROUP_' messageID = intValue groupName = identifierValue gvalue = intValue ':'
    (signals += identifierValue)*
    ';'
    ;

categoryDefinitions:
    (items += categoryDefinition)*
    ;

categoryDefinition:
    'CAT_DEF_' cat = intValue  name = identifierValue num = intValue
    ';'
    ;

categories:
    (items += category)*
    ;

category:
    'CAT_'  (('BU_' nodeName = identifierValue)
        | ('BO_' mid1 = intValue )
        | ('EV_' evName = identifierValue))
       cat = intValue
    ';'
    ;

intValue:
    i = INT
    ;

floatValue:
    f = FLOAT
    ;

number:
     i = intValue
   | f = floatValue
   ;

stringValue:
    s = STRING
    ;

identifierValue:
    i = C_IDENTIFIER
    ;


//
//      Lexer.
//
//VECTOR_XXX:
//    'Vector__XXX'
//    ;

DUMMY_NODE_VECTOR:
    'DUMMY_NODE_VECTOR'
    ('0' .. '9')+
    ;

C_IDENTIFIER:
    ('a'..'z'|'A'..'Z'|'_') ('a'..'z'|'A'..'Z'|'0'..'9'|'_')*
    ;


fragment
EXPONENT:
    ('e'|'E') ('+'|'-')? ('0'..'9')+
    ;

FLOAT:
    SIGN?
    (
      ('0'..'9')+ '.' ('0'..'9')* EXPONENT?
    | '.' ('0'..'9')+ EXPONENT?
    | ('0'..'9')+ EXPONENT
    )
    ;


INT:
    SIGN? '0'..'9'+
    ;


WS:
    (' ' | '\t' | '\r' | '\n') -> skip
    ;

fragment
HEX_DIGIT : ('0'..'9'|'a'..'f'|'A'..'F') ;

STRING:
    '"' ( ESC_SEQ | ~('\\'|'"') )* '"'
    ;

fragment
ESC_SEQ
    :   '\\'
        (   // The standard escaped character set such as tab, newline, etc.
            [btnfr"'\\]
        |   // A Java style Unicode escape sequence
            UNICODE_ESC
        |   // Invalid escape
            .
        |   // Invalid escape at end of file
            EOF
        )
    ;

fragment
UNICODE_ESC
    :   'u' (HEX_DIGIT (HEX_DIGIT (HEX_DIGIT HEX_DIGIT?)?)?)?
;


SIGN:
      '+'
    | '-'
    ;

