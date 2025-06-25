# Generated from ldf.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .ldfParser import ldfParser
else:
    from ldfParser import ldfParser

# This class defines a complete generic visitor for a parse tree produced by ldfParser.

class ldfVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ldfParser#lin_description_file.
    def visitLin_description_file(self, ctx:ldfParser.Lin_description_fileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#lin_protocol_version_def.
    def visitLin_protocol_version_def(self, ctx:ldfParser.Lin_protocol_version_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#lin_language_version_def.
    def visitLin_language_version_def(self, ctx:ldfParser.Lin_language_version_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#lin_file_revision_def.
    def visitLin_file_revision_def(self, ctx:ldfParser.Lin_file_revision_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#lin_speed_def.
    def visitLin_speed_def(self, ctx:ldfParser.Lin_speed_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#channel_name_def.
    def visitChannel_name_def(self, ctx:ldfParser.Channel_name_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#node_def.
    def visitNode_def(self, ctx:ldfParser.Node_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#node_attributes_def.
    def visitNode_attributes_def(self, ctx:ldfParser.Node_attributes_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#node_attribute.
    def visitNode_attribute(self, ctx:ldfParser.Node_attributeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#attributes_def.
    def visitAttributes_def(self, ctx:ldfParser.Attributes_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#configurable_frames.
    def visitConfigurable_frames(self, ctx:ldfParser.Configurable_framesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#configurable_frame.
    def visitConfigurable_frame(self, ctx:ldfParser.Configurable_frameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#node_composition_def.
    def visitNode_composition_def(self, ctx:ldfParser.Node_composition_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#configuration.
    def visitConfiguration(self, ctx:ldfParser.ConfigurationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#configuration_item.
    def visitConfiguration_item(self, ctx:ldfParser.Configuration_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_def.
    def visitSignal_def(self, ctx:ldfParser.Signal_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_item.
    def visitSignal_item(self, ctx:ldfParser.Signal_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#init_value.
    def visitInit_value(self, ctx:ldfParser.Init_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#init_value_scalar.
    def visitInit_value_scalar(self, ctx:ldfParser.Init_value_scalarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#init_value_array.
    def visitInit_value_array(self, ctx:ldfParser.Init_value_arrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#diagnostic_signal_def.
    def visitDiagnostic_signal_def(self, ctx:ldfParser.Diagnostic_signal_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#diagnostic_item.
    def visitDiagnostic_item(self, ctx:ldfParser.Diagnostic_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_groups_def.
    def visitSignal_groups_def(self, ctx:ldfParser.Signal_groups_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_group.
    def visitSignal_group(self, ctx:ldfParser.Signal_groupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_group_item.
    def visitSignal_group_item(self, ctx:ldfParser.Signal_group_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#frame_def.
    def visitFrame_def(self, ctx:ldfParser.Frame_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#frame_item.
    def visitFrame_item(self, ctx:ldfParser.Frame_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#frame_signal.
    def visitFrame_signal(self, ctx:ldfParser.Frame_signalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#sporadic_frame_def.
    def visitSporadic_frame_def(self, ctx:ldfParser.Sporadic_frame_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#sporadic_frame_item.
    def visitSporadic_frame_item(self, ctx:ldfParser.Sporadic_frame_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#event_triggered_frame_def.
    def visitEvent_triggered_frame_def(self, ctx:ldfParser.Event_triggered_frame_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#event_triggered_frame_item.
    def visitEvent_triggered_frame_item(self, ctx:ldfParser.Event_triggered_frame_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#diag_frame_def.
    def visitDiag_frame_def(self, ctx:ldfParser.Diag_frame_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#diag_frame_item.
    def visitDiag_frame_item(self, ctx:ldfParser.Diag_frame_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#schedule_table_def.
    def visitSchedule_table_def(self, ctx:ldfParser.Schedule_table_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#schedule_table_entry.
    def visitSchedule_table_entry(self, ctx:ldfParser.Schedule_table_entryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#schedule_table_command.
    def visitSchedule_table_command(self, ctx:ldfParser.Schedule_table_commandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#command.
    def visitCommand(self, ctx:ldfParser.CommandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_encoding_type_def.
    def visitSignal_encoding_type_def(self, ctx:ldfParser.Signal_encoding_type_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_encoding_entry.
    def visitSignal_encoding_entry(self, ctx:ldfParser.Signal_encoding_entryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_encoding_value.
    def visitSignal_encoding_value(self, ctx:ldfParser.Signal_encoding_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#logical_value.
    def visitLogical_value(self, ctx:ldfParser.Logical_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#physical_range.
    def visitPhysical_range(self, ctx:ldfParser.Physical_rangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#bcd_value.
    def visitBcd_value(self, ctx:ldfParser.Bcd_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#ascii_value.
    def visitAscii_value(self, ctx:ldfParser.Ascii_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_representation_def.
    def visitSignal_representation_def(self, ctx:ldfParser.Signal_representation_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_representation_entry.
    def visitSignal_representation_entry(self, ctx:ldfParser.Signal_representation_entryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#intValue.
    def visitIntValue(self, ctx:ldfParser.IntValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#floatValue.
    def visitFloatValue(self, ctx:ldfParser.FloatValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#number.
    def visitNumber(self, ctx:ldfParser.NumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#stringValue.
    def visitStringValue(self, ctx:ldfParser.StringValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#identifierValue.
    def visitIdentifierValue(self, ctx:ldfParser.IdentifierValueContext):
        return self.visitChildren(ctx)



del ldfParser