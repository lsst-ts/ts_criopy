# This file is part of M1M3 SS GUI.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top - level directory of this distribution
# for details of code ownership.
#
# This program is free software : you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.


from lsst.ts.salobj import BaseMsgType
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QVBoxLayout, QWidget

from ..gui import InterlockOffGrid, PowerOnOffGrid, TimeChart, TimeChartView
from ..salcomm import MetaSAL


class InterlockPageWidget(QWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(
            PowerOnOffGrid(
                {
                    "heartbeatCommandedState": ("Controller to Interlock Heartbeat"),
                    "heartbeatOutputState": "Interlock heartbeat state",
                },
                m1m3.interlockStatus,
                1,
            )
        )
        layout.addSpacing(20)
        layout.addWidget(
            InterlockOffGrid(
                {
                    "auxPowerNetworksOff": "AUX Power Networks",
                    "thermalEquipmentOff": "Thermal Equipment",
                    "airSupplyOff": "Air Supply",
                    "tmaMotionStop": "TMA Motion Stop",
                    "gisHeartbeatLost": "GIS Heartbeat Lost",
                    "cabinetDoorOpen": "Cabinet Door Open",
                },
                m1m3.interlockWarning,
                2,
            )
        )

        self.chart = TimeChart({"Heartbeats": ["Commanded State", "Interlock State"]})
        layout.addWidget(TimeChartView(self.chart))

        self.setLayout(layout)

        m1m3.interlockStatus.connect(self.interlockStatus)

    @Slot()
    def interlockStatus(self, data: BaseMsgType) -> None:
        self.chart.append(
            data.timestamp,
            [
                data.heartbeatCommandedState,
                data.heartbeatOutputState,
            ],
        )
