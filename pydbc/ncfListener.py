# Generated from ncf.g4 by ANTLR 4.7

import antlr4

class NcfListener(antlr4.ParseTreeListener):

    def exitToplevel(self, ctx):
        self. value = "hello"

    def exitLanguage_version(self, ctx):
        print("language_ver", ctx.s.value)

    def exitNode_definition(self, ctx):
        print("node_def", ctx.name.value, ctx.g.value, ctx.d.value, ctx.f.value)

    def exitNode_name(self, ctx):
        print("node_name", ctx.i.value)
        ctx.value = ctx.i.value

    def exitGeneral_definition(self, ctx):
        print("gen_def", ctx.pv.value)

    def exitProtocol_version(self, ctx):
        ctx.value = ctx.s.value

    def exitSupplier_id(self, ctx):
        ctx.value = ctx.i.value

    def exitFunction_id(self, ctx):
        ctx.value = ctx.i.value

    def exitVariant_id(self, ctx):
        ctx.value = ctx.i.value

    def exitBitrate_definition(self, ctx):
        pass

    def exitBitrate(self, ctx):
        pass

    def exitDiagnostic_definition(self, ctx):
        pass

    def exitFrame_definition(self, ctx):
        print("frame_def", ctx.frames)

    def exitSingle_frame(self, ctx):
        print("single_frame", ctx.d)

    def exitFrame_kind(self, ctx):
        print("frame_kind")

    def exitFrame_name(self, ctx):
        print("frame_name")

    def exitFrame_properties(self, ctx):
        pass

    def exitSignal_definition(self, ctx):
        pass

    def exitSignal_name(self, ctx):
        pass

    def exitSignal_properties(self, ctx):
        pass

    def exitInit_value(self, ctx):
        pass

    def exitInit_value_scalar(self, ctx):
        pass

    def exitInit_value_array(self, ctx):
        pass

    def exitEncoding_definition(self, ctx):
        pass

    def exitEncoding_name(self, ctx):
        pass

    def exitLogical_value(self, ctx):
        pass

    def exitPhysical_range(self, ctx):
        pass

    def exitBcd_value(self, ctx):
        pass

    def exitAscii_value(self, ctx):
        pass

    def exitSignal_value(self, ctx):
        pass

    def exitMin_value(self, ctx):
        pass

    def exitMax_value(self, ctx):
        pass

    def exitScale(self, ctx):
        pass

    def exitOffset(self, ctx):
        pass

    def exitText_info(self, ctx):
        pass

    def exitStatus_management(self, ctx):
        pass

    def exitPublished_signal(self, ctx):
        pass

    def exitFree_text_definition(self, ctx):
        pass

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

