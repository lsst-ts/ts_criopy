from .CustomLabels import PowerOnOffLabel, WarningLabel
from .TimeChart import TimeChart, TimeChartView
from .SALComm import SALCommand
from .StateEnabled import EngineeringButton

from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout
from PySide2.QtCore import Slot
from asyncqt import asyncSlot


def bus(b):
    return chr(ord("A") + b)


class TurnButton(EngineeringButton):
    def __init__(self, m1m3, kind, bus, onOff):
        super().__init__(f"Turn {kind} {bus} {onOff}", m1m3)
        self.m1m3 = m1m3
        self.onOff = onOff

        if kind == "Main":
            self.__commandName = f"turnPowerNetwork{bus}{onOff}"
        else:
            self.__commandName = f"turn{kind}PowerNetwork{bus}{onOff}"

        self.clicked.connect(self.runCommand)

    @SALCommand
    def _turnPower(self, **kwargs):
        return getattr(self.m1m3.remote, f"cmd_turnPower{self.onOff}")

    @asyncSlot()
    async def runCommand(self):
        await self._turnPower(**{self.__commandName: True})


class PowerPageWidget(QWidget):
    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3

        layout = QVBoxLayout()
        dataLayout = QGridLayout()
        warningLayout = QGridLayout()
        commandLayout = QGridLayout()
        plotLayout = QVBoxLayout()
        layout.addLayout(commandLayout)
        layout.addLayout(dataLayout)
        layout.addSpacing(20)
        layout.addLayout(warningLayout)
        layout.addLayout(plotLayout)

        self.setLayout(layout)

        def createButtons(kind, onOff, col):
            for b in range(4):
                but = TurnButton(m1m3, kind, bus(b), onOff)
                commandLayout.addWidget(but, b, col)

        createButtons("Main", "On", 0)
        createButtons("Main", "Off", 1)

        createButtons("Aux", "On", 2)
        createButtons("Aux", "Off", 3)

        self.anyWarningLabel = WarningLabel()
        self.rcpMirrorCellUtility220VAC1StatusLabel = QLabel("UNKNOWN")
        self.rcpCabinetUtility220VACStatusLabel = QLabel("UNKNOWN")
        self.rcpExternalEquipment220VACStatusLabel = QLabel("UNKNOWN")
        self.rcpMirrorCellUtility220VAC2StatusLabel = QLabel("UNKNOWN")
        self.rcpMirrorCellUtility220VAC3StatusLabel = QLabel("UNKNOWN")
        self.powerNetworkARedundancyControlStatusLabel = QLabel("UNKNOWN")
        self.powerNetworkBRedundancyControlStatusLabel = QLabel("UNKNOWN")
        self.powerNetworkCRedundancyControlStatusLabel = QLabel("UNKNOWN")
        self.powerNetworkDRedundancyControlStatusLabel = QLabel("UNKNOWN")
        self.controlsPowerNetworkRedundancyControlStatusLabel = QLabel("UNKNOWN")
        self.powerNetworkAStatusLabel = QLabel("UNKNOWN")
        self.powerNetworkARedundantStatusLabel = QLabel("UNKNOWN")
        self.powerNetworkBStatusLabel = QLabel("UNKNOWN")
        self.powerNetworkBRedundantStatusLabel = QLabel("UNKNOWN")
        self.powerNetworkCStatusLabel = QLabel("UNKNOWN")
        self.powerNetworkCRedundantStatusLabel = QLabel("UNKNOWN")
        self.powerNetworkDStatusLabel = QLabel("UNKNOWN")
        self.powerNetworkDRedundantStatusLabel = QLabel("UNKNOWN")
        self.controlsPowerNetworkStatusLabel = QLabel("UNKNOWN")
        self.controlsPowerNetworkRedundantStatusLabel = QLabel("UNKNOWN")
        self.lightPowerNetworkStatusLabel = QLabel("UNKNOWN")
        self.externalEquipmentPowerNetworkStatusLabel = QLabel("UNKNOWN")
        self.laserTrackerPowerNetworkStatusLabel = QLabel("UNKNOWN")

        self.mainOnOffLabels = []
        self.auxOnOffLabels = []
        self.currentLabels = []

        dataLayout.addWidget(QLabel("<b>Main (ON/OFF)</b>"), 0, 1)
        dataLayout.addWidget(QLabel("<b>Aux (ON/OFF)</b>"), 0, 2)
        dataLayout.addWidget(QLabel("<b>Current (A)</b>"), 0, 3)

        def createLabels(title, row, onOff=True):
            dataLayout.addWidget(QLabel(f"<b>{title}</b>"), row, 0)

            if onOff:
                self.mainOnOffLabels.append(PowerOnOffLabel())
                dataLayout.addWidget(self.mainOnOffLabels[-1], row, 1)

                self.auxOnOffLabels.append(PowerOnOffLabel())
                dataLayout.addWidget(self.auxOnOffLabels[-1], row, 2)

            self.currentLabels.append(QLabel("---"))
            dataLayout.addWidget(self.currentLabels[-1], row, 3)

        for row in range(4):
            createLabels(f"Power Network {bus(row)}", row + 1)

        createLabels("Light Network", 5, False)
        createLabels("Controls Network", 6, False)

        self.chart = TimeChart(
            {"Current (A)": ["A", "B", "C", "D", "Lights", "Controls"]}
        )
        self.chartView = TimeChartView(self.chart)

        row = 0
        col = 0
        warningLayout.addWidget(QLabel("Any Warnings"), row, col)
        warningLayout.addWidget(self.anyWarningLabel, row, col + 1)
        row += 1
        warningLayout.addWidget(QLabel("RCP Utility 220VAC 1 Status"), row, col)
        warningLayout.addWidget(
            self.rcpMirrorCellUtility220VAC1StatusLabel, row, col + 1
        )
        row += 1
        warningLayout.addWidget(QLabel("RCP Utility 220VAC 2 Status"), row, col)
        warningLayout.addWidget(
            self.rcpMirrorCellUtility220VAC2StatusLabel, row, col + 1
        )
        row += 1
        warningLayout.addWidget(QLabel("RCP Utility 220VAC 3 Status"), row, col)
        warningLayout.addWidget(
            self.rcpMirrorCellUtility220VAC3StatusLabel, row, col + 1
        )
        row += 1
        warningLayout.addWidget(QLabel("RCP Cabinet Utility 220VAC Status"), row, col)
        warningLayout.addWidget(self.rcpCabinetUtility220VACStatusLabel, row, col + 1)
        row += 1
        warningLayout.addWidget(
            QLabel("RCP External Equipment 220VAC Status"), row, col
        )
        warningLayout.addWidget(
            self.rcpExternalEquipment220VACStatusLabel, row, col + 1
        )
        row += 1
        warningLayout.addWidget(QLabel("A Redundancy Control Status"), row, col)
        warningLayout.addWidget(
            self.powerNetworkARedundancyControlStatusLabel, row, col + 1
        )

        row = 1
        col = 2
        warningLayout.addWidget(QLabel("B Redundancy Control Status"), row, col)
        warningLayout.addWidget(
            self.powerNetworkBRedundancyControlStatusLabel, row, col + 1
        )
        row += 1
        warningLayout.addWidget(QLabel("C Redundancy Control Status"), row, col)
        warningLayout.addWidget(
            self.powerNetworkCRedundancyControlStatusLabel, row, col + 1
        )
        row += 1
        warningLayout.addWidget(QLabel("D Redundancy Control Status"), row, col)
        warningLayout.addWidget(
            self.powerNetworkDRedundancyControlStatusLabel, row, col + 1
        )
        row += 1
        warningLayout.addWidget(QLabel("Controls Redundancy Control Status"), row, col)
        warningLayout.addWidget(
            self.controlsPowerNetworkRedundancyControlStatusLabel, row, col + 1
        )
        row += 1
        warningLayout.addWidget(QLabel("A Status"), row, col)
        warningLayout.addWidget(self.powerNetworkAStatusLabel, row, col + 1)
        row += 1
        warningLayout.addWidget(QLabel("A Redundant Status"), row, col)
        warningLayout.addWidget(self.powerNetworkARedundantStatusLabel, row, col + 1)

        row = 1
        col = 4
        warningLayout.addWidget(QLabel("B Status"), row, col)
        warningLayout.addWidget(self.powerNetworkBStatusLabel, row, col + 1)
        row += 1
        warningLayout.addWidget(QLabel("B Redundant Status"), row, col)
        warningLayout.addWidget(self.powerNetworkBRedundantStatusLabel, row, col + 1)
        row += 1
        warningLayout.addWidget(QLabel("C Status"), row, col)
        warningLayout.addWidget(self.powerNetworkCStatusLabel, row, col + 1)
        row += 1
        warningLayout.addWidget(QLabel("C Redundant Status"), row, col)
        warningLayout.addWidget(self.powerNetworkCRedundantStatusLabel, row, col + 1)
        row += 1
        warningLayout.addWidget(QLabel("D Status"), row, col)
        warningLayout.addWidget(self.powerNetworkDStatusLabel, row, col + 1)
        row += 1
        warningLayout.addWidget(QLabel("D Redundant Status"), row, col)
        warningLayout.addWidget(self.powerNetworkDRedundantStatusLabel, row, col + 1)

        row = 1
        col = 6
        warningLayout.addWidget(QLabel("Controls Status"), row, col)
        warningLayout.addWidget(self.controlsPowerNetworkStatusLabel, row, col + 1)
        row += 1
        warningLayout.addWidget(QLabel("Controls Redundant Status"), row, col)
        warningLayout.addWidget(
            self.controlsPowerNetworkRedundantStatusLabel, row, col + 1
        )
        row += 1
        warningLayout.addWidget(QLabel("Light Status"), row, col)
        warningLayout.addWidget(self.lightPowerNetworkStatusLabel, row, col + 1)
        row += 1
        warningLayout.addWidget(QLabel("External Equipment Status"), row, col)
        warningLayout.addWidget(
            self.externalEquipmentPowerNetworkStatusLabel, row, col + 1
        )
        row += 1
        warningLayout.addWidget(QLabel("Laser Tracker Status"), row, col)
        warningLayout.addWidget(self.laserTrackerPowerNetworkStatusLabel, row, col + 1)

        plotLayout.addWidget(self.chartView)

        self.m1m3.powerWarning.connect(self.powerWarning)
        self.m1m3.powerStatus.connect(self.powerStatus)
        self.m1m3.powerSupplyData.connect(self.powerSupplyData)

    @Slot(map)
    def powerWarning(self, data):
        self.anyWarningLabel.setValue(data.anyWarning)
        # TODO setWarningLabel(self.rcpMirrorCellUtility220VAC1StatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.RCPMirrorCellUtility220VAC1Status))
        # TODO setWarningLabel(self.rcpCabinetUtility220VACStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.RCPCabinetUtility220VACStatus))
        # TODO setWarningLabel(self.rcpExternalEquipment220VACStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.RCPExternalEquipment220VACStatus))
        # TODO setWarningLabel(self.rcpMirrorCellUtility220VAC2StatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.RCPMirrorCellUtility220VAC2Status))
        # TODO setWarningLabel(self.rcpMirrorCellUtility220VAC3StatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.RCPMirrorCellUtility220VAC3Status))
        # TODO setWarningLabel(self.powerNetworkARedundancyControlStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.PowerNetworkARedundancyControlStatus))
        # TODO setWarningLabel(self.powerNetworkBRedundancyControlStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.PowerNetworkBRedundancyControlStatus))
        # TODO setWarningLabel(self.powerNetworkCRedundancyControlStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.PowerNetworkCRedundancyControlStatus))
        # TODO setWarningLabel(self.powerNetworkDRedundancyControlStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.PowerNetworkDRedundancyControlStatus))
        # TODO setWarningLabel(self.controlsPowerNetworkRedundancyControlStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.ControlsPowerNetworkRedundancyControlStatus))
        # TODO setWarningLabel(self.powerNetworkAStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.PowerNetworkAStatus))
        # TODO setWarningLabel(self.powerNetworkARedundantStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.PowerNetworkARedundantStatus))
        # TODO setWarningLabel(self.powerNetworkBStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.PowerNetworkBStatus))
        # TODO setWarningLabel(self.powerNetworkBRedundantStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.PowerNetworkBRedundantStatus))
        # TODO setWarningLabel(self.powerNetworkCStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.PowerNetworkCStatus))
        # TODO setWarningLabel(self.powerNetworkCRedundantStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.PowerNetworkCRedundantStatus))
        # TODO setWarningLabel(self.powerNetworkDStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.PowerNetworkDStatus))
        # TODO setWarningLabel(self.powerNetworkDRedundantStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.PowerNetworkDRedundantStatus))
        # TODO setWarningLabel(self.controlsPowerNetworkStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.ControlsPowerNetworkStatus))
        # TODO setWarningLabel(self.controlsPowerNetworkRedundantStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.ControlsPowerNetworkRedundantStatus))
        # TODO setWarningLabel(self.lightPowerNetworkStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.LightPowerNetworkStatus))
        # TODO setWarningLabel(self.externalEquipmentPowerNetworkStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.ExternalEquipmentPowerNetworkStatus))
        # TODO setWarningLabel(self.laserTrackerPowerNetworkStatusLabel, BitHelper.get(data.powerSystemFlags, PowerSystemFlags.LaserTrackerPowerNetworkStatus))

    @Slot(map)
    def powerStatus(self, data):
        for b in range(4):
            self.mainOnOffLabels[b].setValue(
                getattr(data, f"powerNetwork{bus(b)}CommandedOn")
            )
            self.auxOnOffLabels[b].setValue(
                getattr(data, f"auxPowerNetwork{bus(b)}CommandedOn")
            )

    @Slot(map)
    def powerSupplyData(self, data):
        for b in range(4):
            name = f"powerNetwork{chr(ord('A') + b)}Current"
            self.currentLabels[b].setText(f"{getattr(data, name):0.3f}")

        self.currentLabels[4].setText(f"{data.lightPowerNetworkCurrent:0.3f}")
        self.currentLabels[5].setText(f"{data.controlsPowerNetworkCurrent:0.3f}")

        self.chart.append(
            data.timestamp,
            [
                data.powerNetworkACurrent,
                data.powerNetworkBCurrent,
                data.powerNetworkCCurrent,
                data.powerNetworkDCurrent,
                data.lightPowerNetworkCurrent,
                data.controlsPowerNetworkCurrent,
            ],
        )
