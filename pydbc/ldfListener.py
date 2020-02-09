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

from collections import namedtuple

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

class AttributeContainer:

    def __init__(self, name, objType, valueType, minimum = None, maximum = None, array = False):
        self.name = name
        self.objType = objType
        self.valueType = valueType
        self.minimum = minimum
        self.maximum = maximum
        self.array = array

    def __repr__(self):
        return "{}({} {} {} {} {} {})".format(self.__class__.__name__, self.name, self.objType, self.valueType, self.minimum, self.maximum, self.array)


LDF_ATTRS = {
    # Network
    "LIN_protocol_version": AttributeContainer("LIN_protocol_version", AttributeType.NETWORK, ValueType.STRING),
    "LIN_language_version": AttributeContainer("LIN_language_version", AttributeType.NETWORK, ValueType.STRING),
    "LIN_file_revision": AttributeContainer("LIN_file_revision", AttributeType.NETWORK, ValueType.STRING),
    "LIN_speed": AttributeContainer("LIN_speed", AttributeType.NETWORK, ValueType.FLOAT),
    "LIN_channel_name": AttributeContainer("LIN_channel_name", AttributeType.NETWORK, ValueType.STRING),
    "LIN_include_diag": AttributeContainer("LIN_include_diag", AttributeType.NETWORK, ValueType.INT),
    # Nodes
    "LIN_is_master": AttributeContainer("LIN_is_master", AttributeType.NODE, ValueType.INT),
    "LIN_is_slave": AttributeContainer("LIN_is_slave", AttributeType.NODE, ValueType.INT),
    "LIN_time_base": AttributeContainer("LIN_time_base", AttributeType.NODE, ValueType.FLOAT),
    "LIN_jitter": AttributeContainer("LIN_jitter", AttributeType.NODE, ValueType.FLOAT),
    "LIN_protocol": AttributeContainer("LIN_protocol", AttributeType.NODE, ValueType.STRING),
    "LIN_configured_NAD": AttributeContainer("LIN_configured_NAD", AttributeType.NODE, ValueType.INT),
    "LIN_initial_NAD": AttributeContainer("LIN_initial_NAD", AttributeType.NODE, ValueType.INT),
    "LIN_supplier_id": AttributeContainer("LIN_supplier_id", AttributeType.NODE, ValueType.INT),
    "LIN_function_id": AttributeContainer("LIN_function_id", AttributeType.NODE, ValueType.INT),
    "LIN_variant": AttributeContainer("LIN_variant", AttributeType.NODE, ValueType.INT),
    "LIN_response_error": AttributeContainer("LIN_response_error", AttributeType.NODE, ValueType.STRING),
    #fault_state_signals*        identifierValue [SIGNAL]
    "LIN_P2_min": AttributeContainer("LIN_P2_min", AttributeType.NODE, ValueType.FLOAT),
    "LIN_ST_min": AttributeContainer("LIN_ST_min", AttributeType.NODE, ValueType.FLOAT),
    "LIN_N_As_timeout": AttributeContainer("LIN_N_As_timeout", AttributeType.NODE, ValueType.FLOAT),
    "LIN_N_Cr_timeout": AttributeContainer("LIN_N_Cr_timeout", AttributeType.NODE, ValueType.FLOAT),
    # Signals
    "LIN_signal_initial_value": AttributeContainer("LIN_signal_initial_value", AttributeType.SIGNAL, ValueType.INT, array = True),
}


class LdfListener(parser.BaseListener):

    def __init__(self, database, logLevel = 'INFO', *args, **kws):
        super(LdfListener, self).__init__(database, logLevel, *args, **kws)
        self.nodes = {}
        self.signals = {}
        self.frames = {}
        self.insertNetwork()
        self.insertAttributeDefinitions()

    def insertAttributeDefinitions(self):
        for key, attr in LDF_ATTRS.items():
            ad = Attribute_Definition(
                name = attr.name, objecttype = attr.objType, valuetype = attr.valueType, array = attr.array
            )
            self.db.session.add(ad)
            self.db.session.flush()
            attr.attrDef = ad.rid
        self.db.session.flush()

    def setAttributeValue(self, objID, attribute, value):
        #print("S-A", objID, attribute, value)
        attr = LDF_ATTRS.get(attribute)
        if attr is None:
            raise KeyError("Invalid attribute '{}'".format(attribute))
        numValue = None
        stringValue = None
        if attr.array:
            stringValue = value
        else:
            if attr.valueType in (ValueType.FLOAT, ValueType.INT):
                numValue = value
            elif attr.valueType == ValueType.STRING:
                stringValue = value
        ad = self.db.session.query(Attribute_Definition).filter(Attribute_Definition.name == attribute).one()
        av = Attribute_Value(object_id = objID, attribute_definition = ad, num_value = numValue, string_value = stringValue)
        self.db.session.add(av)
        self.db.session.flush()

    def insertNetwork(self, specific = None):
        network = Network(name = self.db.dbname)
        self.db.session.add(network)
        self.network_id = network.rid
        proto = Vndb_Protocol(network = network, name = BusType.LIN.name, specific = specific)
        self.db.session.add(proto)
        self.db.session.flush()

    def insertConfigurableFrames(self):
        for node, frames in self.configurableFrames.items():
            for frameName, messageID in frames:
                frame = self.db.session.query(LinUnconditionalFrame).\
                    filter(LinUnconditionalFrame.name == frameName).scalar()
                cf = LinConfigurableFrame(node = node, frame = frame, identifier = messageID)
                self.db.session.add(cf)
        self.db.session.flush()

    def insertFaultStateSignals(self):
        for node, signals in self.faultStateSignals.items():
            for signalName in signals:
                signal = self.db.session.query(Signal).filter(Signal.name == signalName).one()
                lfs = LinFaultStateSignal(node = node, signal = signal)
                self.db.session.add(lfs)
        self.db.session.flush()

    def insertFrameSignalRelationships(self):
        for sigName, signal in self.signals.items():
            sgrid = signal['rid']
            for frameName in self.sendingFrameNames(sigName):
                frame = self.frames.get(frameName)
                frid = frame['rid']
                for nodeName in signal['subscribedBy']:
                    nid = self.nodes.get(nodeName)
                    rxs = Node_RxSignal(node_id = nid, message_id = frid, signal_id = sgrid)
                    self.db.session.add(rxs)
        self.db.session.flush()

    def sendingFrameNames(self, signal):
        result = []
        for _, frame in self.frames.items():
            frameSignals = (s['signalName'] for s in frame['signals'])
            frameName = frame['frameName']
            if signal in frameSignals:
                result.append(frameName)
        return result

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
        self.insertConfigurableFrames()
        self.insertFaultStateSignals()
        self.insertFrameSignalRelationships()
        self.db.session.commit()

    def exitLin_protocol_version_def(self, ctx):
        ctx.value = self.getValue(ctx.s)

    def exitLin_language_version_def(self, ctx):
        ctx.value = self.getValue(ctx.s)

    def exitLin_file_revision_def(self, ctx):
        ctx.value = self.getValue(ctx.s)

    def exitLin_speed_def(self, ctx):
        ctx.value = self.getValue(ctx.n)

    def exitChannel_name_def(self, ctx):
        ctx.value = self.getValue(ctx.i)

    def exitNode_def(self, ctx):
        mname = self.getValue(ctx.mname)
        tb = self.getValue(ctx.tb)
        j = self.getValue(ctx.j)
        snames = [x.value for x in ctx.snames]
        ctx.value = dict(master = mname, timeBase = tb, jitter = j, slaves = snames)
        nodes = ctx.value
        masterNode = nodes['master']
        master = Node(name = masterNode)
        print("master", master)
        self.db.session.add(master)
        self.db.session.flush()
        mrid = master.rid
        self.nodes[masterNode] = mrid
        self.master = masterNode
        self.setAttributeValue(mrid, "LIN_is_master", 1)
        self.setAttributeValue(mrid, "LIN_time_base", nodes['timeBase'])
        self.setAttributeValue(mrid, "LIN_jitter", nodes['jitter'])
        for name in nodes['slaves']:
            slave = Node(name = name)
            self.db.session.add(slave)
            self.db.session.flush()
            srid = slave.rid
            self.setAttributeValue(srid, "LIN_is_slave", 1)
            self.nodes[name] = srid
            print("SlaveNode:", name, srid)

    def exitNode_attributes_def(self, ctx):
        KEY_MAP = {
            'initialNAD': "LIN_initial_NAD",
            'configuredNAD': "LIN_configured_NAD",
            'version': "LIN_protocol",
            'nAs': "LIN_N_As_timeout",
            'supplierID': "LIN_supplier_id",
            'functionID': "LIN_function_id",
            'variant': "LIN_variant",
            'p2Min': "LIN_P2_min",
            'nCr': "LIN_N_Cr_timeout",
            'stMin': "LIN_ST_min",
            'responseErrorSignal': 'LIN_response_error',
            #'faultStateSignals': ""
        }
        items = [x.value for x in ctx.items]
        ctx.value = items
        attrs = ctx.value
        self.configurableFrames = {}
        self.faultStateSignals = {}
        for attr in attrs:
            name = attr['name']
            nid = self.nodes.get(name)
            node = self.db.session.query(Node).get(nid)
            for key, mappedKey in KEY_MAP.items():
                value = attr.get(key)
                if value is not None:
                    self.setAttributeValue(nid, mappedKey, value)
            if 'configurableFrames' in attr:
                self.configurableFrames[node] = []
                for cframe in attr['configurableFrames']:
                    self.configurableFrames[node].append((cframe['frameName'],cframe['messageID'], ))
            if 'faultStateSignals' in attr:
                self.faultStateSignals[node] = []
                for fs in attr['faultStateSignals']:
                    self.faultStateSignals[node].append(fs)

    def exitNode_attribute(self, ctx):
        name = self.getValue(ctx.name)
        version = self.getValue(ctx.version)
        n0 = self.getValue(ctx.n0)
        n1 = self.getValue(ctx.n1)
        attrs = self.getValue(ctx.attrs, dict())
        ctx.value = dict(name = name, version = version, configuredNAD = n0, initialNAD = n1, **attrs)

    def exitAttributes_def(self, ctx):
        sid = self.getValue(ctx.sid)
        fid = self.getValue(ctx.fid)
        v = self.getValue(ctx.v)
        sn0 = self.getValue(ctx.sn0)
        sn1s = [x.value for x in ctx.sn1s]
        cf = self.getValue(ctx.cf)
        p2Min = self.getValue(ctx.p2Min)
        stMin = self.getValue(ctx.stMin)
        nAs = self.getValue(ctx.nAs)
        nCr = self.getValue(ctx.nCr)
        ctx.value = dict(supplierID = sid, functionID = fid, variant = v, responseErrorSignal = sn0, faultStateSignals = sn1s,
            p2Min = p2Min, stMin = stMin, nAs = nAs, nCr = nCr, configurableFrames = cf
        )

    def exitConfigurable_frames(self, ctx):
        ctx.value = [x.value for x in ctx.frames]

    def exitConfigurable_frame(self, ctx):
        fname = self.getValue(ctx.fname)
        mid = self.getValue(ctx.mid)
        ctx.value = dict(frameName = fname, messageID = mid)

    def exitNode_composition_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitConfiguration(self, ctx):
        cname = self.getValue(ctx.cname)
        items = [x.value for x in ctx.items]
        ctx.value = dict(configurationName = cname, items = items)

    def exitConfiguration_item(self, ctx):
        cnode = self.getValue(ctx.cnode)
        lnodes = [x.value for x in ctx.lnodes]
        ctx.value = dict(compositeNode = cnode, logicalNodes = lnodes)

    def exitSignal_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        for signal in ctx.value:
            print("SIG:", signal)
            initValue = signal['initValue']
            name = signal['name']
            size = signal['size']
            publishedBy = signal['publishedBy']
            subscribedBy = signal['subscribedBy']
            sig = Signal(name = name, bitsize = size)
            self.db.session.add(sig)
            self.db.session.flush()
            signal['rid'] = sig.rid
            publisher = self.db.session.query(Node).filter(Node.name == publishedBy).one()
            txs = Node_TxSig(node = publisher, signal = sig)
            self.db.session.add(txs)
            self.db.session.flush()
            self.signals[name] = signal
            # TODO: move to setAttributeValue
            if initValue['array'] is None:
                if initValue['scalar'] is None:
                    continue
                else:
                    iv = initValue['scalar']
            else:
                iv = ';'.join([str(x) for x in initValue['array']])
            self.setAttributeValue(sig.rid, 'LIN_signal_initial_value', iv)

    def exitSignal_item(self, ctx):
        sname = self.getValue(ctx.sname)
        ssize = self.getValue(ctx.ssize)
        initValue = self.getValue(ctx.initValue)
        pub = self.getValue(ctx.pub)
        sub = [x.value for x in ctx.sub]
        ctx.value = dict(name = sname, size = ssize, initValue = initValue, publishedBy = pub, subscribedBy = sub)

    def exitInit_value(self, ctx):
        scalar = self.getValue(ctx.s)
        array = self.getValue(ctx.a)
        ctx.value = dict(scalar = scalar, array = array)

    def exitInit_value_scalar(self, ctx):
        ctx.value = self.getValue(ctx.i)

    def exitInit_value_array(self, ctx):
        ctx.value = [x.value for x in ctx.vs]

    def exitDiagnostic_signal_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitDiagnostic_item(self, ctx):
        name = self.getValue(ctx.name)
        size = self.getValue(ctx.size)
        initValue = self.getValue(ctx.initValue)
        ctx.value = dict(name = name, size = size, initValue = initValue)

    def exitSignal_groups_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitSignal_group(self, ctx):
        sgname = self.getValue(ctx.sgname)
        gsize = self.getValue(ctx.gsize)
        items = [x.value for x in ctx.items]
        ctx.value = dict(signalGroupName = sgname, groupSize = gsize, items = items)

    def exitSignal_group_item(self, ctx):
        sname = self.getValue(ctx.sname)
        goffs = self.getValue(ctx.goffs)
        ctx.value = dict(signalName = sname, groupOffset = goffs)

    def exitFrame_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        for frame in ctx.value:
            frid = frame['frameID']
            name = frame['frameName']
            size = frame['frameSize']
            publishedBy = frame['publishedBy']
            sender = self.nodes.get(publishedBy)
            msg = LinUnconditionalFrame(name = name, message_id = frid, dlc = size, sender = sender)
            self.db.session.add(msg)
            self.db.session.flush()
            print("FRAME:", msg)
            frame['rid'] = msg.rid
            self.frames[name] = frame
            for signal in frame['signals']:
                signalOffs = signal['signalOffset']
                signalName = signal['signalName']
                srid = self.signals[signalName]['rid']
                sig = self.db.session.query(Signal).get(srid)
                ms = Message_Signal(offset = signalOffs, signal = sig, message = msg)
                self.db.session.add(ms)
            self.db.session.flush()

    def exitFrame_item(self, ctx):
        fname = self.getValue(ctx.fname)
        fid = self.getValue(ctx.fid)
        p = self.getValue(ctx.p)
        fsize = self.getValue(ctx.fsize)
        items = [x.value for x in ctx.items]
        ctx.value = dict(frameName = fname, frameID = fid, publishedBy = p, frameSize = fsize, signals = items)

    def exitFrame_signal(self, ctx):
        sname = self.getValue(ctx.sname)
        soffs = self.getValue(ctx.soffs)
        ctx.value = dict(signalName = sname, signalOffset = soffs)

    def exitSporadic_frame_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        for sf in ctx.value:
            print("*SPOR", sf)
            name = sf['sporadicFrameName']
            lsf = LinSporadicFrame(name = name)
            self.db.session.add(lsf)
            self.db.session.flush()
            for frameName in sf['frameNames']:
                frame = self.db.session.query(Message).filter(Message.name == frameName).first()
                print("\t*SP-FRAME", frame)
                lsf.associated_frames.append(frame)
        self.db.session.flush()

    def exitSporadic_frame_item(self, ctx):
        name = ctx.sfn.value
        fnames = [x.value for x in ctx.names]
        ctx.value = dict(sporadicFrameName = name, frameNames = fnames)

    def exitEvent_triggered_frame_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        for ef in ctx.value:
            print("*ETF", ef)
            name = ef['frameName']
            scheduleTable = ef['scheduleTable']
            lst = self.db.session.query(LinScheduleTable).filter(LinScheduleTable.name == scheduleTable).first()
            print("SCH", scheduleTable, lst)
            frameID = ef['frameID']
            etf = LinEventTriggeredFrame(name = name, message_id = frameID,  collision_resolving_schedule_table = lst)
            self.db.session.add(etf)
            self.db.session.flush()
            for frameName in ef['frameNames']:
                frame = self.db.session.query(Message).filter(Message.name == frameName).first()
                print("\t*ET-FRAME", frame)
                etf.associated_frames.append(frame)
        self.db.session.flush()

    def exitEvent_triggered_frame_item(self, ctx):
        e = self.getValue(ctx.e)
        c = self.getValue(ctx.c)
        fid = self.getValue(ctx.fid)
        items = [x.value for x in ctx.items]
        ctx.value = dict(frameName = e, frameID = fid, scheduleTable = c, frameNames = items)

    def exitDiag_frame_def(self, ctx):
        mid = self.getValue(ctx.mid)
        sid = self.getValue(ctx.sid)
        mitems = [x.value for x in ctx.mitems]
        sitems = [x.value for x in ctx.sitems]
        ctx.value = dict(masterID = mid, slaveID = sid, masterSignals = mitems, slaveSignals = sitems)

    def exitDiag_frame_item(self, ctx):
        sname = self.getValue(ctx.sname)
        soffs = self.getValue(ctx.soffs)
        ctx.value = dict(signalName = sname, signalOffset = soffs)

    def exitSchedule_table_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]
        for table in ctx.value:
            name = table['name']
            lst = LinScheduleTable(name = name)
            self.db.session.add(lst)
            self.db.session.flush()
            for cmd in table['commands']:
                frame_time = cmd['frameTime']
                cmd = cmd['command']
                ct = cmd['type']
                if ct == 'Frame':
                    name = cmd['frame_name']
                    frame = self.db.session.query(Message).filter(Message.name == name).first()
                    entry = LinScheduleTable_Command_Frame(frame_time = frame_time, frame = frame)
                elif ct == 'MasterReq':
                    entry = LinScheduleTable_Command_MasterReq(frame_time = frame_time)
                elif ct == 'SlaveResp':
                    entry = LinScheduleTable_Command_SlaveResp(frame_time = frame_time)
                elif ct == 'AssignNAD':
                    name = cmd['node_name']
                    node = self.db.session.query(Node).filter(Node.name == name).first()
                    entry = LinScheduleTable_Command_AssignNad(frame_time = frame_time, node = node)
                elif ct == 'ConditionalChangeNAD':
                    nad = cmd['nad']
                    id_ = cmd['id']
                    byte_ = cmd['byte']
                    mask = cmd['mask']
                    inv = cmd['inv']
                    new_nad = cmd['new_nad']
                    entry = LinScheduleTable_Command_ConditionalChangeNad(frame_time = frame_time, nad = nad,
                        id = id_, byte = byte_, mask = mask, inv = inv, new_nad = new_nad
                    )
                elif ct == 'DataDump':
                    name = cmd['node_name']
                    node = self.db.session.query(Node).filter(Node.name == name).first()
                    d1 = cmd['d1']
                    d2 = cmd['d2']
                    d3 = cmd['d3']
                    d4 = cmd['d4']
                    d5 = cmd['d5']
                    entry = LinScheduleTable_Command_DataDump(frame_time = frame_time, node = node, d1 = d1,
                        d2 = d2, d3 = d3, d4 = d4, d5 = d5
                    )
                elif ct == 'SaveConfiguration':
                    name = cmd['node_name']
                    node = self.db.session.query(Node).filter(Node.name == name).first()
                    entry = LinScheduleTable_Command_SaveConfiguration(frame_time = frame_time, node = node)
                elif ct == 'AssignFrameIdRange':
                    name = cmd['node_name']
                    node = self.db.session.query(Node).filter(Node.name == name).first()
                    frame_index = cmd['frame_index']
                    frame_pid1 = cmd['pid1']
                    frame_pid2 = cmd['pid2']
                    frame_pid3 = cmd['pid3']
                    frame_pid4 = cmd['pid4']
                    entry = LinScheduleTable_Command_AssignFrameIdRange(frame_time = frame_time, node = node,
                        frame_index = frame_index, frame_pid1 = frame_pid1, frame_pid2 = frame_pid2,
                        frame_pid3 = frame_pid3, frame_pid4 = frame_pid4
                    )
                elif ct == 'FreeFormat':
                    d1 = cmd['d1']
                    d2 = cmd['d2']
                    d3 = cmd['d3']
                    d4 = cmd['d4']
                    d5 = cmd['d5']
                    d6 = cmd['d6']
                    d7 = cmd['d7']
                    d8 = cmd['d8']
                    entry = LinScheduleTable_Command_FreeFormat(frame_time = frame_time, d1 = d1, d2 = d2, d3 = d3,
                        d4 = d4, d5 = d5, d6 = d6, d7 = d7, d8 = d8
                    )
                elif ct == 'AssignFrameId':
                    node_name = cmd['nodeName']
                    frame_name = cmd['frameName']
                    node = self.db.session.query(Node).filter(Node.name == node_name).first()
                    frame = self.db.session.query(Message).filter(Message.name == frame_name).first()
                    entry = LinScheduleTable_Command_AssignFrameId(frame_time = frame_time, node = node, frame = frame)
                entry.lin_schedule_table = lst
                self.db.session.add(entry)
            self.db.session.flush()

    def exitSchedule_table_entry(self, ctx):
        s = self.getValue(ctx.s)
        items = [x.value for x in ctx.items]
        ctx.value = dict(name = s, commands = items)

    def exitSchedule_table_command(self, ctx):
        c = self.getValue(ctx.c)
        f = self.getValue(ctx.f)
        ctx.value = dict(command = c, frameTime = f)

    def exitCommand(self, ctx):
        if ctx.frameName:
            cmdName = "Frame"
        else:
            cmdName = ctx.c.text
        cmd = dict(type = cmdName)
        if cmdName == "Frame":
            cmd['frame_name'] = ctx.frameName.value
        elif cmdName == 'AssignNAD':
            cmd['node_name'] = ctx.nodeName.value
        elif cmdName == 'ConditionalChangeNAD':
            cmd['nad'] = ctx.nad.value
            cmd['id'] = ctx.id_.value
            cmd['byte'] = ctx.byte_.value
            cmd['mask'] = ctx.mask.value
            cmd['inv'] = ctx.inv.value
            cmd['new_nad'] = ctx.new_NAD.value
        elif cmdName == 'DataDump':
            cmd['node_name'] = ctx.nodeName.value
            cmd['d1'] = ctx.d1.value
            cmd['d2'] = ctx.d2.value
            cmd['d3'] = ctx.d3.value
            cmd['d4'] = ctx.d4.value
            cmd['d5'] = ctx.d5.value
        elif cmdName == 'SaveConfiguration':
            cmd['node_name'] = ctx.nodeName.value
        elif cmdName == 'AssignFrameIdRange':
            cmd['node_name'] = ctx.nodeName.value
            cmd['frame_index'] = ctx.frameIndex.value
            cmd['pid1'] = None
            cmd['pid2'] = None
            cmd['pid3'] = None
            cmd['pid4'] = None
            pids = [p.value for p in ctx.pids]
            lp = len(pids)
            if lp == 1:
                cmd['pid1'] = pids[0]
            elif lp == 2:
                cmd['pid1'] = pids[0]
                cmd['pid2'] = pids[1]
            elif lp == 3:
                cmd['pid1'] = pids[0]
                cmd['pid2'] = pids[1]
                cmd['pid3'] = pids[2]
            elif lp == 4:
                cmd['pid1'] = pids[0]
                cmd['pid2'] = pids[1]
                cmd['pid3'] = pids[2]
                cmd['pid4'] = pids[3]
        elif cmdName == 'FreeFormat':
            cmd['d1'] = ctx.d1.value
            cmd['d2'] = ctx.d2.value
            cmd['d3'] = ctx.d3.value
            cmd['d4'] = ctx.d4.value
            cmd['d5'] = ctx.d5.value
            cmd['d6'] = ctx.d6.value
            cmd['d7'] = ctx.d7.value
            cmd['d8'] = ctx.d8.value
        elif cmdName == 'AssignFrameId':
            cmd['nodeName'] = ctx.nodeName.value
            cmd['frameName'] = ctx.frameName.value
        ctx.value = cmd

    def exitSignal_encoding_type_def(self, ctx):
        items = [x.value for x in ctx.items]
        ctx.value = items
        tps = set()
        for enc in items:
            lse = LinSignalEncodingType(name = enc['name'])
            self.db.session.add(lse)
            for value in enc['values']:
                vtype = value['valueType']
                value = value["value"]
                if vtype == "logical":
                    entry = LinSignalEncodingEntry_Logical(signal_value = value['signalValue'], text_info = value['text'])
                elif vtype == "range":
                    min_value = value['min']
                    max_value = value['max']
                    scale = value['scale']
                    offset = value['offset']
                    text = value['text']
                    entry = LinSignalEncodingEntry_Physical(min_value = min_value, max_value = max_value,
                        scale = scale, offset = offset, text_info = text
                    )
                elif vtype == "bcd":
                    entry = LinSignalEncodingEntry_Value(entry_type = 2)
                elif vtype == "ascii":
                    entry = LinSignalEncodingEntry_Value(entry_type = 1)
                lse.entries.append(entry)
                self.db.session.add(entry)
        self.db.session.flush()

    def exitSignal_encoding_entry(self, ctx):
        s = self.getValue(ctx.s)
        items = [x.value for x in ctx.items]
        ctx.value = dict(name = s, values = items)


    def exitSignal_encoding_value(self, ctx):
        if ctx.l:
            value = self.getValue(ctx.l)
            vtype = "logical"
        elif ctx.p:
            value = self.getValue(ctx.p)
            vtype = "range"
        elif ctx.b:
            value = None
            vtype = "bcd"
        elif ctx.a:
            value = None
            vtype = "ascii"
        ctx.value = dict(value = value, valueType = vtype)

    def exitLogical_value(self, ctx):
        s = self.getValue(ctx.s)
        t = self.getValue(ctx.t)
        ctx.value = dict(signalValue = s, text = t)

    def exitPhysical_range(self, ctx):
        minValue = self.getValue(ctx.minValue)
        maxValue = self.getValue(ctx.maxValue)
        #scale = ctx.scale.value if ctx.scale else None
        #offset = ctx.offset.value
        scale = self.getValue(ctx.s)
        offset = self.getValue(ctx.o)
        t = self.getValue(ctx.t)
        ctx.value = dict(min = minValue, max = maxValue, scale = scale, offset = offset, text = t)

    def exitBcd_value(self, ctx):
        pass

    def exitAscii_value(self, ctx):
        pass

    def exitSignal_representation_def(self, ctx):
        items = [x.value for x in ctx.items]
        ctx.value = items
        for sr in items:
            name = sr['name']
            lse = self.db.session.query(LinSignalEncodingType).filter(LinSignalEncodingType.name == name).first()
            for signal_name in sr['signalNames']:
                signal = self.db.session.query(Signal).filter(Signal.name == signal_name).first()
                lsr = LinSignalRepresentation(lin_signal_encoding_type = lse, signal = signal)
                self.db.session.add(lsr)
        self.db.session.flush()

    def exitSignal_representation_entry(self, ctx):
        enc = self.getValue(ctx.enc)
        names = [x.value for x in ctx.names]
        ctx.value = dict(name = enc, signalNames = names)
