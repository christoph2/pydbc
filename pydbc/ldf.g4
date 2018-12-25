
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

/*
LIN_description_file;
LIN_protocol_version = "2.2";
LIN_language_version = "2.2";
LIN_speed = 19.2 kbps;
Channel_name = "DB"
Nodes {
  Master: CEM, 5 ms, 0.1 ms;
  Slaves: LSM, RSM;
}
Signals {
  InternalLightsRequest: 2, 0, CEM, LSM, RSM;
  RightIntLightsSwitch: 8, 0, RSM, CEM;
  LeftIntLightsSwitch: 8, 0, LSM, CEM;
  LSMerror: 1, 0, LSM, CEM;
  RSMerror: 1, 0, RSM, CEM;
  IntTest: 2, 0, LSM, CEM;
}
Frames {
  CEM_Frm1: 0x01, CEM, 1 {
    InternalLightsRequest, 0;
  }
  LSM_Frm1: 0x02, LSM, 2 {
    LeftIntLightsSwitch, 8;
  }
  LSM_Frm2: 0x03, LSM, 1 {
    LSMerror, 0;
    IntTest, 1;
  }
  RSM_Frm1: 0x04, RSM, 2 {
    RightIntLightsSwitch, 8;
  }
  RSM_Frm2: 0x05, RSM, 1 {
    RSMerror, 0;
  }
}
Event_triggered_frames {
  Node_Status_Event : Collision_resolver, 0x06, RSM_Frm1, LSM_Frm1;
}
*/

lin_description_file:
    'LIN_description_file' ';'
    pv = lin_protocol_version_def
    lv = lin_language_version_def
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

lin_speed_def:
    'LIN_speed' '=' n = number 'kbps' ';'
    ;

channel_name_def:
    'Channel_name' '=' i = identifierValue ';'
    ;

node_def:
    'Nodes' '{'
        'Master' ':' mname = node_name ',' tb = time_base 'ms' ',' j = jitter 'ms' ';'
        'Slaves' ':' snames += node_name (',' snames += node_name)* ';'
    '}'
    ;

node_name:
    i = identifierValue
    ;

time_base:
    n = number
    ;

jitter:
    n = number
    ;

node_attributes_def:
    'Node_attributes' '{'
      (name = node_name '{'
        'LIN_protocol' '=' version = protocol_version ';'
        'configured_NAD' '=' n0 = diag_address ';'
        ('initial_NAD' '=' n1 = diag_address ';')?
        attrs = attributes_def ';'
    '}')*
    '}'
    ;

protocol_version:
    s = stringValue
    ;

diag_address:
    i = intValue
    ;

attributes_def:
    'product_id' '=' sid = supplier_id ',' fid = function_id (',' v = variant)? ';'
    'response_error' '=' sn0 = signal_name ';'
    ('fault_state_signals' '=' sn1s += signal_name (',' sn1s += signal_name)* ';')?
    ('P2_min' '=' p2Min = number 'ms' ';')?
    ('ST_min' '=' stMin = number 'ms' ';')?
    ('N_As_timeout' '=' nAs = number 'ms' ';')?
    ('N_Cr_timeout' '=' nCr = number 'ms' ';')?
    cf20 = configurable_frames_20_def | cf21 = configurable_frames_21_def
    ;

supplier_id:
    i = intValue
    ;

function_id:
    i = intValue
    ;

variant:
    i = intValue
    ;

signal_name:
    i = identifierValue
    ;

configurable_frames_20_def:
    'configurable_frames' '{'
        (fname = frame_name '=' mid = message_id ';')*
    '}'
    ;

message_id:
    i = intValue
    ;

configurable_frames_21_def:
    'configurable_frames' '{'
        (fnames += frame_name ';')*
    '}'
    ;

node_composition_def:
    'composite' '{'
        ('configuration' cname = configuration_name '{'
            (cnode = composite_node '{' lnodes += logical_node (',' lnodes += logical_node)* ';')*
        '}')*
    '}'
    ;

configuration_name:
    i = identifierValue
    ;

composite_node:
    i = identifierValue
    ;

logical_node:
    i = identifierValue
    ;

signal_def:
    'Signals' '{'
        (sname = signal_name ':' ssize = signal_size ',' initValue = init_value ',' pub = published_by (',' sub += subscribed_by)* ';')*
    '}'
    ;

signal_size:
    i = intValue
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

published_by:
    i = identifierValue
    ;

subscribed_by:
    i = identifierValue
    ;

diagnostic_signal_def:
    'Diagnostic_signals' '{'
        (i10 = identifierValue ':' i11 = intValue ',' i12 = intValue ';')*
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

signal_groups_def:
    'Signal_groups' '{'
        (sgname = signal_group_name ':' gsize = group_size '{'
            (sname = signal_name ',' goffs = group_offset ';')*
        '}')*
    '}'
    ;

signal_group_name:
    i = identifierValue
    ;

group_size:
    i = intValue
    ;

group_offset:
    i = intValue
    ;

frame_def:
    'Frames' '{'
        (fname = frame_name ':' fid = frame_id ',' p = published_by ',' fsize = frame_size '{'
          (sname = signal_name ',' soffs = signal_offset ';')*
        '}')*
    '}'
    ;

frame_name:
    i = identifierValue
    ;

frame_id:
    i = intValue
    ;

frame_size:
    i = intValue
    ;

signal_offset:
    i = intValue
    ;

sporadic_frame_def:
    'Sporadic_frames' '{'
        (sfn = sporadic_frame_name ':' names += frame_name (',' names += frame_name)* ';')*
    '}'
    ;

sporadic_frame_name:
    i = identifierValue
    ;

event_triggered_frame_def:
    'Event_triggered_frames' '{'
        (e = event_trig_frm_name ':' c = collision_resolving_schedule_table ',' fid = frame_id (',' frame_name ';')* )*
    '}'
    ;

event_trig_frm_name:
    i = identifierValue
    ;

collision_resolving_schedule_table:
    i = identifierValue
    ;

diag_frame_def:
    'Diagnostic_frames' '{'
        'MasterReq' ':' m = intValue '{'
            (i10 = identifierValue ',' i11 = intValue ';')*
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
        'SlaveResp' ':' s = intValue '{'
            (i20 = identifierValue ',' i21 = intValue ';')*
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

schedule_table_def:
    'Schedule_tables' '{'
        (s = schedule_table_name  '{' (c = command 'delay' f = frame_time 'ms' ';')*  '}')*
    '}'
    ;

schedule_table_name:
    i = identifierValue
    ;

command:
      frameName = frame_name
    |  c = 'MasterReq'
    | c = 'SlaveResp'
    | c = 'AssignNAD' '{' nodeName = node_name '}'
    | c = 'ConditionalChangeNAD' '{' nad = intValue ',' id_ = intValue ',' byte_ = intValue ',' mask = intValue ',' inv = intValue ',' new_NAD = intValue'}'
    | c = 'DataDump'  '{' nodeName = node_name ',' d1 = intValue ',' d2 = intValue ',' d3 = intValue ',' d4 = intValue ',' d5 = intValue'}'
    | c = 'SaveConfiguration' '{' nodeName = node_name '}'
    | c = 'AssignFrameIdRange' '{' nodeName = node_name ',' frameIndex = frame_index (',' pids += frame_PID ',' pids += frame_PID ',' pids += frame_PID ',' pids += frame_PID)? '}'
    | c = 'FreeFormat' '{' d1 = intValue ',' d2 = intValue ',' d3 = intValue ',' d4 = intValue ',' d5 = intValue ',' d6 = intValue ','
        d7 = intValue ',' d8 = intValue '}'
    | c = 'AssignFrameId' '{' nodeName = node_name ',' frameName = frame_name  '}'
    ;

frame_index:
    i = intValue
    ;

frame_PID:
    i = intValue
    ;

frame_time:
    n = number
    ;


signal_encoding_type_def:
    'Signal_encoding_types' '{'
        (s = signal_encoding_type_name '{'
            (l = logical_value | p = physical_range | b = bcd_value | a = ascii_value)*
        '}')*
    '}'
    ;

signal_encoding_type_name:
    i = identifierValue
    ;

logical_value:
    'logical_value' ',' s = signal_value (',' t = text_info)? ';'
    ;

physical_range:
    'physical_value' ',' minValue = min_value ',' maxValue = max_value ',' s = scale ',' o = offset (',' t = text_info)? ';'
    ;

bcd_value:
    'bcd_value' ';'
    ;

ascii_value:
    'ascii_value' ';'
    ;

signal_value:
    i = intValue
    ;

min_value:
    i = intValue
    ;

max_value:
    i = intValue
    ;

scale:
    n = number
    ;

offset:
    n = number
    ;

text_info:
    s = stringValue
    ;

signal_representation_def:
    'Signal_representation' '{'
        ( enc = signal_encoding_type_name ':' names += signal_name (',' names += signal_name)* ';')*
    '}'
    ;


/*
**
**  Lexer.
**
*/
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

COMMENT
    :   ('//' ~('\n'|'\r')* '\r'? '\n'
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



