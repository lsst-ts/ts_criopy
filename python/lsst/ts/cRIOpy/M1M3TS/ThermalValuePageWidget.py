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

EDIT_FCU = "Edit FCU Fan speed"
SET_FCU = "Set FCU Fan speed"


class FanButton(QPushButton):
    def __init__(self, m1m3ts):
        super().__init__(EDIT_FCU)
        self.m1m3ts = m1m3ts
        self.setDisabled(True)

        m1m3ts.engineeringMode.connect(self.engineeringMode)

    @Slot(map)
    def engineeringMode(self, data):
        self.setEnabled(data.engineeringMode)
        if not (data.engineeringMode):
            self.setText(EDIT_FCU)


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

        self.setFansbutton = FanButton(m1m3ts)
        self.setFansbutton.clicked.connect(self.setFans)

        commandLayout = QGridLayout()
        commandLayout.addWidget(self.setFansbutton, 0, 0)

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
        if self.setFansbutton.text() == EDIT_FCU:
            self.updateValues(self.m1m3ts.remote.tel_thermalData.get().fanRPM, True)
            self.setFansbutton.setText(SET_FCU)
        else:
            data = []
            for r in range(0, 10):
                for c in range(0, 10):
                    index = r * 10 + c
                    if index < 96:
                        data.append(int(self.dataWidget.item(r, c).text()))
            await self._heaterFanDemand(heaterPWM=[0] * 97, fanRPM=data)
            self.freezed = False
            self.setFansbutton.setText(EDIT_FCU)

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
