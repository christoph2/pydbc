
from collections import namedtuple, OrderedDict
from pprint import pprint

import antlr4

class LdfListener(antlr4.ParseTreeListener):


    def exitLin_description_file(self, ctx):
        """
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
        """
        self.value = OrderedDict(
            protocolVersion = ctx.pv.value,
            languageVersion = ctx.lv.value,
            speed = ctx.ls.value,
        )

    def exitLin_protocol_version_def(self, ctx):
        ctx.value = ctx.s.value
        print("protocol_ver", ctx.value)

    def exitLin_language_version_def(self, ctx):
        ctx.value = ctx.s.value
        print("language_ver", ctx.value)

    def exitLin_speed_def(self, ctx):
        ctx.value = ctx.n.value
        print("speed:", ctx.value)

    def exitChannel_name_def(self, ctx):
        ctx.value = ctx.i.value
        print("channel_name", ctx.value)

    def exitNode_def(self, ctx):
        mname = ctx.mname.value
        tb = ctx.tb.value
        j = ctx.j.value
        snames = [x.value for x in ctx.snames]
        ctx.value = OrderedDict(master = mname, timeBase = tb, jitter = j, slaves = snames)
        print("node_def:", ctx.value)

    def exitNode_name(self, ctx):
        ctx.value = ctx.i.value

    def exitTime_base(self, ctx):
        ctx.value = ctx.n.value

    def exitJitter(self, ctx):
        ctx.value = ctx.n.value

    def exitNode_attributes_def(self, ctx):
        print("node_attr_def", ctx.name.value, ctx.getChildren())

    def exitNode_attribute(self, ctx):
        name = ctx.name.value
        version = ctx.version.value
        n0 = ctx.n0.value
        n1 = ctx.n1.value
        attrs = ctx.attrs.value
        ctx.value = OrderedDict(name = name, version = version, configuredNAD = n0, initialNAD = n1, attrs = attrs)
        print("node_attribute:", ctx.value)

    def exitProtocol_version(self, ctx):
        ctx.value = ctx.s.value

    def exitDiag_address(self, ctx):
        ctx.value = ctx.i.value

    def exitAttributes_def(self, ctx):
        pass

    def exitSupplier_id(self, ctx):
        ctx.value = ctx.i.value

    def exitFunction_id(self, ctx):
        ctx.value = ctx.i.value

    def exitVariant(self, ctx):
        ctx.value = ctx.i.value

    def exitSignal_name(self, ctx):
        ctx.value = ctx.i.value
        print("signal_name", ctx.value)

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
        #(sname = signal_name ':' ssize = signal_size ',' initValue = init_value ',' pub = published_by (',' sub += subscribed_by)* ';')*
        sname = ctx.sname.value
        ssize = ctx.ssize.value
        initValue = ctx.initValue.value
        pub = ctx.pub.value
        sub = [x.value for x in ctx.sub]
        ctx.value = OrderedDict(name = sname, size = ssize, initValue = initValue, pub = pub, sub = sub)
        print("signal_def:", ctx.value)

    def exitSignal_size(self, ctx):
        ctx.value = ctx.i.value

    def exitInit_value(self, ctx):
        scalar = ctx.s.value if ctx.s else None
        array = ctx.a.value if ctx.a else None
        ctx.value = OrderedDict(scalar = scalar, array = array)
        print("init_value:", ctx.value)

    def exitInit_value_scalar(self, ctx):
        ctx.value = ctx.i.value

    def exitInit_value_array(self, ctx):
        ctx.value = [x.value for x in ctx.vs]

    def exitPublished_by(self, ctx):
        ctx.value =  ctx.i.value

    def exitSubscribed_by(self, ctx):
        ctx.value =  ctx.i.value

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
        pass

    def exitEvent_trig_frm_name(self, ctx):
        ctx.value = ctx.i.value

    def exitCollision_resolving_schedule_table(self, ctx):
        ctx.value = ctx.i.value

    def exitDiag_frame_def(self, ctx):
        m = ctx.m.value
        #ms = [x.value for x in ctx.ms]
        s = ctx.s.value
        #ss = [x.value for x in ctx.ss]
        #ctx.value = OrderedDict(m = m, ms = ms, s = s, ss = ss)
        ctx.value = OrderedDict(m = m, s = s)


    def exitSchedule_table_def(self, ctx):
        pass
        #items = [x.value for x in ctx.items]
        #ctx.value = items
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
        #minValue = min_value ',' maxValue = max_value ',' s = scale ',' o = offset (',' t = text_info)?
        minValue = ctx.minValue.value
        maxValue = ctx.maxValue.value
        scale = ctx.scale
        offset = ctx.offset
        ctx.value = OrderedDict(min = minValue, max = maxValue, scale = scale, offset = offset)
        print("pyhs_range: ", ctx.value)

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
        print("scale:", ctx.value)

    def exitOffset(self, ctx):
        ctx.value = ctx.n.value
        print("offset:", ctx.value)

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

