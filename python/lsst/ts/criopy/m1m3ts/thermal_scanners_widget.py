# This file is part of the cRIO GUI.
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

import math

from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.tables.m1m3 import Scanner, ThermocoupleTable, find_thermocouple
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGridLayout, QTableWidget, QTableWidgetItem, QWidget

from ..salcomm import MetaSAL

__all__ = ["ThermalScannersWidget"]


class ThermalScannersWidget(QWidget):
    def __init__(self, ts_1: MetaSAL, ts_2: MetaSAL, ts_3: MetaSAL, ts_4: MetaSAL):
        super().__init__()
        ts_1.temperature.connect(self.temperature)
        ts_2.temperature.connect(self.temperature)
        ts_3.temperature.connect(self.temperature)
        ts_4.temperature.connect(self.temperature)

        self.top_middle_bottom = QTableWidget(3, 4)

        self.top_middle_bottom.setHorizontalHeaderLabels(
            ["Min", "Average", "Mean", "Max"]
        )
        self.top_middle_bottom.setVerticalHeaderLabels(["Front", "Middle", "Bottom"])
        for r in range(self.top_middle_bottom.rowCount()):
            for c in range(self.top_middle_bottom.columnCount()):
                self.top_middle_bottom.setItem(r, c, QTableWidgetItem("--"))

        self.sensor_data = QTableWidget(45, 4)
        self.sensor_data.setHorizontalHeaderLabels(["#1", "#2", "#3", "#4"])

        layout = QGridLayout()
        layout.addWidget(self.top_middle_bottom, 0, 0)
        layout.addWidget(self.sensor_data)

        self.setLayout(layout)

        self.data = ThermocoupleTable
        # data are modified to hold actual received data
        for tc in self.data:
            tc.value = None
            tc.timestamp = None

        self.coldplates = [math.nan] * 4

    @Slot()
    def temperature(self, data: BaseMsgType) -> None:
        device = data.salIndex
        num = int(data.sensorName[-3]) - 1

        if num == 0:
            self.coldplates[device - Scanner.TS_01] = data.temperatureItem[0]

        for i in range((1 if num == 0 else 0), 16):
            # 0/0 data is ref coldplate, which we ignore..
            channel = num * 16 + i
            tc = find_thermocouple(device, channel)
            if tc is None:
                continue
            tc.value = data.temperatureItem[i]
            tc.timestamp = data.private_sndStamp

        self._refresh()

    def _refresh(self) -> None:

        fmb: list[list[float]] = [[], [], []]

        for tc in self.data:
            if tc.value is None:
                continue

            if tc.is_front():
                fmb[0].append(tc.value)
            elif tc.is_middle():
                fmb[1].append(tc.value)
            else:
                fmb[2].append(tc.value)

        for row, data in enumerate(fmb):
            print(row, data)
            self.top_middle_bottom.item(row, 0).setText(f"{min(data):.02f} \u00b0C")
            self.top_middle_bottom.item(row, 3).setText(f"{max(data):.02f} \u00b0C")
