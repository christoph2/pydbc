#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2020 by Christoph Schueler <cpu12.gems.googlemail.com>

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
"""
__author__  = 'Christoph Schueler'
__version__ = '0.1.0'


from sqlalchemy.sql.expression import literal, bindparam

from pydbc.logger import Logger
from pydbc import parser
from pydbc.types import AttributeType, BusType, CategoryType, ValueType
from pydbc.db.model import (
    Dbc_Version, Message, Message_Signal, Network, Node, Signal, Value_Description,
    Valuetable, EnvironmentVariablesData, EnvVar, Attribute_Definition, Attribute_Value,
    Node_TxMessage, Node_RxSignal, Category_Definition, Category_Value, AttributeRel_Value,
    Signal_Group_Signal, Signal_Group, Node_TxSig, LinSignalEncodingType, LinSignalEncodingEntry_Value,
    LinSignalEncodingEntry_Logical, LinSignalEncodingEntry_Physical, LinSignalRepresentation,
    LinScheduleTable, LinScheduleTable_Command_Frame, LinScheduleTable_Command_MasterReq,
    LinScheduleTable_Command_SlaveResp, LinScheduleTable_Command_AssignNad,
    LinScheduleTable_Command_ConditionalChangeNad, LinScheduleTable_Command_DataDump,
    LinScheduleTable_Command_SaveConfiguration, LinScheduleTable_Command_AssignFrameIdRange,
    LinScheduleTable_Command_FreeFormat, LinScheduleTable_Command_AssignFrameId, LinSporadicFrame,
    LinUnconditionalFrame, LinEventTriggeredFrame, LinConfigurableFrame, LinFaultStateSignal,
    Vndb_Protocol
)


class NcfListener(parser.BaseListener):

    def __init__(self, database, logLevel = 'INFO', *args, **kws):
        super(NcfListener, self).__init__(database, logLevel, *args, **kws)
        self.logger = Logger(__name__, level = logLevel)
        #self.bake_queries()

    def exitToplevel(self, ctx):
        v = ctx.v.value
        nodes = [x.value for x in ctx.nodes]
        self.value = dict(version = v, nodes = nodes)

    def exitLanguage_version(self, ctx):
        s = ctx.s.value if ctx.s else None
        ctx.value = s

    def exitNode_definition(self, ctx):
        name = ctx.name.value
        g = ctx.g.value if ctx.g else None
        d = ctx.d.value if ctx.d else None
        f = ctx.f.value if ctx.d else None
        e = ctx.e.value if ctx.e else None
        s = ctx.s.value if ctx.s else None
        t = ctx.t.value if ctx.t else None
        ctx.value = dict(name = name, general = g, diagnostic = d, frames= f, encodings = e, status = s, freeText = t)

    def exitNode_name(self, ctx):
        ctx.value = ctx.i.value

    def exitGeneral_definition(self, ctx):
        pv = ctx.pv.value
        sup = ctx.sup.value
        fun = ctx.fun.value
        var = ctx.var.value
        br = ctx.br.value
        tf = True if ctx.tf.text == "yes" else False
        vfrom = ctx.vfrom.value if ctx.vfrom else None
        vto = ctx.vto.value if ctx.vto else None
        tfrom = ctx.tfrom.value if ctx.tfrom else None
        tto = ctx.tto.value if ctx.tto else None
        conf = ctx.conf.value if ctx.conf else None
        ctx.value = dict(
            protocolVersion = pv, supplier = sup, function = fun, variant = var, bitrate = br, wakeupSignal = tf,
            voltageFrom = vfrom, voltageTo = vto, temperatureFrom = tfrom, temperatureTo = tto, conformance = conf,
        )

    def exitProtocol_version(self, ctx):
        ctx.value = ctx.s.value

    def exitSupplier_id(self, ctx):
        ctx.value = ctx.i.value

    def exitFunction_id(self, ctx):
        ctx.value = ctx.i.value

    def exitVariant_id(self, ctx):
        ctx.value = ctx.i.value

    def exitBitrate_definition(self, ctx):
        rates = br = minBr = maxBr = None
        if ctx.rates:
            rates = [x.value for x in ctx.rates]
        elif ctx.br:
            br = ctx.br.value
        else:
            minBr = ctx.minBr.value
            maxBr = ctx.maxBr.value
        ctx.value = dict(bitrate = br, minBr = minBr, maxBr = maxBr, rates = rates)

    def exitBitrate(self, ctx):
        ctx.value = ctx.n.value

    def exitDiagnostic_definition(self, ctx):
        lhs = ctx.lhs.value
        rhs = ctx.rhs.value if ctx.rhs else None
        nads = [x.value for x in ctx.nads] if ctx.nads else []
        dc = ctx.dc.value if ctx.dc else None
        p2Min = ctx.p2Min.value if ctx.p2Min else None
        stMin = ctx.stMin.value if ctx.p2Min else None
        nAs = ctx.nAs.value if ctx.nAs else None
        nCr = ctx.nCr.value if ctx.nCr else None
        sids = [x.value for x in ctx.sids] if ctx.sids else []
        mml = ctx.mml.value if ctx.mml else None
        ctx.value = dict(
            maxMessageLength = mml, lhs = lhs, rhs = rhs, nads = nads, diagnosticClass = dc, p2Min = p2Min, stMin = stMin, nAs = nAs, nCr = nCr, supportedSids = sids
        )

    def exitFrame_definition(self, ctx):
        frames = [x.value for x in ctx.frames]
        ctx.value = frames

    def exitSingle_frame(self, ctx):
        n = ctx.n.value
        p = ctx.p.value if ctx.p else None
        s = ctx.s.value if ctx.s else None
        ctx.value = dict(name = n, properties = p, signal = s)

    def exitFrame_kind(self, ctx):
        text = ctx.v.text
        ctx.value = text

    def exitFrame_name(self, ctx):
        name = ctx.i.value
        ctx.value = name

    def exitFrame_properties(self, ctx):
        l = ctx.l.value
        minValue = ctx.minValue.value if ctx.minValue else None
        maxValue = ctx.maxValue.value if ctx.maxValue else None
        etf = ctx.etf.value if ctx.etf else None
        ctx.value = dict(length = l, minPeriod = minValue, maxPeriod = maxValue, eventTriggeredFrame = etf)

    def exitSignal_definition(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitSignal_definition_entry(self, ctx):
        n = ctx.n.value
        p = ctx.p.value if ctx.p else None
        ctx.value = dict(name = n, properties = p)

    def exitSignal_name(self, ctx):
        name = ctx.i.value
        ctx.value = name

    def exitSignal_properties(self, ctx):
        init = ctx.init.value
        s = ctx.s.value
        o = ctx.o.value if ctx.o else None
        e = ctx.e.value if ctx.e else None
        ctx.value = dict(initValue = init, size = s, offset = o, encoding = e)

    def exitInit_value(self, ctx):
        scalar = ctx.s.value if ctx.s else None
        array = ctx.a.value if ctx.a else None
        ctx.value = dict(scalar = scalar, array = array)

    def exitInit_value_scalar(self, ctx):
        ctx.value = ctx.i.value

    def exitInit_value_array(self, ctx):
        ctx.value = [x.value for x in ctx.values]

    def exitEncoding_definition(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitEncoding_definition_entry(self, ctx):
        name = ctx.name.value
        items = [x.value for x in ctx.items]
        ctx.value = dict(name = name, values = items)

    def exitEncoding_definition_value(self, ctx):
        if ctx.l:
            value = ctx.l.value
            vtype = "logical"
        elif ctx.p:
            value = ctx.p.value
            vtype = "range"
        elif ctx.b:
            value = None
            vtype = "bcd"
        elif ctx.a:
            value = None
            vtype = "ascii"
        ctx.value = dict(value = value, valueType = vtype)

    def exitSignal_encoding_type_name(self, ctx):
        ctx.value = ctx.i.value

    def exitEncoding_name(self, ctx):
        ctx.value = ctx.i.value

    def exitLogical_value(self, ctx):
        s = ctx.s.value
        t = ctx.t.value if ctx.t else None
        ctx.value = dict(signalValue = s, text = t)

    def exitPhysical_range(self, ctx):
        #'physical_value' ',' minValue = min_value ',' maxValue = max_value ',' s = scale ',' o = offset (',' t = text_info)? ';'
        minValue = ctx.minValue.value
        maxValue = ctx.maxValue.value
        s = ctx.s.value
        o = ctx.o.value
        t = ctx.t.value if ctx.t else None
        ctx.value = dict(min = minValue, max = maxValue, scale = s, offset = o, text = t)

    def exitBcd_value(self, ctx):
        pass

    def exitAscii_value(self, ctx):
        pass

    def exitSignal_value(self, ctx):
        ctx.value = ctx.n.value

    def exitMin_value(self, ctx):
        ctx.value = ctx.n.value

    def exitMax_value(self, ctx):
        ctx.value = ctx.n.value

    def exitScale(self, ctx):
        ctx.value = ctx.n.value

    def exitOffset(self, ctx):
        ctx.value = ctx.n.value

    def exitText_info(self, ctx):
        ctx.value = ctx.t.value

    def exitStatus_management(self, ctx):
        r = ctx.r.value
        values = [x.value for x in ctx.values] if ctx.values else []
        ctx.value = dict(responseError = r, faultStateSignals = values)

    def exitPublished_signal(self, ctx):
        pass

    def exitFree_text_definition(self, ctx):
        text = ctx.f.value
        ctx.value = text
