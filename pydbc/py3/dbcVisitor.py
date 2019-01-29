# Generated from dbc.g4 by ANTLR 4.7
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .dbcParser import dbcParser
else:
    from dbcParser import dbcParser

# This class defines a complete generic visitor for a parse tree produced by dbcParser.

class dbcVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by dbcParser#dbcfile.
    def visitDbcfile(self, ctx:dbcParser.DbcfileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#messageTransmitters.
    def visitMessageTransmitters(self, ctx:dbcParser.MessageTransmittersContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#messageTransmitter.
    def visitMessageTransmitter(self, ctx:dbcParser.MessageTransmitterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#signalExtendedValueTypeList.
    def visitSignalExtendedValueTypeList(self, ctx:dbcParser.SignalExtendedValueTypeListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#signalExtendedValueType.
    def visitSignalExtendedValueType(self, ctx:dbcParser.SignalExtendedValueTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#messages.
    def visitMessages(self, ctx:dbcParser.MessagesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#message.
    def visitMessage(self, ctx:dbcParser.MessageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#signal.
    def visitSignal(self, ctx:dbcParser.SignalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#receiver.
    def visitReceiver(self, ctx:dbcParser.ReceiverContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#transmitter.
    def visitTransmitter(self, ctx:dbcParser.TransmitterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#multiplexerIndicator.
    def visitMultiplexerIndicator(self, ctx:dbcParser.MultiplexerIndicatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#valueTables.
    def visitValueTables(self, ctx:dbcParser.ValueTablesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#valueTable.
    def visitValueTable(self, ctx:dbcParser.ValueTableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#valueDescription.
    def visitValueDescription(self, ctx:dbcParser.ValueDescriptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#nodes.
    def visitNodes(self, ctx:dbcParser.NodesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#bitTiming.
    def visitBitTiming(self, ctx:dbcParser.BitTimingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#newSymbols.
    def visitNewSymbols(self, ctx:dbcParser.NewSymbolsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#version.
    def visitVersion(self, ctx:dbcParser.VersionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#valueDescriptions.
    def visitValueDescriptions(self, ctx:dbcParser.ValueDescriptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#specializedValueDescription.
    def visitSpecializedValueDescription(self, ctx:dbcParser.SpecializedValueDescriptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#environmentVariables.
    def visitEnvironmentVariables(self, ctx:dbcParser.EnvironmentVariablesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#environmentVariable.
    def visitEnvironmentVariable(self, ctx:dbcParser.EnvironmentVariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#accessNodes.
    def visitAccessNodes(self, ctx:dbcParser.AccessNodesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#environmentVariablesData.
    def visitEnvironmentVariablesData(self, ctx:dbcParser.EnvironmentVariablesDataContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#environmentVariableData.
    def visitEnvironmentVariableData(self, ctx:dbcParser.EnvironmentVariableDataContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#signalTypes.
    def visitSignalTypes(self, ctx:dbcParser.SignalTypesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#signalType.
    def visitSignalType(self, ctx:dbcParser.SignalTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#comments.
    def visitComments(self, ctx:dbcParser.CommentsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#comment.
    def visitComment(self, ctx:dbcParser.CommentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeDefinitions.
    def visitAttributeDefinitions(self, ctx:dbcParser.AttributeDefinitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeDefinition.
    def visitAttributeDefinition(self, ctx:dbcParser.AttributeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#relativeAttributeDefinitions.
    def visitRelativeAttributeDefinitions(self, ctx:dbcParser.RelativeAttributeDefinitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#relativeAttributeDefinition.
    def visitRelativeAttributeDefinition(self, ctx:dbcParser.RelativeAttributeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeValueType.
    def visitAttributeValueType(self, ctx:dbcParser.AttributeValueTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeDefaults.
    def visitAttributeDefaults(self, ctx:dbcParser.AttributeDefaultsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeDefault.
    def visitAttributeDefault(self, ctx:dbcParser.AttributeDefaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#relativeAttributeDefaults.
    def visitRelativeAttributeDefaults(self, ctx:dbcParser.RelativeAttributeDefaultsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#relativeAttributeDefault.
    def visitRelativeAttributeDefault(self, ctx:dbcParser.RelativeAttributeDefaultContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeValue.
    def visitAttributeValue(self, ctx:dbcParser.AttributeValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeValues.
    def visitAttributeValues(self, ctx:dbcParser.AttributeValuesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeValueForObject.
    def visitAttributeValueForObject(self, ctx:dbcParser.AttributeValueForObjectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#relativeAttributeValues.
    def visitRelativeAttributeValues(self, ctx:dbcParser.RelativeAttributeValuesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#relativeAttributeValueForObject.
    def visitRelativeAttributeValueForObject(self, ctx:dbcParser.RelativeAttributeValueForObjectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#signalGroups.
    def visitSignalGroups(self, ctx:dbcParser.SignalGroupsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#signalGroup.
    def visitSignalGroup(self, ctx:dbcParser.SignalGroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#categoryDefinitions.
    def visitCategoryDefinitions(self, ctx:dbcParser.CategoryDefinitionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#categoryDefinition.
    def visitCategoryDefinition(self, ctx:dbcParser.CategoryDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#categories.
    def visitCategories(self, ctx:dbcParser.CategoriesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#category.
    def visitCategory(self, ctx:dbcParser.CategoryContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#intValue.
    def visitIntValue(self, ctx:dbcParser.IntValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#floatValue.
    def visitFloatValue(self, ctx:dbcParser.FloatValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#number.
    def visitNumber(self, ctx:dbcParser.NumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#stringValue.
    def visitStringValue(self, ctx:dbcParser.StringValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#identifierValue.
    def visitIdentifierValue(self, ctx:dbcParser.IdentifierValueContext):
        return self.visitChildren(ctx)



del dbcParser