# Generated from dbc.g4 by ANTLR 4.7
from antlr4 import *

# This class defines a complete generic visitor for a parse tree produced by dbcParser.

class dbcVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by dbcParser#dbcfile.
    def visitDbcfile(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#messageTransmitters.
    def visitMessageTransmitters(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#messageTransmitter.
    def visitMessageTransmitter(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#signalExtendedValueTypeList.
    def visitSignalExtendedValueTypeList(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#signalExtendedValueType.
    def visitSignalExtendedValueType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#messages.
    def visitMessages(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#message.
    def visitMessage(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#signal.
    def visitSignal(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#receiver.
    def visitReceiver(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#transmitter.
    def visitTransmitter(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#multiplexerIndicator.
    def visitMultiplexerIndicator(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#valueTables.
    def visitValueTables(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#valueTable.
    def visitValueTable(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#valueDescription.
    def visitValueDescription(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#nodes.
    def visitNodes(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#bitTiming.
    def visitBitTiming(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#newSymbols.
    def visitNewSymbols(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#version.
    def visitVersion(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#valueDescriptions.
    def visitValueDescriptions(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#specializedValueDescription.
    def visitSpecializedValueDescription(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#environmentVariables.
    def visitEnvironmentVariables(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#environmentVariable.
    def visitEnvironmentVariable(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#accessNodes.
    def visitAccessNodes(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#environmentVariablesData.
    def visitEnvironmentVariablesData(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#environmentVariableData.
    def visitEnvironmentVariableData(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#signalTypes.
    def visitSignalTypes(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#signalType.
    def visitSignalType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#comments.
    def visitComments(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#comment.
    def visitComment(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeDefinitions.
    def visitAttributeDefinitions(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeDefinition.
    def visitAttributeDefinition(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#customAttributeDefinitions.
    def visitCustomAttributeDefinitions(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#customAttributeDefinition.
    def visitCustomAttributeDefinition(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeValueType.
    def visitAttributeValueType(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeDefaults.
    def visitAttributeDefaults(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeDefault.
    def visitAttributeDefault(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#customAttributeDefaults.
    def visitCustomAttributeDefaults(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#customAttributeDefault.
    def visitCustomAttributeDefault(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeValue.
    def visitAttributeValue(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeValues.
    def visitAttributeValues(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#attributeValueForObject.
    def visitAttributeValueForObject(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#customAttributeValues.
    def visitCustomAttributeValues(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#customAttributeValueForObject.
    def visitCustomAttributeValueForObject(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#categoryDefinitions.
    def visitCategoryDefinitions(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#categoryDefinition.
    def visitCategoryDefinition(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#categories.
    def visitCategories(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#category.
    def visitCategory(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#intValue.
    def visitIntValue(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#floatValue.
    def visitFloatValue(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#number.
    def visitNumber(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#stringValue.
    def visitStringValue(self, ctx):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by dbcParser#identifierValue.
    def visitIdentifierValue(self, ctx):
        return self.visitChildren(ctx)


