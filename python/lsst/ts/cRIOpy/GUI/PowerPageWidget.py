from .CustomLabels import PowerOnOffLabel
from .TimeChart import TimeChart, TimeChartView
from .SALComm import SALCommand
from .StateEnabled import EngineeringButton
from .WarningsGrid import WarningsGrid

from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout, QSpacerItem
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
        commandLayout = QGridLayout()
        plotLayout = QVBoxLayout()

        def createButtons(kind, onOff, col):
            ret = []
            for b in range(4):
                ret.append(TurnButton(m1m3, kind, bus(b), onOff))
                commandLayout.addWidget(ret[-1], b, col)
            return ret

        self.mainOnButtons = createButtons("Main", "On", 0)
        self.mainOffButtons = createButtons("Main", "Off", 1)

        self.auxOnButtons = createButtons("Aux", "On", 2)
        self.auxOffButtons = createButtons("Aux", "Off", 3)

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

        self.mainCommandedLabels = []
        self.mainOutputLabels = []
        self.auxCommandedLabels = []
        self.auxOutputLabels = []
        self.currentLabels = []

        dataLayout.addWidget(QLabel("<b>Main</b>"), 0, 1)
        dataLayout.addWidget(QLabel("Output"), 0, 2)
        dataLayout.addWidget(QLabel("<b>Aux</b>"), 0, 3)
        dataLayout.addWidget(QLabel("Output"), 0, 4)
        dataLayout.addWidget(QLabel("<b>Current (A)</b>"), 0, 5)

        dataLayout.addItem(QSpacerItem(1, 1), 0, 6, -1, 1)

        dataLayout.setColumnStretch(0, 1)
        dataLayout.setColumnStretch(5, 1)
        dataLayout.setColumnStretch(6, 2)

        def createLabels(title, row, onOff=True):
            dataLayout.addWidget(QLabel(f"<b>{title}</b>"), row, 0)

            if onOff:
                self.mainCommandedLabels.append(PowerOnOffLabel())
                self.mainOutputLabels.append(PowerOnOffLabel())
                dataLayout.addWidget(self.mainCommandedLabels[-1], row, 1)
                dataLayout.addWidget(self.mainOutputLabels[-1], row, 2)

                self.auxCommandedLabels.append(PowerOnOffLabel())
                self.auxOutputLabels.append(PowerOnOffLabel())
                dataLayout.addWidget(self.auxCommandedLabels[-1], row, 3)
                dataLayout.addWidget(self.auxOutputLabels[-1], row, 4)

            self.currentLabels.append(QLabel("---"))
            dataLayout.addWidget(self.currentLabels[-1], row, 5)

        for row in range(4):
            createLabels(f"Power Network {bus(row)}", row + 1)

        createLabels("Light Network", 5, False)
        createLabels("Controls Network", 6, False)

        self.chart = TimeChart(
            {"Current (A)": ["A", "B", "C", "D", "Lights", "Controls"]}
        )
        self.chartView = TimeChartView(self.chart)

        warningGrid = WarningsGrid(
            {
                "powerNetworkAOutputMismatch": "Main A Mismatch",
                "powerNetworkBOutputMismatch": "Main B Mismatch",
                "powerNetworkCOutputMismatch": "Main C Mismatch",
                "powerNetworkDOutputMismatch": "Main D Mismatch",
                "auxPowerNetworkAOutputMismatch": "Aux A Mismatch",
                "auxPowerNetworkBOutputMismatch": "Aux B Mismatch",
                "auxPowerNetworkCOutputMismatch": "Aux C Mismatch",
                "auxPowerNetworkDOutputMismatch": "Aux D Mismatch",
            },
            self.m1m3.powerWarning,
            2,
        )

        plotLayout.addWidget(self.chartView)

        layout.addLayout(commandLayout)
        layout.addLayout(dataLayout)
        layout.addSpacing(20)
        layout.addWidget(warningGrid)
        layout.addLayout(plotLayout)

        self.setLayout(layout)

        self.m1m3.powerStatus.connect(self.powerStatus)
        self.m1m3.powerSupplyData.connect(self.powerSupplyData)

    @Slot(map)
    def powerStatus(self, data):
        for b in range(4):
            mainCmd = getattr(data, f"powerNetwork{bus(b)}CommandedOn")
            mainOut = getattr(data, f"powerNetwork{bus(b)}OutputOn")
            self.mainOnButtons[b].setDisabled(mainCmd)
            self.mainOffButtons[b].setEnabled(mainCmd)
            self.mainCommandedLabels[b].setValue(mainCmd)
            self.mainOutputLabels[b].setValue(mainOut)

            auxCmd = getattr(data, f"auxPowerNetwork{bus(b)}CommandedOn")
            auxOut = getattr(data, f"auxPowerNetwork{bus(b)}OutputOn")
            self.auxOnButtons[b].setDisabled(mainCmd)
            self.auxOffButtons[b].setEnabled(mainCmd)
            self.auxCommandedLabels[b].setValue(auxCmd)
            self.auxOutputLabels[b].setValue(auxOut)

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
