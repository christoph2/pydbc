# Generated from ncf.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .ncfParser import ncfParser
else:
    from ncfParser import ncfParser

# This class defines a complete generic visitor for a parse tree produced by ncfParser.

class ncfVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ncfParser#toplevel.
    def visitToplevel(self, ctx:ncfParser.ToplevelContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#language_version.
    def visitLanguage_version(self, ctx:ncfParser.Language_versionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#node_definition.
    def visitNode_definition(self, ctx:ncfParser.Node_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#node_name.
    def visitNode_name(self, ctx:ncfParser.Node_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#general_definition.
    def visitGeneral_definition(self, ctx:ncfParser.General_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#protocol_version.
    def visitProtocol_version(self, ctx:ncfParser.Protocol_versionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#supplier_id.
    def visitSupplier_id(self, ctx:ncfParser.Supplier_idContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#function_id.
    def visitFunction_id(self, ctx:ncfParser.Function_idContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#variant_id.
    def visitVariant_id(self, ctx:ncfParser.Variant_idContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#bitrate_definition.
    def visitBitrate_definition(self, ctx:ncfParser.Bitrate_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#bitrate.
    def visitBitrate(self, ctx:ncfParser.BitrateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#diagnostic_definition.
    def visitDiagnostic_definition(self, ctx:ncfParser.Diagnostic_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#frame_definition.
    def visitFrame_definition(self, ctx:ncfParser.Frame_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#single_frame.
    def visitSingle_frame(self, ctx:ncfParser.Single_frameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#frame_kind.
    def visitFrame_kind(self, ctx:ncfParser.Frame_kindContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#frame_name.
    def visitFrame_name(self, ctx:ncfParser.Frame_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#frame_properties.
    def visitFrame_properties(self, ctx:ncfParser.Frame_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#signal_definition.
    def visitSignal_definition(self, ctx:ncfParser.Signal_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#signal_name.
    def visitSignal_name(self, ctx:ncfParser.Signal_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#signal_properties.
    def visitSignal_properties(self, ctx:ncfParser.Signal_propertiesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#init_value.
    def visitInit_value(self, ctx:ncfParser.Init_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#init_value_scalar.
    def visitInit_value_scalar(self, ctx:ncfParser.Init_value_scalarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#init_value_array.
    def visitInit_value_array(self, ctx:ncfParser.Init_value_arrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#encoding_definition.
    def visitEncoding_definition(self, ctx:ncfParser.Encoding_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#encoding_name.
    def visitEncoding_name(self, ctx:ncfParser.Encoding_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#logical_value.
    def visitLogical_value(self, ctx:ncfParser.Logical_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#physical_range.
    def visitPhysical_range(self, ctx:ncfParser.Physical_rangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#bcd_value.
    def visitBcd_value(self, ctx:ncfParser.Bcd_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#ascii_value.
    def visitAscii_value(self, ctx:ncfParser.Ascii_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#signal_value.
    def visitSignal_value(self, ctx:ncfParser.Signal_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#min_value.
    def visitMin_value(self, ctx:ncfParser.Min_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#max_value.
    def visitMax_value(self, ctx:ncfParser.Max_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#scale.
    def visitScale(self, ctx:ncfParser.ScaleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#offset.
    def visitOffset(self, ctx:ncfParser.OffsetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#text_info.
    def visitText_info(self, ctx:ncfParser.Text_infoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#status_management.
    def visitStatus_management(self, ctx:ncfParser.Status_managementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#published_signal.
    def visitPublished_signal(self, ctx:ncfParser.Published_signalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#free_text_definition.
    def visitFree_text_definition(self, ctx:ncfParser.Free_text_definitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#intValue.
    def visitIntValue(self, ctx:ncfParser.IntValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#floatValue.
    def visitFloatValue(self, ctx:ncfParser.FloatValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#number.
    def visitNumber(self, ctx:ncfParser.NumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#stringValue.
    def visitStringValue(self, ctx:ncfParser.StringValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ncfParser#identifierValue.
    def visitIdentifierValue(self, ctx:ncfParser.IdentifierValueContext):
        return self.visitChildren(ctx)



del ncfParser