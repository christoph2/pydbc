
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
        items = [x.value for x in ctx.items]
        ctx.value = items
        print("node_attr_def", ctx.value)

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
        sid = ctx.sid.value
        fid = ctx.fid.value
        v = ctx.v.value if ctx.v else None
        sn0 = ctx.sn0.value
        sn1s = [x.value for x in ctx.sn1s]
        cf = ctx.cf.value
        p2Min = ctx.p2Min.value
        stMin = ctx.stMin.value
        nAs = ctx.nAs.value
        nCr = ctx.nCr.value
        ctx.value = OrderedDict(supplierID = sid, functionID = fid, variant = v, responseErrorSignal = sn0, faultStateSignals = sn1s,
                p2Min = p2Min, stMin = stMin, nAs = nAs, nCr = nCr, configurableFrames = cf
        )

    def exitSupplier_id(self, ctx):
        ctx.value = ctx.i.value

    def exitFunction_id(self, ctx):
        ctx.value = ctx.i.value

    def exitVariant(self, ctx):
        ctx.value = ctx.i.value

    def exitSignal_name(self, ctx):
        ctx.value = ctx.i.value
        #print("signal_name", ctx.value)

    def exitConfigurable_frames(self, ctx):
        ctx.value = [x.value for x in ctx.frames]

    def exitConfigurable_frame(self, ctx):
        fname = ctx.fname.value
        mid = ctx.mid.value if ctx.mid else None
        ctx.value = OrderedDict(frameName = fname, messageID = mid)

    def exitMessage_id(self, ctx):
        ctx.value = ctx.i.value

    def exitNode_composition_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitConfiguration(self, ctx):
        cname = ctx.cname.value
        items = [x.value for x in ctx.items]
        ctx.value = OrderedDict(configurationName = cname, items = items)

    def exitConfiguration_item(self, ctx):
        cnode = ctx.cnode.value
        lnodes = [x.value for x in ctx.lnodes]
        ctx.value = OrderedDict(compositeNode = cnode, logicalNodes = lnodes)

    def exitConfiguration_name(self, ctx):
        ctx.value = ctx.i.value

    def exitComposite_node(self, ctx):
        ctx.value = ctx.i.value

    def exitLogical_node(self, ctx):
        ctx.value = ctx.i.value

    def exitSignal_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitSignal_item(self, ctx):
        sname = ctx.sname.value
        ssize = ctx.ssize.value
        initValue = ctx.initValue.value
        pub = ctx.pub.value
        sub = [x.value for x in ctx.sub]
        ctx.value = OrderedDict(name = sname, size = ssize, initValue = initValue, publishedBy = pub, subscribedBy = sub)
        print("signal_item:", ctx.value)

    def exitSignal_size(self, ctx):
        ctx.value = ctx.i.value

    def exitInit_value(self, ctx):
        scalar = ctx.s.value if ctx.s else None
        array = ctx.a.value if ctx.a else None
        ctx.value = OrderedDict(scalar = scalar, array = array)

    def exitInit_value_scalar(self, ctx):
        ctx.value = ctx.i.value

    def exitInit_value_array(self, ctx):
        ctx.value = [x.value for x in ctx.vs]

    def exitPublished_by(self, ctx):
        ctx.value =  ctx.i.value

    def exitSubscribed_by(self, ctx):
        ctx.value =  ctx.i.value

    def exitDiagnostic_signal_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitDiagnostic_item(self, ctx):
        name = ctx.name.value
        size = ctx.size.value
        initValue = ctx.initValue.value
        ctx.value = OrderedDict(name = name, size = size, initValue = initValue)

    def exitSignal_groups_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitSignal_group(self, ctx):
        sgname = ctx.sgname.value
        gsize = ctx.gsize.value
        items = [x.value for x in ctx.items]
        ctx.value = OrderedDict(signalGroupName = sgname, groupSize = gsize, items = items)

    def exitSignal_group_item(self, ctx):
        sname = ctx.sname.value
        goffs = ctx.goffs.value
        ctx.value = OrderedDict(signalName = sname, groupOffset = goffs)

    def exitSignal_group_name(self, ctx):
        ctx.value = ctx.i.value

    def exitGroup_size(self, ctx):
        ctx.value = ctx.i.value

    def exitGroup_offset(self, ctx):
        ctx.value = ctx.i.value

    def exitFrame_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitFrame_item(self, ctx):
        fname = ctx.fname.value
        fid = ctx.fid.value
        p = ctx.p.value
        fsize = ctx.fsize.value
        items = [x.value for x in ctx.items]
        ctx.value = OrderedDict(frameName = fname, frameID = fid, publishedBy = p, frameSize = fsize, signals = items)

    def exitFrame_signal(self, ctx):
        sname = ctx.sname.value
        soffs = ctx.soffs.value
        ctx.value = OrderedDict(signalName = sname, signalOffset = soffs)

    def exitFrame_name(self, ctx):
        ctx.value = ctx.i.value

    def exitFrame_id(self, ctx):
        ctx.value = ctx.i.value

    def exitFrame_size(self, ctx):
        ctx.value = ctx.i.value

    def exitSignal_offset(self, ctx):
        ctx.value = ctx.i.value

    def exitSporadic_frame_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitSporadic_frame_item(self, ctx):
        name = ctx.sfn.value
        fnames = [x.value for x in ctx.names]
        ctx.value = OrderedDict(sporadicFrameName = name, frameNames = fnames)

    def exitSporadic_frame_name(self, ctx):
        ctx.value = ctx.i.value

    def exitEvent_triggered_frame_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitEvent_triggered_frame_item(self, ctx):
        e = ctx.e.value
        c = ctx.c.value
        fid = ctx.fid.value
        items = [x.value for x in ctx.items]
        ctx.value = OrderedDict(frameName = e, frameID = fid, scheduleTable = c, frameNames = items)

    def exitEvent_trig_frm_name(self, ctx):
        ctx.value = ctx.i.value

    def exitCollision_resolving_schedule_table(self, ctx):
        ctx.value = ctx.i.value

    def exitDiag_frame_def(self, ctx):
        mid = ctx.mid.value
        sid = ctx.sid.value
        mitems = [x.value for x in ctx.mitems]
        sitems = [x.value for x in ctx.sitems]
        ctx.value = OrderedDict(masterID = mid, slaveID = sid, masterSignals = mitems, slaveSignals = sitems)

    def exitDiag_frame_item(self, ctx):
        sname = ctx.sname.value
        soffs = ctx.soffs.value
        ctx.value = OrderedDict(signalName = sname, signalOffset = soffs)

    def exitSchedule_table_def(self, ctx):
        ctx.value = [x.value for x in ctx.items]

    def exitSchedule_table_entry(self, ctx):
        s = ctx.s.value
        items = [x.value for x in ctx.items]
        ctx.value = OrderedDict(name = s, commands = items)

    def exitSchedule_table_command(self, ctx):
        c = ctx.c.value
        f = ctx.f.value
        ctx.value = OrderedDict(command = c, frameTime = f)

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
        items = [x.value for x in ctx.items]
        ctx.value = items

    def exitSignal_encoding_entry(self, ctx):
        s = ctx.s.value
        items = [x.value for x in ctx.items]
        ctx.value = OrderedDict(name = s, values = items)

    def exitSignal_encoding_value(self, ctx):
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
        ctx.value = OrderedDict(value = value, valueType = vtype)


    def exitSignal_encoding_type_name(self, ctx):
        ctx.value = ctx.i.value

    def exitLogical_value(self, ctx):
        pass

    def exitPhysical_range(self, ctx):
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
        items = [x.value for x in ctx.items]
        ctx.value = items

    def exitSignal_representation_entry(self, ctx):
        enc = ctx.enc.value
        names = [x.value for x in ctx.names]
        ctx.value = OrderedDict(name = enc, signalNames = names)

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

