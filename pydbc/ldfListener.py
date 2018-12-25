
from collections import namedtuple
from pprint import pprint

from antlr4 import *


class ldfListener(ParseTreeListener):


    def exitLin_description_file(self, ctx):
        pass

    def exitLin_protocol_version_def(self, ctx):
        pass

    def exitLin_language_version_def(self, ctx):
        pass

    def exitLin_speed_def(self, ctx):
        pass

    def exitChannel_name_def(self, ctx):
        pass

    def exitNode_def(self, ctx):
        pass

    def exitNode_name(self, ctx):
        pass

    def exitTime_base(self, ctx):
        pass

    def exitJitter(self, ctx):
        pass

    def exitNode_attributes_def(self, ctx):
        pass

    def exitProtocol_version(self, ctx):
        pass

    def exitDiag_address(self, ctx):
        pass

    def exitAttributes_def(self, ctx):
        pass

    def exitSupplier_id(self, ctx):
        pass

    def exitFunction_id(self, ctx):
        pass

    def exitVariant(self, ctx):
        pass

    def exitSignal_name(self, ctx):
        pass

    def exitConfigurable_frames_20_def(self, ctx):
        pass

    def exitMessage_id(self, ctx):
        pass

    def exitConfigurable_frames_21_def(self, ctx):
        pass

    def exitNode_composition_def(self, ctx):
        pass

    def exitConfiguration_name(self, ctx):
        pass

    def exitComposite_node(self, ctx):
        pass

    def exitLogical_node(self, ctx):
        pass

    def exitSignal_def(self, ctx):
        pass

    def exitSignal_size(self, ctx):
        pass

    def exitInit_value(self, ctx):
        pass

    def exitInit_value_scalar(self, ctx):
        pass

    def exitInit_value_array(self, ctx):
        pass

    def exitPublished_by(self, ctx):
        pass

    def exitSubscribed_by(self, ctx):
        pass

    def exitDiagnostic_signal_def(self, ctx):
        pass

    def exitSignal_groups_def(self, ctx):
        pass

    def exitSignal_group_name(self, ctx):
        pass

    def exitGroup_size(self, ctx):
        pass

    def exitGroup_offset(self, ctx):
        pass

    def exitFrame_def(self, ctx):
        pass

    def exitFrame_name(self, ctx):
        ctx.value = ctx.i.value

    def exitFrame_id(self, ctx):
        ctx.value = ctx.i.value

    def exitFrame_size(self, ctx):
        ctx.value = ctx.i.value

    def exitSignal_offset(self, ctx):
        ctx.value = ctx.i.value

    def exitSporadic_frame_def(self, ctx):
        pass

    def exitSporadic_frame_name(self, ctx):
        ctx.value = ctx.i.value

    def exitEvent_triggered_frame_def(self, ctx):
        #(e = event_trig_frm_name ':' c = collision_resolving_schedule_table ',' fid = frame_id names += (',' frame_name ';')* )*

    def exitEvent_trig_frm_name(self, ctx):
        ctx.value = ctx.i.value

    def exitCollision_resolving_schedule_table(self, ctx):
        ctx.value = ctx.i.value

    def exitDiag_frame_def(self, ctx):
        m = ctx.m.value
        ms = [x.value for x in ctx.ms]
        s = ctx.s.value
        ss = [x.value for x in ctx.ss]
        ctx.value = OrderedDict(m = m, ms = ms, s = s, ss = ss)


    def exitSchedule_table_def(self, ctx):
        items = [x.value for x in ctx.items]
        ctx.value = items
        #(s = schedule_table_name  '{' (c = command 'delay' f = frame_time 'ms' ';')*  '}')*

    def exitSchedule_table_name(self, ctx):
        ctx.value = ctx.i.value

    def exitCommand(self, ctx):
        if ctx.frameName:
            cmd = ctx.frameName.value
        else:
            cmd = ctx.c.value
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
            pids = [p.value for p in ctx.p]
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
        ctx.value = OrderedDict(command = cmd)

    def exitFrame_index(self, ctx):
        ctx.value = ctx.i.value

    def exitFrame_PID(self, ctx):
        ctx.value = ctx.i.value

    def exitFrame_time(self, ctx):
        ctx.value = ctx.n.value

    def exitSignal_encoding_type_def(self, ctx):
        encoding_type_name = ctx.s.value
        if ctx.l:
            value = ctx.l.value
            vtype = "logical"
        elif ctx.p:
            value = ctx.p.value
            vtype = "range"
        elif ctx.b:
            value = ctx.b.value
            vtype = "bcd"
        elif ctx.a:
            value = ctx.a.name
            vtype = "ascii"
        ctx.value = OrderedDict(encoding_type_name = encoding_type_name, value = value, type = vtype)

    def exitSignal_encoding_type_name(self, ctx):
        ctx.value = ctx.i.value

    def exitLogical_value(self, ctx):
        pass

    def exitPhysical_range(self, ctx):
        pass

    def exitBcd_value(self, ctx):
        pass

    def exitAscii_value(self, ctx):
        pass

    def exitSignal_value(self, ctx):
        ctx.value = ctx.i.value

    def exitMin_value(self, ctx):
        ctx.value = ctx.i.value

    def exitMax_value(self, ctx):
        ctx.value = ctx.i.value

    def exitScale(self, ctx):
        ctx.value = ctx.n.value

    def exitOffset(self, ctx):
        ctx.value = ctx.n.value

    def exitText_info(self, ctx):
        ctx.value = ctx.s.value

    def exitSignal_representation_def(self, ctx):
        names = [x.value for x in ctx.names]
        ctx.value = OrderedDict(encoding_type = ctx.enc.value, signal_names = names)

    def exitIntValue(self, ctx):
        ctx.value = int(ctx.i.text) if ctx.i else None

    def exitFloatValue(self, ctx):
        ctx.value = float(ctx.f.text) if ctx.f else None

    def exitNumber(self, ctx):
        ctx.value = ctx.i.value if ctx.i else ctx.f.value

    def exitStringValue(self, ctx):
        ctx.value = ctx.s.text.strip('"') if ctx.s else None

    def exitIdentifierValue(self, ctx):
        ctx.value = ctx.i.text if ctx.i else None

