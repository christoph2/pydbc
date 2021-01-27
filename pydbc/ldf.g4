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

grammar ldf;

/*
::=     A name on the left of the ::= is expressed using the syntax on its right
<>      Used to mark objects specified later
|       The vertical bar indicates choice. Either the left-hand side or the right hand side of the vertical bar shall appear
Bold    The text in bold is reserved - either because it is a reserved word, or mandatory punctuation
[ ]     The text between the square brackets shall appear once or multiple times
( )     The text between the parenthesis are optional, i.e. shall appear once or zero times char_string
char_string         Any character string enclosed in quotes "like this" identifier
identifier          An identifier. Typically used to name objects. Identifiers shall follow the normal C rules for variable declaration
integer             An integer. Integers can be in decimal or hexadecimal (prefixed with 0x) format.
real_or_integer     A real or integer number. A real number is always in decimal and has an embedded decimal point.
*/
lin_description_file:
    'LIN_description_file' ';'
    pv = lin_protocol_version_def
    lv = lin_language_version_def
    fr = lin_file_revision_def?
    ls = lin_speed_def
    cn = channel_name_def?
    ndef = node_def
    ncdef = node_composition_def?
    sdef = signal_def
    dsdef = diagnostic_signal_def?
    fdef = frame_def
    sfdef = sporadic_frame_def?
    etfdef = event_triggered_frame_def?
    dffdef = diag_frame_def?
    nadef = node_attributes_def
    stdef = schedule_table_def
    sgdef = signal_groups_def?
    setdef = signal_encoding_type_def?
    srdef = signal_representation_def?
    ;

lin_protocol_version_def:
    'LIN_protocol_version' '='  s = stringValue ';'
    ;

lin_language_version_def:
    'LIN_language_version' '=' s = stringValue ';'
    ;

lin_file_revision_def:
    'LDF_file_revision' '=' s = stringValue ';' // ISO17987
    ;

lin_speed_def:
    'LIN_speed' '=' n = number 'kbps' ';'
    ;

channel_name_def:
    'Channel_name' '=' i = identifierValue ';'
    ;

node_def:
    'Nodes' '{'
        'Master' ':' mname = identifierValue ',' tb = number 'ms' ',' j = number 'ms'
        (',' bit_length = number 'bits' ',' tolerant = number '%')? // Only SAE J2602.
        ';'
        'Slaves' ':' snames += identifierValue (',' snames += identifierValue)* ';'
    '}'
    ;

node_attributes_def:
    'Node_attributes' '{'
      (items += node_attribute)*
    '}'
    ;

node_attribute:
      name = identifierValue '{'
        'LIN_protocol' '=' version = stringValue ';'
        'configured_NAD' '=' n0 = intValue ';'
        ('initial_NAD' '=' n1 = intValue ';')?
        attrs = attributes_def
    '}'
    ;

attributes_def:
    'product_id' '=' sid = intValue ',' fid = intValue (',' v = intValue)? ';'
    'response_error' '=' sn0 = identifierValue ';'
    ('fault_state_signals' '=' sn1s += identifierValue (',' sn1s += identifierValue)* ';')?
    ('P2_min' '=' p2Min = number 'ms' ';')?
    ('ST_min' '=' stMin = number 'ms' ';')?
    ('N_As_timeout' '=' nAs = number 'ms' ';')?
    ('N_Cr_timeout' '=' nCr = number 'ms' ';')?
    cf = configurable_frames?
    ('response_tolerance' '=' response_tolerance = number '%' ';')?
    ;


configurable_frames:
    'configurable_frames' '{'
        (frames += configurable_frame)*
    '}'
    ;

configurable_frame:
    fname = identifierValue ('=' mid = intValue)? ';' // Note: optional part is required for LIN < 2.1 -- TODO: syn. predicate!
    ;

node_composition_def:
    'composite' '{'
        (items += configuration)*
    '}'
    ;

configuration:
    'configuration' cname = identifierValue '{'
        (items += configuration_item)*
    '}'
    ;

configuration_item:
    cnode = identifierValue '{' lnodes += identifierValue (',' lnodes += identifierValue)* '}'
    ;

signal_def:
    'Signals' '{'
        (items += signal_item)*
    '}'
    ;

signal_item:
    sname = identifierValue ':' ssize = intValue ',' initValue = init_value ',' pub = identifierValue (',' sub += identifierValue)* ';'
    ;

init_value:
    s = init_value_scalar | a = init_value_array
    ;

init_value_scalar:
    i = intValue
    ;

init_value_array:
    '{'
        vs += intValue (',' vs += intValue)*
    '}'
    ;

diagnostic_signal_def:
    'Diagnostic_signals' '{'
        (items += diagnostic_item)*
/*
        MasterReqB0: 8, 0 ;
        MasterReqB1: 8, 0 ;
        MasterReqB2: 8, 0 ;
        MasterReqB3: 8, 0 ;
        MasterReqB4: 8, 0 ;
        MasterReqB5: 8, 0 ;
        MasterReqB6: 8, 0 ;
        MasterReqB7: 8, 0 ;
        SlaveRespB0: 8, 0 ;
        SlaveRespB1: 8, 0 ;
        SlaveRespB2: 8, 0 ;
        SlaveRespB3: 8, 0 ;
        SlaveRespB4: 8, 0 ;
        SlaveRespB5: 8, 0 ;
        SlaveRespB6: 8, 0 ;
        SlaveRespB7: 8, 0 ;
*/
    '}'
    ;

diagnostic_item:
    name = identifierValue ':' size = init_value ',' initValue = init_value ';'
    ;

signal_groups_def:
    'Signal_groups' '{'
        (items += signal_group)*
    '}'
    ;

signal_group:
    // Signal groups are deprecated.
    sgname = identifierValue ':' gsize = intValue '{' (items += signal_group_item)*
    '}'
    ;

signal_group_item:
    sname = identifierValue ',' goffs = intValue ';'
    ;

frame_def:
    'Frames' '{'
        (items += frame_item)*
    '}'
    ;

frame_item:
    fname = identifierValue ':' fid = intValue ',' p = identifierValue ',' fsize = intValue '{' (items += frame_signal)* '}'
    ;

frame_signal:
    sname = identifierValue ',' soffs = intValue ';'
    ;

sporadic_frame_def:
    'Sporadic_frames' '{'
        (items += sporadic_frame_item)*
    '}'
    ;

sporadic_frame_item:
    sfn = identifierValue ':' names += identifierValue (',' names += identifierValue)* ';'
    ;

event_triggered_frame_def:
    'Event_triggered_frames' '{'
        (items += event_triggered_frame_item)*
    '}'
    ;

event_triggered_frame_item:
    e = identifierValue ':' c = identifierValue ',' fid = intValue (',' items += identifierValue)* ';'
    ;

diag_frame_def:
    'Diagnostic_frames' '{'
        'MasterReq' ':' mid = intValue '{'
            (mitems += diag_frame_item)*
/*
          MasterReqB0, 0;
          MasterReqB1, 8;
          MasterReqB2, 16;
          MasterReqB3, 24;
          MasterReqB4, 32;
          MasterReqB5, 40;
          MasterReqB6, 48;
          MasterReqB7, 56;
*/
        '}'
        'SlaveResp' ':' sid = intValue '{'
            (sitems += diag_frame_item)*
/*
          SlaveRespB0, 0;
          SlaveRespB1, 8;
          SlaveRespB2, 16;
          SlaveRespB3, 24;
          SlaveRespB4, 32;
          SlaveRespB5, 40;
          SlaveRespB6, 48;
          SlaveRespB7, 56;
*/
        '}'
    '}'
    ;

diag_frame_item:
    sname = identifierValue ',' soffs = intValue ';'
    ;

schedule_table_def:
    'Schedule_tables' '{'
        (items += schedule_table_entry)*
    '}'
    ;

schedule_table_entry:
    s = identifierValue  '{' (items += schedule_table_command)*  '}'
    ;

schedule_table_command:
    c = command 'delay' f = number 'ms' ';'
    ;

command:
      frameName = identifierValue
    |  c = 'MasterReq'
    | c = 'SlaveResp'
    | c = 'AssignNAD' '{' nodeName = identifierValue '}'
    | c = 'ConditionalChangeNAD' '{' nad = intValue ',' id_ = intValue ',' byte_ = intValue ',' mask = intValue ',' inv = intValue ',' new_NAD = intValue'}'
    | c = 'DataDump'  '{' nodeName = identifierValue ',' d1 = intValue ',' d2 = intValue ',' d3 = intValue ',' d4 = intValue ',' d5 = intValue'}'
    | c = 'SaveConfiguration' '{' nodeName = identifierValue '}'
    | c = 'AssignFrameIdRange' '{' nodeName = identifierValue ',' frameIndex = intValue (',' pids += intValue ',' pids += intValue ',' pids += intValue ',' pids += intValue)? '}'
    | c = 'FreeFormat' '{' d1 = intValue ',' d2 = intValue ',' d3 = intValue ',' d4 = intValue ',' d5 = intValue ',' d6 = intValue ','
        d7 = intValue ',' d8 = intValue '}'
    | c = 'AssignFrameId' '{' nodeName = identifierValue ',' frName = identifierValue  '}'
    ;

signal_encoding_type_def:
    'Signal_encoding_types' '{'
        (items += signal_encoding_entry)*
    '}'
    ;

signal_encoding_entry:
    s = identifierValue '{'
        (items += signal_encoding_value)*
    '}'
    ;

signal_encoding_value:
    l = logical_value | p = physical_range | b = bcd_value | a = ascii_value
    ;

logical_value:
    'logical_value' ',' s = intValue (',' t = stringValue)? ';'
    ;

physical_range:
    'physical_value' ',' minValue = intValue ',' maxValue = intValue ',' s = number ',' o = number (',' t = stringValue)? ';'
    ;

bcd_value:
    'bcd_value' ';'
    ;

ascii_value:
    'ascii_value' ';'
    ;

signal_representation_def:
    'Signal_representation' '{'
        (items += signal_representation_entry)*
    '}'
    ;

signal_representation_entry:
    enc = identifierValue ':' names += identifierValue (',' names += identifierValue)* ';'
    ;

/*
**
**  Lexer.
**
*/

intValue:
    i = INT
    | h = HEX
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

HEX:
    '0'('x' | 'X') HEX_DIGIT+
    ;

fragment
HEX_DIGIT : ('0'..'9'|'a'..'f'|'A'..'F') ;

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
    (' ' | '\t' | '\r' | '\n') -> skip
    ;

COMMENT
    :   ('//' ~('\n'|'\r')* '\r'*'\n'
    |   '/*' .*? '*/')
        -> channel(HIDDEN)
    ;

STRING:
    '"' ( ESC_SEQ | ~('\\'|'"') )* '"'
    ;

SIGN:
      '+'
    | '-'
    ;

