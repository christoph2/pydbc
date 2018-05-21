/*
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2018 by Christoph Schueler <cpu12.gems.googlemail.com>

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
    version                     // VERSION
    newSymbols                  // NS_
    bitTiming                   // BS_
    nodes                       // BU_
    valueTables                 // VAL_TABLE_
    messages                    // BO_
    messageTransmitters         // BO_TX_BU_
    environmentVariables        // EV_
    environmentVariablesData    // ENVVAR_DATA_
    signalTypes                 // SGTYPE_
    comments                    // CM_
    attributeDefinitions        // BA_DEF_
    customAttributeDefinitions  // BA_DEF_REL_
    attributeDefaults           // BA_DEF_DEF_
    customAttributeDefaults     // BA_DEF_DEF_REL_
    attributeValues             // BA_
    customAttributeValues       // BA_REL_
    valueDescriptions           // VAL_

    //categoryDefinitions
    //categories
    //filter
    //signalTypeRefs
    //signalGroups

    signalExtendedValueTypeList // SIG_VALTYPE_
    ;

messageTransmitters:
    (items += messageTransmitter)*
    ;

messageTransmitter:
    'BO_TX_BU_' messageID = intValue ':' transmitter* ';'
    ;

signalExtendedValueTypeList:
     (items += signalExtendedValueType)*
    ;

signalExtendedValueType:
    'SIG_VALTYPE_' messageID = intValue signalName = C_IDENTIFIER ':' valType = intValue /*('0' | '1' | '2' | '3')*/ ';'
    ;

messages:
    (items  += message)*
    ;

message :
    ma = 'BO_' messageID = intValue messageName = C_IDENTIFIER ':' messageSize = intValue
    transmt = (C_IDENTIFIER | VECTOR_XXX) (sgs += signal)*
    ;

signal:
    ma = 'SG_' signalName = C_IDENTIFIER mind = multiplexerIndicator? ':' startBit = intValue '|' signalSize = intValue '@'
    byteOrder = intValue /*('0' | '1')*/ valueType = SIGN
    '(' factor = number ',' offset = number ')'
    '[' minimum = number '|' maximum = number ']'
    unit = STRING rcv = receiver
    ;

receiver:
    fid = (C_IDENTIFIER | VECTOR_XXX) (',' ids += C_IDENTIFIER)*
    ;

transmitter:
    (fid = C_IDENTIFIER) (',' ids += C_IDENTIFIER)*
    ;

multiplexerIndicator:
    mind = C_IDENTIFIER
    //('M' | ('m' intValue))
    ;

valueTables:
    (items += valueTable)*
    ;

valueTable:
    'VAL_TABLE_' name = C_IDENTIFIER (desc += valueDescription)* ';'
    ;

valueDescription:
    val = number name = STRING
    ;

nodes:
    'BU_' ':' (ids += C_IDENTIFIER)*
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
    'VERSION' STRING
    ;

valueDescriptions:
    (items += specializedValueDescription)*
    ;

specializedValueDescription:
    'VAL_'  (
      messageID = intValue signalName = C_IDENTIFIER (items += valueDescription)*
    |
      envVarName = C_IDENTIFIER (items += valueDescription)*
    )
    ';'
    ;

environmentVariables:
    (evs += environmentVariable)*
    ;

environmentVariable:
    'EV_' name = C_IDENTIFIER ':' varType = intValue/*('0' | '1' | '2')*/ '[' minimum  = number '|' maximum = number ']'
    unit = STRING initialValue = number envId = intValue DUMMY_NODE_VECTOR
    accNodes = accessNodes ';'
    ;

accessNodes:
      id_ = VECTOR_XXX
    | ids += C_IDENTIFIER (',' ids += C_IDENTIFIER)*
    ;

environmentVariablesData:
    (evars += environmentVariableData)*
    ;

environmentVariableData:
    'ENVVAR_DATA_' varname = C_IDENTIFIER ':' value = intValue ';'
    ;

signalTypes:
    (sigTypes += signalType)*
    ;

signalType:
    'SGTYPE_' signalTypeName = C_IDENTIFIER ':' signalSize = number '@' byteOrder = intValue valueType = SIGN
    '(' factor = number ',' offset = number ')' '[' minimum = number '|' maximum = number ']'
    unit = STRING defaultValue = number ',' valTable = C_IDENTIFIER ';'
    ;

comments:
    (items += comment)*
    ;

comment:
    'CM_'
    (
          ( 'BU_' c0 = C_IDENTIFIER)
        | ('BO_' i1 = intValue)
        | ('SG_' i2 = intValue c2= C_IDENTIFIER)
        | ('EV_' c3 = C_IDENTIFIER)
    )? s = STRING ';'
    ;

attributeDefinitions:
    (items += attributeDefinition)*
    ;

attributeDefinition:
    'BA_DEF_' objectType = ('BU_' | 'BO_' | 'SG_' | 'EV_')?   attrName = STRING  attrValue = attributeValueType ';'
    ;

customAttributeDefinitions:
    (items += customAttributeDefinition)*
    ;

customAttributeDefinition:
    'BA_DEF_REL_' objectType = ('BU_SG_REL_'| 'BU_EV_REL_'| 'BU_BO_REL_')?   attrName = STRING  attrValue = attributeValueType ';'
    ;

attributeValueType:
      'INT' i00 = intValue i01 = intValue
    | 'HEX' i10 = intValue i11 = intValue
    | 'FLOAT' f0 = number  f1 = number
    | s0 = 'STRING'
    | 'ENUM' efirst = STRING (',' eitems += STRING)*
    ;

attributeDefaults:
    (items += attributeDefault)*
    ;

attributeDefault:
    'BA_DEF_DEF_' n = STRING v = attributeValue ';'
    ;

customAttributeDefaults:
    (items += customAttributeDefault)*
    ;

customAttributeDefault:
    'BA_DEF_DEF_REL_' n = STRING v = attributeValue ';'
    ;

attributeValue:
      number
    | STRING
    ;

attributeValues:
    (items += attributeValueForObject)*
    ;

attributeValueForObject:
      'BA_' attributeName = STRING (
          attrValue = attributeValue
        | ('BU_' nodeName = C_IDENTIFIER buValue = attributeValue)
        | ('BO_' mid1 = intValue boValue = attributeValue)
        | ('SG_' mid2 = intValue signalName = C_IDENTIFIER sgValue = attributeValue)
        | ('EV_' evName = C_IDENTIFIER evValue = attributeValue)
      ) ';'
    ;

///
customAttributeValues:
    (items += customAttributeValueForObject)*
    ;

// BA_ "NWM-Stationsadresse" BU_ Console 26;
// BA_ "GenMsgAutoGenSnd" BO_ 1540 0;

// BA_REL_ "AttrNodeTx" BU_BO_REL_ Motor 1 "foo";

customAttributeValueForObject:
      'BA_REL' attributeName = STRING (
          attributeValue
        | ('BU_BO_REL_' nodeName = C_IDENTIFIER buValue = attributeValue cmValue = STRING)
        | ('BU_SG_REL_' mid2 = intValue signalName = C_IDENTIFIER sgValue = attributeValue)
        | ('BU_EV_REL_' evName = C_IDENTIFIER evValue = attributeValue)
      ) ';'
    ;
///

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

//
//      Lexer.
//
VECTOR_XXX:
    'Vector__XXX'
    ;

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

fragment
ESC_SEQ:
      '\\' (
        'b'
      | 't'
      | 'n'
      | 'f'
      | 'r'
      | '\u0022'
      | '\''
      | '\\'
    )
    ;

WS:
    (' ' | '\t' | '\r' | '\n') -> channel(HIDDEN)
    ;

STRING:
    '"' ( ESC_SEQ | ~('\\'|'"') )* '"'
    ;

SIGN:
      '+'
    | '-'
    ;



