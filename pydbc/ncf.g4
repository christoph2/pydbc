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

grammar ncf;

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
node_capability_file;
LIN_language_version = "2.2"
node step_motor {
  general {
    LIN_protocol_version = "2.2";
    supplier = 0x0005;
    function = 0x0020;
    variant = 1;
    bitrate = automatic min 10 kbps max 20 kbps;
    sends_wake_up_signal = "yes";
  }
  diagnostic {
    NAD = 1 to 3;
    diagnostic_class = 2;
    P2_min = 100 ms; ST_min = 40 ms;
    support_sid { 0xB0, 0xB2, 0xB7 };
  }
  frames {
    publish node_status {
      length = 4; min_period = 10 ms; max_period = 100 ms;
      signals {
        state       {size = 8; init_value = 0; offset = 0;}
        fault_state {size = 2; init_value = 0; offset = 9; fault_enc;}
        error_bit   {size = 1; init_value = 0; offset = 8;}
        angle       {size = 16; init_value = {0x22, 0x11}; offset = 16;}
      }
    }
    subscribe control {
      length = 1; max_period = 100 ms;
      signals {
        command {size = 8; init_value = 0; offset = 0; position;}
      }
    }
  }
  encoding {
    position {physical_value 0, 199, 1.8, 0, "deg";}
    fault_enc {logical_value, 0, "no result";
               logical_value, 1, "failed";
               logical_value, 2, "passed";}
  }
  status_management { response_error = error_bit;
                      fault_state_signals = fault_state; }
  free_text { "step_motor signal values outside 0 - 199 are ignored" }
}
*/

toplevel:
    'node_capability_file' ';'
    v = language_version
    (nodes += node_definition)*
    ;

language_version:
    'LIN_language_version' '=' s = stringValue ';'
    ;

node_definition:
    'node' name = node_name '{'
        g = general_definition
        d = diagnostic_definition
        f = frame_definition
        e = encoding_definition?     // Not 2.0
        s = status_management
        t = free_text_definition?
    '}'
    ;

node_name:
    i = identifierValue
    ;

general_definition:
    'general' '{'
        'LIN_protocol_version' '=' pv = protocol_version ';'
        'supplier' '=' sup = supplier_id ';'
        'function' '=' fun = function_id ';'
        'variant' '=' var = variant_id ';'
        'bitrate' '=' br = bitrate_definition ';'
        ('sends_wake_up_signal' '=' tf = ('yes' | 'no') ';')? // Not 2.0
        ('volt_range' '=' vfrom = number ',' vto = number ';')? // optional in 2.0
        ('temp_range' '=' tfrom = number ',' tto = number ';')? // optional in 2.0
        ('conformance' '=' conf = stringValue ';')? // optional in 2.0
    '}'
    ;

protocol_version:
    s = stringValue
    ;

supplier_id:
    i = intValue
    ;

function_id:
    i = intValue
    ;

variant_id:
    i = intValue
    ;

bitrate_definition:
      ('automatic' ('min' minBr = bitrate)? ('max' maxBr = bitrate)? )
    | ('select' '{' rates += bitrate (',' rates += bitrate)* '}')
    | br = bitrate
    ;

bitrate:
    n = number 'kbps'
    ;

diagnostic_definition:
    'diagnostic' '{'
        'NAD' '=' lhs = intValue (('to' rhs = intValue) | (',' nads += intValue)*) ';' // Range (to) new in 2.2
        ('diagnostic_class' '=' dc = intValue ';')? // Required in 2.2
        ('P2_min' '=' p2Min = number 'ms' ';')?
        ('ST_min' '=' stMin = number 'ms' ';')?
        ('N_As_timeout' '=' nAs = number 'ms' ';')? // New in 2.2
        ('N_Cr_timeout' '=' nCr = number 'ms' ';')? // New in 2.2
        ('support_sid' '{' sids += intValue (',' sids += intValue)* '}' ';')?
        ('max_message_length' '=' mml = intValue ';')?
    '}'
    ;

frame_definition:
    'frames' '{'
        (frames += single_frame)*
    '}'
    ;

single_frame:
    n = frame_kind frame_name '{'
        p = frame_properties
        s = signal_definition?
    '}'
    ;

frame_kind:
    v = ('publish' | 'subscribe')
    ;

frame_name:
    i = identifierValue
    ;

frame_properties:
    // message_ID = intValue ';' // Required in 2.0
    'length' '=' l = intValue ';'
    ('min_period' '=' minValue = intValue 'ms' ';')?
    ('max_period' '=' maxValue = intValue 'ms' ';')?
    ('event_triggered_frame' '=' etf = identifierValue)?
    ;

signal_definition:
    'signals' '{'
        (items += signal_definition_entry)*
    '}'
    ;

signal_definition_entry:
    n = signal_name '{' p = signal_properties '}'
    ;

signal_name:
    i = identifierValue
    ;

signal_properties:
    init = init_value ';'
    'size' '=' s = intValue ';'
    'offset' '=' o = intValue ';'
    (e = encoding_name ';')?
    ;


init_value:
    s = init_value_scalar | a = init_value_array
    ;

init_value_scalar:
    'init_value' '=' i = intValue
    ;

init_value_array:
     'init_value' '=' '{'
        values += intValue (',' values += intValue )*
     '}'
     ;

encoding_definition:
    'encoding' '{'
        (items += encoding_definition_entry)*
    '}'
    ;

encoding_definition_entry:
    name = encoding_name '{' (items += encoding_definition_value)* '}'
    ;

encoding_definition_value:
    l = logical_value | p = physical_range | b = bcd_value | a = ascii_value
    ;

encoding_name:
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
    n = intValue
    ;

min_value:
    n = intValue
    ;

max_value:
    n = intValue
    ;

scale:
    n = number
    ;

offset:
    n = number
    ;

text_info:
    t = stringValue
    ;

status_management:
    'status_management' '{'
        'response_error' '=' r = identifierValue ';'
        ('fault_state_signals' '=' values += identifierValue (',' values += identifierValue)* ';')? // New in 2.2
    '}'
    ;

published_signal:
    s = identifierValue
    ;

free_text_definition:
    'free_text' '{'
        f = stringValue
    '}'
    ;



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


