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


import itertools

from pydbc.types import AttributeType, ValueType, CategoryType
from .base import BaseLoader

from pydbc.db import BusType

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

from pprint import pprint


"""
LIN-Attributes
==============

Network
-------
    LIN_protocol_version        stringValue
    LIN_language_version        stringValue
    LIN_speed                   number
    LIN_channel_name            stringValue

Node
----
    ismaster                    number
    isslave                     number
    time_base [MASTER]          number
    jitter    [MASTER]          number
    LIN_protocol                stringValue
    configured_NAD              intValue
    initial_NAD                 intValue
    (product_id)
        supplier_id             intValue
        function_id             intValue
        variant                 intValue
    response_error              identifierValue [SIGNAL]
    fault_state_signals*        identifierValue [SIGNAL]
    P2_min                      number
    ST_min                      number
    N_As_timeout                number
    N_Cr_timeout                number

Signal
------

"""

# fbxFrame_Triggering
# fbxSchedule_Table
# fbxSchedule_Table_Entry

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

class LdfLoader(BaseLoader):

    def __init__(self, db):
        super(LdfLoader, self).__init__(db)
        self.nodes = {}
        self.signals = {}
        self.frames = {}

    def _insertValues(self, tree):
        pprint(tree)
        pprint(tree.keys())
        self.insertAttributeDefinitions()
        self.insertNetworkAttributes(tree)
        """
        dict_keys([
            'diagnosticSignals',
            'channelName',
            'signalGroups',
            'nodeCompositions',
            'diagnosticFrames',
            ])
        """
        self.insertNetwork()
        self.insertNodes(tree['nodes'])
        self.insertNodeAttributes(tree['nodeAttributes'])
        self.insertSignals(tree['signals'])
        self.insertFrames(tree['frames'])
        self.insertFrameSignalRelationships()
        self.insertSporadicFrames(tree['sporadicFrames'])
        self.insertEventTriggeredFrames(tree['eventTriggeredFrames'])
        self.insertConfigurableFrames()
        self.insertFaultStateSignals()
        self.insertScheduleTables(tree['scheduleTables'])
        self.insertSignalEncodings(tree['signalEncodings'])
        self.insertSignalRepresentations(tree['signalRepresentations'])
        self.session.commit()

    def insertAttributeDefinitions(self):
        for key, attr in LDF_ATTRS.items():
            ad = Attribute_Definition(
                name = attr.name, objecttype = attr.objType, valuetype = attr.valueType, array = attr.array
            )
            self.session.add(ad)
            self.session.flush()
            attr.attrDef = ad.rid
        self.session.flush()

    def insertNetworkAttributes(self, tree):
        KEY_MAP = {
            'languageVersion'   : "LIN_language_version",
            'protocolVersion'   : "LIN_protocol_version",
            'fileRevision'      : "LIN_file_revision",
            'speed'             : "LIN_speed",
            'channelName'       : 'LIN_channel_name',
        }
        objID = 0
        for key, mappedKey in KEY_MAP.items():
            value = tree[key]
            if value is not None:
                self.setAttributeValue(objID, mappedKey, value)

    def insertNetwork(self, specific = None):
        network = Network(name = self.db.dbname)
        self.session.add(network)
        proto = Vndb_Protocol(network = network, name = BusType.LIN.name, specific = specific)
        self.session.add(proto)
        self.session.flush()

    def insertNodes(self, nodes):
        nodeIDs = {}
        masterNode = nodes['master']
        master = Node(name = masterNode)
        self.session.add(master)
        self.session.flush()
        mrid = master.rid
        self.nodes[masterNode] = mrid
        self.master = masterNode
        self.setAttributeValue(mrid, "LIN_is_master", 1)
        self.setAttributeValue(mrid, "LIN_time_base", nodes['timeBase'])
        self.setAttributeValue(mrid, "LIN_jitter", nodes['jitter'])
        for name in nodes['slaves']:
            slave = Node(name = name)
            self.session.add(slave)
            self.session.flush()
            srid = slave.rid
            self.setAttributeValue(srid, "LIN_is_slave", 1)
            self.nodes[name] = srid
            print("SlaveNode:", name, srid)

    def insertNodeAttributes(self, attrs):
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
        self.configurableFrames = {}
        self.faultStateSignals = {}
        for attr in attrs:
            name = attr['name']
            nid = self.nodes.get(name)
            node = self.session.query(Node).get(nid)
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
        
    def insertConfigurableFrames(self):
        for node, frames in self.configurableFrames.items():
            for frameName, messageID in frames:
                frame = self.session.query(LinUnconditionalFrame).\
                    filter(LinUnconditionalFrame.name == frameName).scalar()
                cf = LinConfigurableFrame(node = node, frame = frame, identifier = messageID)
                self.session.add(cf)
        self.session.flush()
        
    def insertFaultStateSignals(self):
        for node, signals in self.faultStateSignals.items():
            for signalName in signals:
                signal = self.session.query(Signal).filter(Signal.name == signalName).one()
                lfs = LinFaultStateSignal(node = node, signal = signal)
                self.session.add(lfs)
        self.session.flush()

    def insertSignals(self, signals):
        for signal in signals:
            initValue = signal['initValue']
            name = signal['name']
            size = signal['size']
            publishedBy = signal['publishedBy']
            subscribedBy = signal['subscribedBy']
            sig = Signal(name = name, bitsize = size)
            self.session.add(sig)
            self.session.flush()
            signal['rid'] = sig.rid
            publisher = self.session.query(Node).filter(Node.name == publishedBy).one()
            txs = Node_TxSig(node = publisher, signal = sig)
            self.session.add(txs)
            self.session.flush()
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


    def insertFrames(self, frames):
        for frame in frames:
            frid = frame['frameID']
            name = frame['frameName']
            size = frame['frameSize']
            publishedBy = frame['publishedBy']
            sender = self.nodes.get(publishedBy)
            msg = LinUnconditionalFrame(name = name, message_id = frid, dlc = size, sender = sender)
            self.session.add(msg)
            self.session.flush()
            print("FRAME:", msg)
            frame['rid'] = msg.rid
            self.frames[name] = frame
            for signal in frame['signals']:
                signalOffs = signal['signalOffset']
                signalName = signal['signalName']
                srid = self.signals[signalName]['rid']
                sig = self.session.query(Signal).get(srid)
                ms = Message_Signal(offset = signalOffs)
                self.session.add(ms)
                ms.signal = sig
                ms.message = msg
                #msg.signals.append(ms)
            self.session.flush()

    def insertFrameSignalRelationships(self):
        for sigName, signal in self.signals.items():
            sgrid = signal['rid']
            for frameName in self.sendingFrameNames(sigName):
                frame = self.frames.get(frameName)
                frid = frame['rid']
                for nodeName in signal['subscribedBy']:
                    nid = self.nodes.get(nodeName)
                    rxs = Node_RxSignal(node_id = nid, message_id = frid, signal_id = sgrid)
                    self.session.add(rxs)
        self.session.flush()
        
    def insertSporadicFrames(self, sporadicFrames):
        for sf in sporadicFrames:
            print("*SPOR", sf)
            name = sf['sporadicFrameName']
            lsf = LinSporadicFrame(name = name)
            self.session.add(lsf)
            self.session.flush()
            for frameName in sf['frameNames']:
                frame = self.session.query(Message).filter(Message.name == frameName).first()
                print("\t*SP-FRAME", frame)
                lsf.associated_frames.append(frame)
        self.session.flush()

    def insertEventTriggeredFrames(self, eventTriggeredFrames):
        for ef in eventTriggeredFrames:
            print("*ETF", ef)
            name = ef['frameName']
            scheduleTable = ef['scheduleTable']
            lst = self.session.query(LinScheduleTable).filter(LinScheduleTable.name == scheduleTable).first()
            print("SCH", scheduleTable, lst)
            frameID = ef['frameID']
            etf = LinEventTriggeredFrame(name = name, message_id = frameID,  collision_resolving_schedule_table = lst)
            self.session.add(etf)
            self.session.flush()
            for frameName in ef['frameNames']:
                frame = self.session.query(Message).filter(Message.name == frameName).first()
                print("\t*ET-FRAME", frame)
                etf.associated_frames.append(frame)
        self.session.flush()
        
    def setAttributeValue(self, objID, attribute, value):
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
        ad = self.session.query(Attribute_Definition).filter(Attribute_Definition.name == attribute).one()
        av = Attribute_Value(object_id = objID, attribute_definition = ad, num_value = numValue, string_value = stringValue)
        self.session.add(av)
        self.session.flush()

    def sendingFrameNames(self, signal):
        result = []
        for _, frame in self.frames.items():
            frameSignals = (s['signalName'] for s in frame['signals'])
            frameName = frame['frameName']
            if signal in frameSignals:
                result.append(frameName)
        return result

    def insertScheduleTables(self, scheduleTables):
        for table in scheduleTables:
            print("TABLE:", table)
            name = table['name']
            lst = LinScheduleTable(name = name)
            self.session.add(lst)
            self.session.flush()
            for cmd in table['commands']:
                frame_time = cmd['frameTime']
                cmd = cmd['command']
                print("\tCMD", cmd)
                ct = cmd['type']
                if ct == 'Frame':
                    name = cmd['frame_name']
                    frame = self.session.query(Message).filter(Message.name == name).first()
                    print("\t*FRAME", frame)
                    entry = LinScheduleTable_Command_Frame(frame_time = frame_time, frame = frame)
                elif ct == 'MasterReq':
                    entry = LinScheduleTable_Command_MasterReq(frame_time = frame_time)
                elif ct == 'SlaveResp':
                    entry = LinScheduleTable_Command_SlaveResp(frame_time = frame_time)
                elif ct == 'AssignNAD':
                    name = cmd['node_name']
                    node = self.session.query(Node).filter(Node.name == name).first()
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
                    node = self.session.query(Node).filter(Node.name == name).first()
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
                    node = self.session.query(Node).filter(Node.name == name).first()
                    entry = LinScheduleTable_Command_SaveConfiguration(frame_time = frame_time, node = node)
                elif ct == 'AssignFrameIdRange':
                    name = cmd['node_name']
                    node = self.session.query(Node).filter(Node.name == name).first()
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
                    node = self.session.query(Node).filter(Node.name == node_name).first()
                    frame = self.session.query(Message).filter(Message.name == frame_name).first()
                    entry = LinScheduleTable_Command_AssignFrameId(frame_time = frame_time, node = node, frame = frame)
                entry.lin_schedule_table = lst
                self.session.add(entry)
            self.session.flush()

    def insertSignalEncodings(self, signalEncodings):
        tps = set()
        for enc in signalEncodings:
            lse = LinSignalEncodingType(name = enc['name'])
            self.session.add(lse)
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
                self.session.add(entry)
        self.session.flush()

    def insertSignalRepresentations(self, signalRepresentations):
        for sr in signalRepresentations:
            name = sr['name']
            lse = self.session.query(LinSignalEncodingType).filter(LinSignalEncodingType.name == name).first()
            for signal_name in sr['signalNames']:
                signal = self.session.query(Signal).filter(Signal.name == signal_name).first()
                lsr = LinSignalRepresentation(lin_signal_encoding_type = lse, signal = signal)
                self.session.add(lsr)
        self.session.flush()
