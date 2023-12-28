# This file is part of cRIO/VMS GUI.
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


from lsst.ts.salobj import BaseMsgType
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QFormLayout, QVBoxLayout, QWidget
from qasync import asyncSlot

from ..gui import OnOffLabel, WarningLabel
from ..gui.sal import EngineeringButton
from ..salcomm import MetaSAL, command


class CellLightPageWidget(QWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        self.m1m3 = m1m3

        layout = QVBoxLayout()

        self.turnLightsOnButton = EngineeringButton("Turn Lights On", m1m3)
        self.turnLightsOnButton.clicked.connect(self.issueCommandTurnLightsOn)
        self.turnLightsOnButton.setFixedWidth(256)
        self.turnLightsOffButton = EngineeringButton("Turn Lights Off", m1m3)
        self.turnLightsOffButton.clicked.connect(self.issueCommandTurnLightsOff)
        self.turnLightsOffButton.setFixedWidth(256)

        self.cellLightsCommandedOnLabel = OnOffLabel()
        self.cellLightsOnLabel = OnOffLabel()

        layout.addWidget(self.turnLightsOnButton)
        layout.addWidget(self.turnLightsOffButton)

        layout.addSpacing(20)

        dataLayout = QFormLayout()
        dataLayout.addRow("Command", self.cellLightsCommandedOnLabel)
        dataLayout.addRow("Sensor", self.cellLightsOnLabel)

        layout.addLayout(dataLayout)
        layout.addSpacing(20)

        warningLayout = QFormLayout()

        warningLayout.addRow(
            "Any Warnings", WarningLabel(m1m3.cellLightWarning, "anyWarning")
        )
        warningLayout.addRow(
            "Output Mismatch",
            WarningLabel(m1m3.cellLightWarning, "cellLightsOutputMismatch"),
        )
        warningLayout.addRow(
            "Sensor Mismatch",
            WarningLabel(m1m3.cellLightWarning, "cellLightsSensorMismatch"),
        )

        layout.addLayout(warningLayout)
        layout.addStretch()

        self.setLayout(layout)

        self.m1m3.cellLightStatus.connect(self.cellLightStatus)

    @Slot()
    def cellLightStatus(self, data: BaseMsgType) -> None:
        self.cellLightsCommandedOnLabel.setValue(data.cellLightsCommandedOn)
        self.cellLightsOnLabel.setValue(data.cellLightsOn)

        self.turnLightsOnButton.setDisabled(data.cellLightsCommandedOn)
        self.turnLightsOffButton.setEnabled(data.cellLightsCommandedOn)

    @asyncSlot()
    async def issueCommandTurnLightsOn(self) -> None:
        await command(self, self.m1m3.remote.cmd_turnLightsOn)

    @asyncSlot()
    async def issueCommandTurnLightsOff(self) -> None:
        await command(self, self.m1m3.remote.cmd_turnLightsOff)
