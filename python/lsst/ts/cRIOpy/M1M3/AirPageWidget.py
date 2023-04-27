# This file is part of M1M3 SS GUI.
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

from asyncqt import asyncSlot
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QVBoxLayout, QWidget

from ..GUI import OnOffGrid, SALAxis, SALChartWidget, WarningGrid
from ..GUI.SAL import EngineeringButton, SALCommand


class AirPageWidget(QWidget):
    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3

        layout = QVBoxLayout()

        self.turnAirOnButton = EngineeringButton("Turn Air On", m1m3)
        self.turnAirOnButton.clicked.connect(self.issueCommandTurnAirOn)
        self.turnAirOnButton.setFixedWidth(256)
        self.turnAirOffButton = EngineeringButton("Turn Air Off", m1m3)
        self.turnAirOffButton.clicked.connect(self.issueCommandTurnAirOff)
        self.turnAirOffButton.setFixedWidth(256)

        layout.addWidget(self.turnAirOnButton)
        layout.addWidget(self.turnAirOffButton)
        layout.addSpacing(20)

        layout.addWidget(
            OnOffGrid(
                {
                    "airCommandedOn": "Commanded On",
                    "airValveOpened": "Valve Opened",
                    "airValveClosed": "Valve Closed",
                },
                m1m3.airSupplyStatus,
                1,
            )
        )

        layout.addSpacing(20)

        layout.addWidget(
            WarningGrid(
                {
                    "anyWarning": "Any Warnings",
                    "commandOutputMismatch": "Output Mismatch",
                    "commandSensorMismatch": "Sensor Mismatch",
                },
                m1m3.airSupplyWarning,
                3,
            )
        )

        axis = SALAxis("Pressure", m1m3.hardpointMonitorData)

        for s in range(6):
            axis.addArrayValue(str(s), "breakawayPressure", s)

        layout.addWidget(SALChartWidget(axis))

        self.setLayout(layout)

        self.m1m3.airSupplyStatus.connect(self.airSupplyStatus)

    @Slot(map)
    def airSupplyStatus(self, data):
        self.turnAirOnButton.setDisabled(data.airCommandedOn)
        self.turnAirOffButton.setEnabled(data.airCommandedOn)

    @asyncSlot()
    async def issueCommandTurnAirOn(self):
        await SALCommand(self, self.m1m3.remote.cmd_turnAirOn)

    @asyncSlot()
    async def issueCommandTurnAirOff(self):
        await SALCommand(self, self.m1m3.remote.cmd_turnAirOff)
