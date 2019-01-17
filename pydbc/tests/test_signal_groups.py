
from pydbc.parser import BaseListener, Parser

SG0 = """SIG_GROUP_ 288 Switches 1 : WindowSwitch DoorSwitch;"""

SG1 = """SIG_GROUP_ 2316304896 Serial_number 1 : Serial_number_3 Serial_number_2 Serial_number_1 Serial_number_0;
SIG_GROUP_ 2316304896 Version 1 : Version_2 Version_1 Version_0;
SIG_GROUP_ 2316304896 Part_number 1 : Part_name_3 Part_name_2 Part_name_1 Part_name_0;
SIG_GROUP_ 2316304896 CC_Charging 1 : CC_charging_low CC_charging_high;
SIG_GROUP_ 2316304896 CC_Discharging 1 : CC_discharging_low CC_discharging_high;
SIG_GROUP_ 2316304896 Voltages 1 : Voltage_2 Voltage_1 Voltage_0;
SIG_GROUP_ 2316304896 Coulomb_Count 1 : CC_low CC_high;
"""


class SignalGroups(BaseListener):

    def exitSignalGroups(self, ctx):
        items = [x.value for x in ctx.items]
        ctx.value = items
        self.value = ctx.value

    def exitSignalGroup(self, ctx):
        messageID = ctx.messageID.value
        groupName = ctx.groupName.value
        gvalue = ctx.gvalue.value
        signals = [x.value for x in ctx.signals]
        ctx.value = dict(messageID = messageID, groupName = groupName, gvalue = gvalue, signals = signals)

def test_signal_groups():
    tsg = Parser("dbc", "signalGroups", SignalGroups)
    res = tsg.parseFromString(SG0)
    print(res)
    assert len(res) == 1
    res = res[0]
    assert res["groupName"] == "Switches"
    assert res['gvalue'] == 1
    assert res['messageID'] == 288
    signals = res['signals']
    assert signals[0] == "WindowSwitch"
    assert signals[1] == "DoorSwitch"

