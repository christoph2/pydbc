#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2019 by Christoph Schueler <cpu12.gems.googlemail.com>

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

from collections import namedtuple

from pydbc import parser

class LdfListener(parser.BaseListener):

    def exitLin_description_file(self, ctx):
        self.value = dict(
            protocolVersion = ctx.pv.value,
            languageVersion = ctx.lv.value,
            fileRevision = ctx.fr.value if ctx.fr else None,
            speed = ctx.ls.value,
            channelName = ctx.cn.value if ctx.cn else None,
            nodes = ctx.ndef.value,
            nodeCompositions = ctx.ncdef.value if ctx.ncdef else None,
            signals = ctx.sdef.value,
            diagnosticSignals = ctx.dsdef.value if ctx.dsdef else None,
            frames = ctx.fdef.value,
            sporadicFrames = ctx.sfdef.value if ctx.sfdef else [],
            eventTriggeredFrames = ctx.etfdef.value if ctx.etfdef else [],
            diagnosticFrames = ctx.dffdef.value if ctx.dffdef else [],
            nodeAttributes = ctx.nadef.value,
            scheduleTables = ctx.stdef.value,
            signalGroups = ctx.sgdef.value if ctx.sgdef else [],
            signalEncodings = ctx.setdef.value if ctx.setdef else [],
            signalRepresentations = ctx.srdef.value if ctx.srdef else [],
        )

    def exitLin_protocol_version_def(self, ctx):
        ctx.value = ctx.s.value

    def exitLin_language_version_def(self, ctx):
        ctx.value = ctx.s.value

    def exitLin_file_revision_def(self, ctx):
        ctx.value = ctx.s.value

    def exitLin_speed_def(self, ctx):
        ctx.value = ctx.n.value if ctx.n else None

    def exitChannel_name_def(self, ctx):
        ctx.value = ctx.i.value

    def exitNode_def(self, ctx):
        mname = ctx.mname.value
        tb = ctx.tb.value
        j = ctx.j.value
        snames = [x.value for x in ctx.snames]
        ctx.value = dict(master = mname, timeBase = tb, jitter = j, slaves = snames)

    def exitNode_attributes_def(self, ctx):
        items = [x.value for x in ctx.items]
        ctx.value = items

    def exitNode_attribute(self, ctx):
        name = ctx.name.value
        version = ctx.version.value
        n0 = ctx.n0.value if ctx.n0 else None
        n1 = ctx.n1.value if ctx.n1 else None
        attrs = ctx.attrs.value if ctx.attrs else dict()
        ctx.value = dict(name = name, version = version, configuredNAD = n0, initialNAD = n1, **attrs)

    def exitAttributes_def(self, ctx):
        sid = ctx.sid.value if ctx.sid else None
        fid = ctx.fid.value if ctx.fid else None
        v = ctx.v.value if ctx.v else None
        sn0 = ctx.sn0.value if ctx.sn0 else None
        sn1s = [x.value for x in ctx.sn1s]
        cf = ctx.cf.value if ctx.cf else None
        p2Min = ctx.p2Min.value if ctx.p2Min else None
        stMin = ctx.stMin.value if ctx.stMin else None
        nAs = ctx.nAs.value if ctx.nAs else None
        nCr = ctx.nCr.value if ctx.nCr else None
        ctx.value = dict(supplierID = sid, functionID = fid, variant = v, responseErrorSignal = sn0, faultStateSignals = sn1s,
            p2Min = p2Min, stMin = stMin, nAs = nAs, nCr = nCr, configurableFrames = cf
        )

    def exitConfigurable_frames(self, ctx):
        ctx.value = [x.value for x in ctx.frames]

    def exitConfigurable_frame(self, ctx):
        fname = ctx.fname.value
        mid = ctx.mid.value if ctx.mid else None
        ctx.value = dict(frameName = fname, messageID = mid)

    def exitNode_composition_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitConfiguration(self, ctx):
        cname = ctx.cname.value
        items = [x.value for x in ctx.items]
        ctx.value = dict(configurationName = cname, items = items)

    def exitConfiguration_item(self, ctx):
        cnode = ctx.cnode.value
        lnodes = [x.value for x in ctx.lnodes]
        ctx.value = dict(compositeNode = cnode, logicalNodes = lnodes)

    def exitSignal_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitSignal_item(self, ctx):
        sname = ctx.sname.value
        ssize = ctx.ssize.value
        initValue = ctx.initValue.value
        pub = ctx.pub.value
        sub = [x.value for x in ctx.sub]
        ctx.value = dict(name = sname, size = ssize, initValue = initValue, publishedBy = pub, subscribedBy = sub)

    def exitInit_value(self, ctx):
        scalar = ctx.s.value if ctx.s else None
        array = ctx.a.value if ctx.a else None
        ctx.value = dict(scalar = scalar, array = array)

    def exitInit_value_scalar(self, ctx):
        ctx.value = ctx.i.value

    def exitInit_value_array(self, ctx):
        ctx.value = [x.value for x in ctx.vs]

    def exitDiagnostic_signal_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitDiagnostic_item(self, ctx):
        name = ctx.name.value
        size = ctx.size.value
        initValue = ctx.initValue.value
        ctx.value = dict(name = name, size = size, initValue = initValue)

    def exitSignal_groups_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitSignal_group(self, ctx):
        sgname = ctx.sgname.value
        gsize = ctx.gsize.value
        items = [x.value for x in ctx.items]
        ctx.value = dict(signalGroupName = sgname, groupSize = gsize, items = items)

    def exitSignal_group_item(self, ctx):
        sname = ctx.sname.value
        goffs = ctx.goffs.value
        ctx.value = dict(signalName = sname, groupOffset = goffs)

    def exitFrame_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitFrame_item(self, ctx):
        fname = ctx.fname.value
        fid = ctx.fid.value
        p = ctx.p.value
        fsize = ctx.fsize.value
        items = [x.value for x in ctx.items]
        ctx.value = dict(frameName = fname, frameID = fid, publishedBy = p, frameSize = fsize, signals = items)

    def exitFrame_signal(self, ctx):
        sname = ctx.sname.value
        soffs = ctx.soffs.value
        ctx.value = dict(signalName = sname, signalOffset = soffs)

    def exitSporadic_frame_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitSporadic_frame_item(self, ctx):
        name = ctx.sfn.value
        fnames = [x.value for x in ctx.names]
        ctx.value = dict(sporadicFrameName = name, frameNames = fnames)

    def exitEvent_triggered_frame_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitEvent_triggered_frame_item(self, ctx):
        e = ctx.e.value
        c = ctx.c.value
        fid = ctx.fid.value
        items = [x.value for x in ctx.items]
        ctx.value = dict(frameName = e, frameID = fid, scheduleTable = c, frameNames = items)

    def exitDiag_frame_def(self, ctx):
        mid = ctx.mid.value
        sid = ctx.sid.value
        mitems = [x.value for x in ctx.mitems]
        sitems = [x.value for x in ctx.sitems]
        ctx.value = dict(masterID = mid, slaveID = sid, masterSignals = mitems, slaveSignals = sitems)

    def exitDiag_frame_item(self, ctx):
        sname = ctx.sname.value
        soffs = ctx.soffs.value
        ctx.value = dict(signalName = sname, signalOffset = soffs)

    def exitSchedule_table_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitSchedule_table_entry(self, ctx):
        s = ctx.s.value
        items = [x.value for x in ctx.items]
        ctx.value = dict(name = s, commands = items)

    def exitSchedule_table_command(self, ctx):
        c = ctx.c.value
        f = ctx.f.value
        ctx.value = dict(command = c, frameTime = f)

    def exitCommand(self, ctx):
        if ctx.frameName:
            cmd = ctx.frameName.value
        else:
            cmd = ctx.c.text
        if cmd == 'AssignNAD':
            nodeName = ctx.nodeName.value
        elif cmd == 'ConditionalChangeNAD':
            nad = ctx.nad.value
            id_ = ctx.id_.value
            byte_ = ctx.byte_.value
            mask = ctx.mask.value
            inv = ctx.inv.value
            newNad = ctx.new_NAD.value
        elif cmd == 'DataDump':
            nodeName = ctx.nodeName.value
            d1 = ctx.d1.value
            d2 = ctx.d2.value
            d3 = ctx.d3.value
            d4 = ctx.d4.value
            d5 = ctx.d5.value
        elif cmd == 'SaveConfiguration':
            nodeName = ctx.nodeName.value
        elif cmd == 'AssignFrameIdRange':
            nodeName = ctx.nodeName.value
            frameIndex = ctx.frameIndex.value
            pids = [p.value for p in ctx.pids]
        elif cmd == 'FreeFormat':
            d1 = ctx.d1.value
            d2 = ctx.d2.value
            d3 = ctx.d3.value
            d4 = ctx.d4.value
            d5 = ctx.d5.value
            d6 = ctx.d6.value
            d7 = ctx.d7.value
            d8 = ctx.d8.value
        elif cmd == 'AssignFrameId':
            nodeName = ctx.nodeName.value
            frameName = ctx.frameName.value
        else:
            d1 = d2 = d3 = d4 = d5 = d6 = d7 = d8 = None
        ctx.value = dict(command = cmd)

    def exitSignal_encoding_type_def(self, ctx):
        items = [x.value for x in ctx.items]
        ctx.value = items

    def exitSignal_encoding_entry(self, ctx):
        s = ctx.s.value
        items = [x.value for x in ctx.items]
        ctx.value = dict(name = s, values = items)

    def exitSignal_encoding_value(self, ctx):
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

    def exitLogical_value(self, ctx):
        s = ctx.s.value
        t = ctx.t.value if ctx.t else None
        ctx.value = dict(signalValue = s, text = t)

    def exitPhysical_range(self, ctx):
        minValue = ctx.minValue.value
        maxValue = ctx.maxValue.value
        #scale = ctx.scale.value if ctx.scale else None
        #offset = ctx.offset.value
        scale = ctx.s.value
        offset = ctx.o.value
        ctx.value = dict(min = minValue, max = maxValue, scale = scale, offset = offset)

    def exitBcd_value(self, ctx):
        pass

    def exitAscii_value(self, ctx):
        pass

    def exitSignal_representation_def(self, ctx):
        items = [x.value for x in ctx.items]
        ctx.value = items

    def exitSignal_representation_entry(self, ctx):
        enc = ctx.enc.value
        names = [x.value for x in ctx.names]
        ctx.value = dict(name = enc, signalNames = names)


