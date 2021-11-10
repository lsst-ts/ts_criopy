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
    QSpinBox,
)
from PySide2.QtCore import Slot
from ..GUI import TopicWindow, SALCommand
from .ThermalData import Thermals

from asyncqt import asyncSlot

BUTTON_FANS = 1
BUTTON_HEATERS = 2


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
    class SetButton(QPushButton):
        def __init__(self, parent, kind):
            self._kind = kind
            if self._kind == BUTTON_HEATERS:
                self._edit_title = "Edit FCU Heaters PWM"
                self._set_title = "Set FCU Heaters PWM"
            elif self._kind == BUTTON_FANS:
                self._edit_title = "Edit FCU Fans speed"
                self._set_title = "Set FCU Fans speed"
            else:
                raise RuntimeError(f"Unknown set button kind {kind}")

            super().__init__(self._edit_title)

            self._parent = parent
            self.setDisabled(True)

            self._parent.m1m3ts.engineeringMode.connect(self.engineeringMode)
            self.clicked.connect(self.edit)

        @Slot(map)
        def engineeringMode(self, data):
            self.setEnabled(data.engineeringMode)
            if not (data.engineeringMode):
                self.setText(self._edit_title)

        @asyncSlot()
        async def edit(self):
            if self.text() == self._edit_title:
                self._parent.startEdit(self._kind)
                self.setText(self._set_title)
            else:
                await self._parent.heaterFanDemand(self._kind)
                self.setText(self._edit_title)

    def __init__(self, m1m3ts):
        super().__init__()
        self.m1m3ts = m1m3ts
        self.freezed = False

        self.dataWidget = DataWidget()

        self.fans = [0] * 96
        self.heaters = [0] * 96

        setHeatersButton = self.SetButton(self, BUTTON_HEATERS)
        setFansbutton = self.SetButton(self, BUTTON_FANS)

        self.flatDemand = QSpinBox()
        self.flatDemand.setRange(0, 255)

        setConstant = QPushButton("Set constant")
        setConstant.clicked.connect(self.setConstant)

        commandLayout = QGridLayout()
        commandLayout.addWidget(self.flatDemand, 0, 0)
        commandLayout.addWidget(setConstant, 0, 1)
        commandLayout.addWidget(setHeatersButton, 1, 0)
        commandLayout.addWidget(setFansbutton, 1, 1)

        hBox = QHBoxLayout()
        hBox.addLayout(commandLayout)
        hBox.addStretch()

        layout = QVBoxLayout()

        layout.addWidget(self.dataWidget)
        layout.addStretch()
        layout.addLayout(hBox)

        self.setLayout(layout)

    @Slot()
    def setConstant(self):
        for r in range(0, 10):
            for c in range(0, 10):
                index = r * 10 + c
                if index < 96:
                    self.dataWidget.item(r, c).setText(self.flatDemand.text())

    @SALCommand
    def _heaterFanDemand(self, **kwargs):
        return self.m1m3ts.remote.cmd_heaterFanDemand

    def startEdit(self, kind):
        if kind == BUTTON_HEATERS:
            self.updateValues(self.heaters, True)
        else:
            self.updateValues(self.fans, True)

    async def heaterFanDemand(self, kind):
        data = []
        for r in range(0, 10):
            for c in range(0, 10):
                index = r * 10 + c
                if index < 96:
                    data.append(int(self.dataWidget.item(r, c).text()))
        if kind == BUTTON_HEATERS:
            await self._heaterFanDemand(heaterPWM=data, fanRPM=self.fans)
            self.heaters = data
        else:
            await self._heaterFanDemand(heaterPWM=self.heaters, fanRPM=data)
            self.fans = data
        self.freezed = False

    def updateValues(self, values, freeze=False):
        if self.freezed:
            return

        self.freezed = freeze

        if values is None:
            self.dataWidget.empty()
            return

        for r in range(0, 10):
            for c in range(0, 10):
                index = r * 10 + c
                if index < 96:
                    self.dataWidget.item(r, c).setText(str(values[index]))


class ThermalValuePageWidget(TopicWindow):
    def __init__(self, m1m3ts):
        self.commandWidget = CommandWidget(m1m3ts)

        super().__init__("Thermal Values", m1m3ts, Thermals(), self.commandWidget)

    def updateValues(self, data):
        if data is None:
            self.commandWidget.updateValues(None)
        else:
            self.commandWidget.updateValues(self.field.getValue(data))
