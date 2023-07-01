# This file is part of M1M3 TS GUI.
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

import enum
import typing

from asyncqt import asyncSlot
from PySide2.QtCore import Slot
from PySide2.QtWidgets import (
    QAbstractItemView,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..gui.SAL import TopicWindow
from ..salcomm import MetaSAL, command
from .ThermalData import Thermals


class Buttons(enum.IntEnum):
    FANS = 1
    HEATERS = 2


class DataWidget(QTableWidget):
    """Table with ILC values. Stores ILC values."""

    def __init__(self) -> None:
        super().__init__(10, 10)
        for r in range(0, 10):
            self.setVerticalHeaderItem(r, QTableWidgetItem(str(r * 10)))
            for c in range(0, 10):
                item = QTableWidgetItem("")
                self.setItem(r, c, item)
        self.empty()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def empty(self) -> None:
        self.setValues(range(1, 97))

    def setValues(self, data: typing.Any) -> None:
        r = 0
        c = 0
        for value in data:
            self.item(r, c).setText(str(value))
            c += 1
            if c >= self.columnCount():
                c = 0
                r += 1

    def getValues(self) -> list[int]:
        data: list[int] = []
        for r in range(0, 10):
            for c in range(0, 10):
                index = r * 10 + c
                if index < 96:
                    data.append(int(self.item(r, c).text()))
        return data


class CommandWidget(QWidget):
    """Widget with buttons to edit table.

    Parameters
    ----------
    m1m3ts : `MetaSAL`
        SAL communication object.
    """

    class SetButton(QPushButton):
        """Button for editing/setting values.

        Parameters
        ----------
        parent : `CommandWidget`
            Command widget holding the button.
        kind : `Buttons`
            Button type.
        """

        def __init__(self, parent: "CommandWidget", kind: Buttons):
            self._kind = kind
            if self._kind == Buttons.HEATERS:
                self._edit_title = "Edit FCU Heaters PWM"
                self._set_title = "Set FCU Heaters PWM"
                tooltip = "Edit and sets Fan Coil Units (FCU) Heaters Power"
                " Wave Modulationi (PWM) (0-255 equals 0-100%)"
            elif self._kind == Buttons.FANS:
                self._edit_title = "Edit FCU Fans speed"
                self._set_title = "Set FCU Fans speed"
                tooltip = (
                    "Edit and sets Fan Coil Units (FCU) Fans Speed (0-255, *10" " RPM)"
                )
            else:
                raise RuntimeError(f"Unknown set button kind {kind}")

            super().__init__(self._edit_title)
            self.setToolTip(tooltip)

            self._parent = parent
            self.setDisabled(True)

            self._parent.m1m3ts.engineeringMode.connect(self.engineeringMode)
            self.clicked.connect(self.edit)

        @Slot()
        def engineeringMode(self, data: typing.Any) -> None:
            self.setEnabled(data.engineeringMode)
            if not (data.engineeringMode):
                self.setText(self._edit_title)

        @asyncSlot()
        async def edit(self) -> None:
            if self.text() == self._edit_title:
                self._parent.startEdit(self._kind)
                self.setText(self._set_title)
            else:
                await self._parent.heaterFanDemand(self._kind)
                self.setText(self._edit_title)

        def cancel(self) -> None:
            self.setText(self._edit_title)
            self.setEnabled(True)

    def __init__(self, m1m3ts: MetaSAL):
        super().__init__()
        self.m1m3ts = m1m3ts
        self.freezed = False

        self.dataWidget = DataWidget()

        self.fans = [0] * 96
        self.heaters = [0] * 96

        self.setHeatersButton = self.SetButton(self, Buttons.HEATERS)
        self.setFansButton = self.SetButton(self, Buttons.FANS)

        self.flatDemand = QSpinBox()
        self.flatDemand.setRange(0, 255)

        self.setConstantButton = QPushButton("Set constant")
        self.setConstantButton.setToolTip("Sets all target values to given constant")
        self.setConstantButton.setDisabled(True)
        self.setConstantButton.clicked.connect(self.setConstant)

        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.setToolTip("Cancel value editing")
        self.cancelButton.setDisabled(True)
        self.cancelButton.clicked.connect(self.cancel)

        commandLayout = QGridLayout()
        commandLayout.addWidget(self.flatDemand, 0, 0)
        commandLayout.addWidget(self.setConstantButton, 0, 1)
        commandLayout.addWidget(self.cancelButton, 0, 2, 2, 1)
        commandLayout.addWidget(self.setHeatersButton, 1, 0)
        commandLayout.addWidget(self.setFansButton, 1, 1)

        hBox = QHBoxLayout()
        hBox.addLayout(commandLayout)
        hBox.addStretch()

        layout = QVBoxLayout()

        layout.addWidget(self.dataWidget)
        layout.addLayout(hBox)

        self.setLayout(layout)

    @Slot()
    def setConstant(self) -> None:
        self.dataWidget.setValues([self.flatDemand.text()] * 96)

    @Slot()
    def cancel(self) -> None:
        self.freezed = False
        self.dataWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setConstantButton.setDisabled(True)
        self.setFansButton.setEnabled(True)
        self.setFansButton.cancel()
        self.setHeatersButton.setEnabled(True)
        self.setHeatersButton.cancel()
        self.cancelButton.setDisabled(True)

    async def _heaterFanDemand(self, **kwargs: typing.Any) -> None:
        await command(self, self.m1m3ts.remote.cmd_heaterFanDemand, **kwargs)

    def startEdit(self, kind: Buttons) -> None:
        if kind == Buttons.HEATERS:
            self.updateValues(self.heaters, True)
            self.setFansButton.setDisabled(True)
        else:
            self.updateValues(self.fans, True)
            self.setHeatersButton.setDisabled(True)

        self.dataWidget.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.dataWidget.setEnabled(True)
        self.cancelButton.setEnabled(True)
        self.setConstantButton.setEnabled(True)

    async def heaterFanDemand(self, kind: Buttons) -> None:
        data = self.dataWidget.getValues()
        if kind == Buttons.HEATERS:
            await self._heaterFanDemand(heaterPWM=data, fanRPM=self.fans)
            self.heaters = data
        else:
            await self._heaterFanDemand(heaterPWM=self.heaters, fanRPM=data)
            self.fans = data

        self.cancel()

    def updateValues(self, values: typing.Any, freeze: bool = False) -> None:
        if self.freezed:
            return

        self.freezed = freeze

        if values is None:
            self.dataWidget.empty()
            return

        self.dataWidget.setValues(values)


class ThermalValuePageWidget(TopicWindow):
    """Widget displaying ILC values.

    Parameters
    ----------
    m1m3ts : `MetaSAL`
        SAL TS object
    """

    def __init__(self, m1m3ts: MetaSAL):
        self.commandWidget = CommandWidget(m1m3ts)

        super().__init__("Thermal Values", m1m3ts, Thermals(), self.commandWidget)

    def updateValues(self, data: typing.Any) -> None:
        if data is None or self.field is None:
            self.commandWidget.updateValues(None)
        else:
            self.commandWidget.updateValues(self.field.getValue(data))
