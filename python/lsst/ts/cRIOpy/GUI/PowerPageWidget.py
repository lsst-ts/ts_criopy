from .CustomLabels import PowerOnOffLabel, WarningLabel
from .TimeChart import TimeChart, TimeChartView
from .SALComm import SALCommand
from .StateEnabled import EngineeringButton
from .StatusGrid import StatusGrid

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
        self.mainMismatchLabels = []

        self.auxCommandedLabels = []
        self.auxOutputLabels = []
        self.auxMismatchLabels = []

        self.currentLabels = []

        dataLayout.addWidget(QLabel("<b>Main</b>"), 0, 1)
        dataLayout.addWidget(QLabel("Output"), 0, 2)
        dataLayout.addWidget(QLabel("Mismatch"), 0, 3)
        dataLayout.addWidget(QLabel("<b>Aux</b>"), 0, 4)
        dataLayout.addWidget(QLabel("Output"), 0, 5)
        dataLayout.addWidget(QLabel("Mismatch"), 0, 6)
        dataLayout.addWidget(QLabel("<b>Current (A)</b>"), 0, 7)

        dataLayout.addItem(QSpacerItem(1, 1), 0, 8, -1, 1)

        dataLayout.setColumnStretch(0, 1)
        dataLayout.setColumnStretch(7, 1)
        dataLayout.setColumnStretch(8, 2)

        def createLabels(title, row, onOff=True):
            dataLayout.addWidget(QLabel(f"<b>{title}</b>"), row, 0)

            if onOff:
                self.mainCommandedLabels.append(PowerOnOffLabel())
                self.mainOutputLabels.append(PowerOnOffLabel())
                self.mainMismatchLabels.append(WarningLabel())
                dataLayout.addWidget(self.mainCommandedLabels[-1], row, 1)
                dataLayout.addWidget(self.mainOutputLabels[-1], row, 2)
                dataLayout.addWidget(self.mainMismatchLabels[-1], row, 3)

                self.auxCommandedLabels.append(PowerOnOffLabel())
                self.auxOutputLabels.append(PowerOnOffLabel())
                self.auxMismatchLabels.append(WarningLabel())
                dataLayout.addWidget(self.auxCommandedLabels[-1], row, 4)
                dataLayout.addWidget(self.auxOutputLabels[-1], row, 5)
                dataLayout.addWidget(self.auxMismatchLabels[-1], row, 6)

            self.currentLabels.append(QLabel("---"))
            dataLayout.addWidget(self.currentLabels[-1], row, 7)

        for row in range(4):
            createLabels(f"Power Network {bus(row)}", row + 1)

        createLabels("Light Network", 5, False)
        createLabels("Controls Network", 6, False)

        self.chart = TimeChart(
            {"Current (A)": ["A", "B", "C", "D", "Lights", "Controls"]}
        )
        self.chartView = TimeChartView(self.chart)

        statusGrid = StatusGrid(
            {
                "rcpMirrorCellUtility220VAC1Status" : "Mirror 220VAC1",
                "rcpMirrorCellUtility220VAC2Status" : "Mirror 220VAC2",
                "rcpMirrorCellUtility220VAC3Status" : "Mirror 222VAC3",
                "rcpCabinetUtility220VACStatus" : "Cabinet 220VAC",
                "rcpExternalEquipment220VACStatus" : "External 220VAC",

                "controlsPowerNetworkRedundantStatus" : "Power Redundant",
                "controlsPowerNetworkRedundancyControlStatus" : "Redundancy Control",

                "lightPowerNetworkStatus" : "Light",
                "externalEquipmentPowerNetworkStatus" : "External",
                "laserTrackerPowerNetworkStatus" : "Laser",
                "controlsPowerNetworkStatus" : "Power",
            },
            self.m1m3.powerSupplyStatus,
            4,
        )

        powerGrid = StatusGrid(
            {
                "powerNetworkAStatus" : "A Power",
                "powerNetworkARedundantStatus" : "A Redundant",
                "powerNetworkARedundancyControlStatus" : "A Redundancy Control",

                "powerNetworkBStatus" : "B Power",
                "powerNetworkBRedundantStatus" : "B Redundant",
                "powerNetworkBRedundancyControlStatus" : "B Redundancy Control",

                "powerNetworkCStatus" : "C Power",
                "powerNetworkCRedundantStatus" : "C Redundant",
                "powerNetworkCRedundancyControlStatus" : "C Redundancy Control",

                "powerNetworkDStatus" : "D Power",
                "powerNetworkDRedundantStatus" : "D Redundant",
                "powerNetworkDRedundancyControlStatus" : "D Redundancy Control",
            },
            self.m1m3.powerSupplyStatus,
            4,
        )

        plotLayout.addWidget(self.chartView)

        layout.addLayout(commandLayout)
        layout.addLayout(dataLayout)
        layout.addWidget(statusGrid)
        layout.addWidget(powerGrid)
        layout.addLayout(plotLayout)

        self.setLayout(layout)

        self.m1m3.powerStatus.connect(self.powerStatus)
        self.m1m3.powerWarning.connect(self.powerWarning)
        self.m1m3.powerSupplyData.connect(self.powerSupplyData)

    @Slot(map)
    def powerStatus(self, data):
        for b in range(4):
            busName = bus(b)
            mainCmd = getattr(data, f"powerNetwork{busName}CommandedOn")
            mainOut = getattr(data, f"powerNetwork{busName}OutputOn")
            self.mainOnButtons[b].setDisabled(mainCmd)
            self.mainOffButtons[b].setEnabled(mainCmd)
            self.mainCommandedLabels[b].setValue(mainCmd)
            self.mainOutputLabels[b].setValue(mainOut)

            auxCmd = getattr(data, f"auxPowerNetwork{busName}CommandedOn")
            auxOut = getattr(data, f"auxPowerNetwork{busName}OutputOn")
            self.auxOnButtons[b].setDisabled(mainCmd)
            self.auxOffButtons[b].setEnabled(mainCmd)
            self.auxCommandedLabels[b].setValue(auxCmd)
            self.auxOutputLabels[b].setValue(auxOut)

    @Slot(map)
    def powerWarning(self, data):
        for b in range(4):
            busName = bus(b)
            mainMis = getattr(data, f"powerNetwork{busName}OutputMismatch")
            self.mainMismatchLabels[b].setValue(mainMis)

            auxMis = getattr(data, f"auxPowerNetwork{busName}OutputMismatch")
            self.auxMismatchLabels[b].setValue(auxMis)

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
