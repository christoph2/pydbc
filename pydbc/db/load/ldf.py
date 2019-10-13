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


import itertools

from pydbc.types import AttributeType, ValueType, CategoryType
from .base import BaseLoader

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

    def __init__(self, name, objType, valueType, minimum = None, maximum = None):
        self.name = name
        self.objType = objType
        self.valueType = valueType
        self.minimum = minimum
        self.maximum = maximum


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
}

class LdfLoader(BaseLoader):

    def __init__(self, db, queryClass):
        super(LdfLoader, self).__init__(db, queryClass)
        self.nodes = {}
        self.signals = {}
        self.frames = {}

    def _insertValues(self, cur, tree):
        pprint(tree)
        pprint(tree.keys())
        self.insertAttributeDefinitions(cur)
        self.insertNetworkAttributes(cur, tree)
        """
        dict_keys([
            'diagnosticSignals',

            'signals',

            'sporadicFrames',
            'nodeAttributes',
            'channelName',
            'nodes',
            'eventTriggeredFrames',
            'signalGroups',
            'signalRepresentations',
            'nodeCompositions',
            'scheduleTables',
            'signalEncodings',
            'diagnosticFrames',

            'frames'])
        """
        self.insertNetwork(cur)
        self.insertNodes(cur, tree['nodes'])
        self.insertNodeAttributes(cur, tree['nodeAttributes'])
        self.insertSignals(cur, tree['signals'])
        self.insertFrames(cur, tree['frames'])
        self.insertFrameSignalRelationships(cur)

    def insertAttributeDefinitions(self, cur):
        for key, attr in LDF_ATTRS.items():
            self.db.insertStatement(
                cur, "linAttribute_Definition", "Name, Objecttype, Valuetype", attr.name, attr.objType, attr.valueType
            )
            rid = cur.lastrowid
            attr.attrDef = rid

    def insertNetworkAttributes(self, cur, tree):
        KEY_MAP = {
            'languageVersion': "LIN_language_version",
            'protocolVersion': "LIN_protocol_version",
            'fileRevision': "LIN_file_revision",
            'speed': "LIN_speed",
            'channelName': 'LIN_channel_name',
        }
        objID = 0
        for key, mappedKey in KEY_MAP.items():
            value = tree[key]
            self.setAttributeValue(cur, objID, mappedKey, value)

    def insertNetwork(self, cur):
        self.db.insertStatement(cur, "Network", "Name", self.db.name)

    def insertNodes(self, cur, nodes):
        nodeIDs = {}
        masterNode = nodes['master']
        self.db.insertStatement(cur, "Node", "Name", masterNode)
        mrid = cur.lastrowid
        self.nodes[masterNode] = mrid
        self.master = masterNode
        self.setAttributeValue(cur, mrid, "LIN_is_master", 1)
        self.setAttributeValue(cur, mrid, "LIN_time_base", nodes['timeBase'])
        self.setAttributeValue(cur, mrid, "LIN_jitter", nodes['jitter'])
        for name in nodes['slaves']:
            self.db.insertStatement(cur, "Node", "Name", name)
            srid = cur.lastrowid
            self.setAttributeValue(cur, srid, "LIN_is_slave", 1)
            self.nodes[name] = srid
            print("SlaveNode:", name, srid)

    def insertNodeAttributes(self, cur, attrs):
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
        for attr in attrs:
            name = attr['name']
            nid = self.nodes.get(name)
            for key, mappedKey in KEY_MAP.items():
                value = attr[key]
                self.setAttributeValue(cur, nid, mappedKey, value)

    def insertSignals(self, cur, signals):
        """
        {'initValue': {'array': None, 'scalar': 0},
            'name': 'LockingSystem',
            'publishedBy': 'Gateway',
            'size': 1,
            'subscribedBy': ['Motor_back', 'Motor_head', 'Motor_horizontal', 'Motor_vertical']
        },
        """
        for signal in signals:
            initValue = signal['initValue']
            name = signal['name']
            size = signal['size']
            publishedBy = signal['publishedBy']
            subscribedBy = signal['subscribedBy']
            self.db.insertStatement(cur, "Signal", "Name, Bitsize", name, size)
            signal['rid'] = cur.lastrowid
            self.signals[name] = signal

    def insertFrames(self, cur, frames):
        """
            {'frameID': 21,
             'frameName': 'Seatheating',
             'frameSize': 1,
             'publishedBy': 'Gateway',
             'signals': [{'signalName': 'Heating', 'signalOffset': 0}]},
        """
        for frame in frames:
            frid = frame['frameID']
            name = frame['frameName']
            size = frame['frameSize']
            publishedBy = frame['publishedBy']
            sender = self.nodes.get(publishedBy)
            self.db.insertStatement(cur, "Message", "Name, Message_ID, DLC, Sender", name, frid, size, sender)
            frame['rid'] = cur.lastrowid
            self.frames[name] = frame

    def insertFrameSignalRelationships(self, cur):
        for sigName, signal in self.signals.items():
            sgrid = signal['rid']
            for frameName in self.sendingFrameNames(sigName):
                frame = self.frames.get(frameName)
                frid = frame['rid']
                for nodeName in signal['subscribedBy']:
                    nid = self.nodes.get(nodeName)
                    self.db.insertStatement(cur, "Node_RxSignal", "Message, Signal, Node", frid, sgrid, nid)

    def setAttributeValue(self, cur, objID, attribute, value):
        attr = LDF_ATTRS.get(attribute)
        if attr is None:
            raise KeyError("Invalid attribute '{}'".format(attribute))
        numValue = None
        stringValue = None
        if attr.valueType in (ValueType.FLOAT, ValueType.INT):
            numValue = value
        elif attr.valueType == ValueType.STRING:
            stringValue = value

        self.db.insertStatement(
            cur, "linAttribute_Value", "Object_ID, Attribute_Definition, Num_Value, String_Value",
            objID, attr.attrDef, numValue, stringValue
        )

    def sendingFrameNames(self, signal):
        result = []
        for _, frame in self.frames.items():
            frameSignals = (s['signalName'] for s in frame['signals'])
            frameName = frame['frameName']
            if signal in frameSignals:
                result.append(frameName)
        return result
