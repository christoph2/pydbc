# Generated from ldf.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
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


    # Visit a parse tree produced by ldfParser#lin_speed_def.
    def visitLin_speed_def(self, ctx:ldfParser.Lin_speed_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#channel_name_def.
    def visitChannel_name_def(self, ctx:ldfParser.Channel_name_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#node_def.
    def visitNode_def(self, ctx:ldfParser.Node_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#node_name.
    def visitNode_name(self, ctx:ldfParser.Node_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#time_base.
    def visitTime_base(self, ctx:ldfParser.Time_baseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#jitter.
    def visitJitter(self, ctx:ldfParser.JitterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#node_attributes_def.
    def visitNode_attributes_def(self, ctx:ldfParser.Node_attributes_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#protocol_version.
    def visitProtocol_version(self, ctx:ldfParser.Protocol_versionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#diag_address.
    def visitDiag_address(self, ctx:ldfParser.Diag_addressContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#attributes_def.
    def visitAttributes_def(self, ctx:ldfParser.Attributes_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#supplier_id.
    def visitSupplier_id(self, ctx:ldfParser.Supplier_idContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#function_id.
    def visitFunction_id(self, ctx:ldfParser.Function_idContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#variant.
    def visitVariant(self, ctx:ldfParser.VariantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_name.
    def visitSignal_name(self, ctx:ldfParser.Signal_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#configurable_frames_20_def.
    def visitConfigurable_frames_20_def(self, ctx:ldfParser.Configurable_frames_20_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#message_id.
    def visitMessage_id(self, ctx:ldfParser.Message_idContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#configurable_frames_21_def.
    def visitConfigurable_frames_21_def(self, ctx:ldfParser.Configurable_frames_21_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#node_composition_def.
    def visitNode_composition_def(self, ctx:ldfParser.Node_composition_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#configuration_name.
    def visitConfiguration_name(self, ctx:ldfParser.Configuration_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#composite_node.
    def visitComposite_node(self, ctx:ldfParser.Composite_nodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#logical_node.
    def visitLogical_node(self, ctx:ldfParser.Logical_nodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_def.
    def visitSignal_def(self, ctx:ldfParser.Signal_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_size.
    def visitSignal_size(self, ctx:ldfParser.Signal_sizeContext):
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


    # Visit a parse tree produced by ldfParser#published_by.
    def visitPublished_by(self, ctx:ldfParser.Published_byContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#subscribed_by.
    def visitSubscribed_by(self, ctx:ldfParser.Subscribed_byContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#diagnostic_signal_def.
    def visitDiagnostic_signal_def(self, ctx:ldfParser.Diagnostic_signal_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_groups_def.
    def visitSignal_groups_def(self, ctx:ldfParser.Signal_groups_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_group_name.
    def visitSignal_group_name(self, ctx:ldfParser.Signal_group_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#group_size.
    def visitGroup_size(self, ctx:ldfParser.Group_sizeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#group_offset.
    def visitGroup_offset(self, ctx:ldfParser.Group_offsetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#frame_def.
    def visitFrame_def(self, ctx:ldfParser.Frame_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#frame_name.
    def visitFrame_name(self, ctx:ldfParser.Frame_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#frame_id.
    def visitFrame_id(self, ctx:ldfParser.Frame_idContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#frame_size.
    def visitFrame_size(self, ctx:ldfParser.Frame_sizeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_offset.
    def visitSignal_offset(self, ctx:ldfParser.Signal_offsetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#sporadic_frame_def.
    def visitSporadic_frame_def(self, ctx:ldfParser.Sporadic_frame_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#sporadic_frame_name.
    def visitSporadic_frame_name(self, ctx:ldfParser.Sporadic_frame_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#event_triggered_frame_def.
    def visitEvent_triggered_frame_def(self, ctx:ldfParser.Event_triggered_frame_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#event_trig_frm_name.
    def visitEvent_trig_frm_name(self, ctx:ldfParser.Event_trig_frm_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#collision_resolving_schedule_table.
    def visitCollision_resolving_schedule_table(self, ctx:ldfParser.Collision_resolving_schedule_tableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#diag_frame_def.
    def visitDiag_frame_def(self, ctx:ldfParser.Diag_frame_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#schedule_table_def.
    def visitSchedule_table_def(self, ctx:ldfParser.Schedule_table_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#schedule_table_name.
    def visitSchedule_table_name(self, ctx:ldfParser.Schedule_table_nameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#command.
    def visitCommand(self, ctx:ldfParser.CommandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#frame_index.
    def visitFrame_index(self, ctx:ldfParser.Frame_indexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#frame_PID.
    def visitFrame_PID(self, ctx:ldfParser.Frame_PIDContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#frame_time.
    def visitFrame_time(self, ctx:ldfParser.Frame_timeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_encoding_type_def.
    def visitSignal_encoding_type_def(self, ctx:ldfParser.Signal_encoding_type_defContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_encoding_type_name.
    def visitSignal_encoding_type_name(self, ctx:ldfParser.Signal_encoding_type_nameContext):
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


    # Visit a parse tree produced by ldfParser#signal_value.
    def visitSignal_value(self, ctx:ldfParser.Signal_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#min_value.
    def visitMin_value(self, ctx:ldfParser.Min_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#max_value.
    def visitMax_value(self, ctx:ldfParser.Max_valueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#scale.
    def visitScale(self, ctx:ldfParser.ScaleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#offset.
    def visitOffset(self, ctx:ldfParser.OffsetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#text_info.
    def visitText_info(self, ctx:ldfParser.Text_infoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ldfParser#signal_representation_def.
    def visitSignal_representation_def(self, ctx:ldfParser.Signal_representation_defContext):
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