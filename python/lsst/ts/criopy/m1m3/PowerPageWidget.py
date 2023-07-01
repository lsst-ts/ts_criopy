# This file is part of M1M3 GUI
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org). See the COPYRIGHT file at the top - level directory
# of this distribution for details of code ownership.
#
# This program is free software : you can redistribute it and / or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.If not, see <https://www.gnu.org/licenses/>.

import typing

from asyncqt import asyncSlot
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QGridLayout, QLabel, QSpacerItem, QVBoxLayout, QWidget

from ..gui import PowerOnOffLabel, StatusGrid, TimeChart, TimeChartView, WarningLabel
from ..gui.SAL import EngineeringButton
from ..salcomm import MetaSAL, command


def bus(b: int) -> str:
    """Returns bus name from its number."""
    return chr(ord("A") + b)


class TurnButton(EngineeringButton):
    """Button to turn bis on/off.

    Parameters
    ----------
    m1m3 : `SALComm`
        M1M3 Sal object.
    kind : `str`
        Either Main or Aux - type of power bus to command.
    bus : `int`
        Bus number (0 to 3).
    onOff : `str`
        On or Off, command is turn On or Off.
    """

    def __init__(self, m1m3: MetaSAL, kind: str, bus: str, onOff: str):
        super().__init__(f"Turn {kind} {bus} {onOff}", m1m3)
        self.m1m3 = m1m3
        self.onOff = onOff

        if kind == "Main":
            self.__commandName = f"turnPowerNetwork{bus}{onOff}"
        else:
            self.__commandName = f"turn{kind}PowerNetwork{bus}{onOff}"

        self.clicked.connect(self.runCommand)

    @asyncSlot()
    async def runCommand(self) -> None:
        await command(
            self,
            getattr(self.m1m3.remote, f"cmd_turnPower{self.onOff}"),
            **{self.__commandName: True},
        )


class PowerPageWidget(QWidget):
    """Displays power related values, allows power commanding.

    Parameters
    ----------
    m1m3 : `SALComm`
        M1M3 SAL object.
    """

    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        self.m1m3 = m1m3

        layout = QVBoxLayout()
        dataLayout = QGridLayout()
        commandLayout = QGridLayout()
        plotLayout = QVBoxLayout()

        def createButtons(kind: str, onOff: str, col: int) -> list[TurnButton]:
            ret = []
            for b in range(4):
                ret.append(TurnButton(m1m3, kind, bus(b), onOff))
                commandLayout.addWidget(ret[-1], b, col)
            return ret

        self.mainOnButtons = createButtons("Main", "On", 0)
        self.mainOffButtons = createButtons("Main", "Off", 1)

        self.auxOnButtons = createButtons("Aux", "On", 2)
        self.auxOffButtons = createButtons("Aux", "Off", 3)

        self.mainCommandedLabels: list[PowerOnOffLabel] = []
        self.mainOutputLabels: list[PowerOnOffLabel] = []
        self.mainMismatchLabels: list[WarningLabel] = []

        self.auxCommandedLabels: list[PowerOnOffLabel] = []
        self.auxOutputLabels: list[PowerOnOffLabel] = []
        self.auxMismatchLabels: list[WarningLabel] = []

        self.currentLabels: list[QLabel] = []

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

        def create_labels(title: str, row: int, onOff: bool = True) -> None:
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
            create_labels(f"Power Network {bus(row)}", row + 1)

        create_labels("Light Network", 5, False)
        create_labels("Controls Network", 6, False)

        self.chart = TimeChart(
            {"Current (A)": ["A", "B", "C", "D", "Lights", "Controls"]}
        )
        self.chartView = TimeChartView(self.chart)

        statusGrid = StatusGrid(
            {
                "rcpMirrorCellUtility220VAC1Status": "Mirror 220VAC1",
                "rcpMirrorCellUtility220VAC2Status": "Mirror 220VAC2",
                "rcpMirrorCellUtility220VAC3Status": "Mirror 222VAC3",
                "rcpCabinetUtility220VACStatus": "Cabinet 220VAC",
                "rcpExternalEquipment220VACStatus": "External 220VAC",
                "controlsPowerNetworkRedundantStatus": "Power Redundant",
                "controlsPowerNetworkRedundancyControlStatus": ("Redundancy Control"),
                "lightPowerNetworkStatus": "Light",
                "externalEquipmentPowerNetworkStatus": "External",
                "laserTrackerPowerNetworkStatus": "Laser",
                "controlsPowerNetworkStatus": "Power",
            },
            self.m1m3.powerSupplyStatus,
            4,
        )

        powerGrid = StatusGrid(
            {
                "powerNetworkAStatus": "A Power",
                "powerNetworkARedundantStatus": "A Redundant",
                "powerNetworkARedundancyControlStatus": "A Redundancy Control",
                "powerNetworkBStatus": "B Power",
                "powerNetworkBRedundantStatus": "B Redundant",
                "powerNetworkBRedundancyControlStatus": "B Redundancy Control",
                "powerNetworkCStatus": "C Power",
                "powerNetworkCRedundantStatus": "C Redundant",
                "powerNetworkCRedundancyControlStatus": "C Redundancy Control",
                "powerNetworkDStatus": "D Power",
                "powerNetworkDRedundantStatus": "D Redundant",
                "powerNetworkDRedundancyControlStatus": "D Redundancy Control",
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

    @Slot()
    def powerStatus(self, data: typing.Any) -> None:
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
            self.auxOnButtons[b].setDisabled(auxCmd)
            self.auxOffButtons[b].setEnabled(auxCmd)
            self.auxCommandedLabels[b].setValue(auxCmd)
            self.auxOutputLabels[b].setValue(auxOut)

    @Slot()
    def powerWarning(self, data: typing.Any) -> None:
        for b in range(4):
            busName = bus(b)
            mainMis = getattr(data, f"powerNetwork{busName}OutputMismatch")
            self.mainMismatchLabels[b].setValue(mainMis)

            auxMis = getattr(data, f"auxPowerNetwork{busName}OutputMismatch")
            self.auxMismatchLabels[b].setValue(auxMis)

    @Slot()
    def powerSupplyData(self, data: typing.Any) -> None:
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
