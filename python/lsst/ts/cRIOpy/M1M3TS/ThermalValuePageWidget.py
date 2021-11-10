# This file is part of M1M3 GUI.
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

from PySide2.QtWidgets import (
    QWidget,
    QTableWidget,
    QPushButton,
    QTableWidgetItem,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
)
from PySide2.QtCore import Slot
from ..GUI import TopicWindow, SALCommand
from .ThermalData import Thermals

from asyncqt import asyncSlot

EDIT_FAN = "Edit FCU Fan speed"
SET_FAN = "Set FCU Fan speed"

EDIT_HEATER = "Edit FCU Heaters PWM"
SET_HEATER = "Set FCU Heaters PWM"


class SetButton(QPushButton):
    def __init__(self, m1m3ts, title):
        super().__init__(title)
        self._title = title
        self.m1m3ts = m1m3ts
        self.setDisabled(True)

        m1m3ts.engineeringMode.connect(self.engineeringMode)

    @Slot(map)
    def engineeringMode(self, data):
        self.setEnabled(data.engineeringMode)
        if not (data.engineeringMode):
            self.setText(self._title)


class DataWidget(QTableWidget):
    def __init__(self):
        super().__init__(10, 10)
        for r in range(0, 10):
            for c in range(0, 10):
                item = QTableWidgetItem("")
                self.setItem(r, c, item)
        self.empty()

    def empty(self):
        for r in range(0, 10):
            for c in range(0, 10):
                self.item(r, c).setText(str(r * 10 + c))


class CommandWidget(QWidget):
    def __init__(self, m1m3ts):
        super().__init__()
        self.m1m3ts = m1m3ts
        self.freezed = False

        self.dataWidget = DataWidget()

        self.fans = [0] * 97
        self.heaters = [0] * 97

        self.setHeatersButton = SetButton(m1m3ts, EDIT_HEATER)
        self.setHeatersButton.clicked.connect(self.setHeaters)

        self.setFansbutton = SetButton(m1m3ts, EDIT_FAN)
        self.setFansbutton.clicked.connect(self.setFans)

        commandLayout = QGridLayout()
        commandLayout.addWidget(self.setHeatersButton, 0, 0)
        commandLayout.addWidget(self.setFansbutton, 0, 1)

        hBox = QHBoxLayout()
        hBox.addLayout(commandLayout)
        hBox.addStretch()

        layout = QVBoxLayout()

        layout.addWidget(self.dataWidget)
        layout.addStretch()
        layout.addLayout(hBox)

        self.setLayout(layout)

    @SALCommand
    def _heaterFanDemand(self, **kwargs):
        return self.m1m3ts.remote.cmd_heaterFanDemand

    @asyncSlot()
    async def setFans(self):
        if self.setFansbutton.text() == EDIT_FAN:
            self.updateValues(self.fans, True)
            self.setFansbutton.setText(SET_FAN)
        else:
            data = []
            for r in range(0, 10):
                for c in range(0, 10):
                    index = r * 10 + c
                    if index < 96:
                        data.append(int(self.dataWidget.item(r, c).text()))
            await self._heaterFanDemand(heaterPWM=self.heaters, fanRPM=data)
            self.fans = data
            self.freezed = False
            self.setFansbutton.setText(EDIT_FAN)

    @asyncSlot()
    async def setHeaters(self):
        if self.setHeatersButton.text() == EDIT_HEATER:
            self.updateValues(self.heaters, True)
            self.setHeatersButton.setText(SET_HEATER)
        else:
            data = []
            for r in range(0, 10):
                for c in range(0, 10):
                    index = r * 10 + c
                    if index < 96:
                        data.append(int(self.dataWidget.item(r, c).text()))
            await self._heaterFanDemand(heaterPWM=data, fanRPM=self.fans)
            self.heaters = data
            self.freezed = False
            self.setHeatersButton.setText(EDIT_HEATER)

    def updateValues(self, values, freeze=False):
        if self.freezed:
            return

        if values is None:
            self.dataWidget.empty()
            return

        for r in range(0, 10):
            for c in range(0, 10):
                index = r * 10 + c
                if index < 96:
                    self.dataWidget.item(r, c).setText(str(values[index]))

        self.freezed = freeze


class ThermalValuePageWidget(TopicWindow):
    def __init__(self, m1m3ts):
        self.commandWidget = CommandWidget(m1m3ts)

        super().__init__("Thermal Values", m1m3ts, Thermals(), self.commandWidget)

    def updateValues(self, data):
        if data is None:
            self.commandWidget.updateValues(None)
        else:
            self.commandWidget.updateValues(self.field.getValue(data))
