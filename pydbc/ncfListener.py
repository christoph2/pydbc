# Generated from ncf.g4 by ANTLR 4.7
from antlr4 import *


class ncfListener(ParseTreeListener):

    def exitToplevel(self, ctx):
        pass

    def exitLanguage_version(self, ctx):
        pass

    def exitNode_definition(self, ctx):
        pass

    def exitNode_name(self, ctx):
        pass

    def exitGeneral_definition(self, ctx):
        pass

    def exitProtocol_version(self, ctx):
        pass

    def exitSupplier_id(self, ctx):
        pass

    def exitFunction_id(self, ctx):
        pass

    def exitVariant_id(self, ctx):
        pass

    def exitBitrate_definition(self, ctx):
        pass

    def exitBitrate(self, ctx):
        pass

    def exitDiagnostic_definition(self, ctx):
        pass

    def exitFrame_definition(self, ctx):
        pass

    def exitSingle_frame(self, ctx):
        pass

    def exitFrame_kind(self, ctx):
        pass

    def exitFrame_name(self, ctx):
        pass

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

