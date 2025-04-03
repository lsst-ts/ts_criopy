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

from lsst.ts.salobj import BaseMsgType
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
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
from qasync import asyncSlot

from ..gui.sal import TopicWindow
from ..salcomm import MetaSAL, command
from .thermal_data import Thermals


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

    def setValues(self, data: BaseMsgType) -> None:
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
        def engineeringMode(self, data: BaseMsgType) -> None:
            self.setEnabled(data.engineeringMode)
            if not (data.engineeringMode):
                self.setText(self._edit_title)

        @asyncSlot()
        async def edit(self) -> None:
            if self.text() == self._edit_title:
                self._parent.startEdit(self._kind)
                self.setText(self._set_title)
            else:
                await self._parent.heater_fan_demand(self._kind)
                self.setText(self._edit_title)

        def cancel(self) -> None:
            self.setText(self._edit_title)
            self.setEnabled(True)

    def __init__(self, m1m3ts: MetaSAL):
        super().__init__()
        self.m1m3ts = m1m3ts
        self.freezed = False

        self.data_widget = DataWidget()

        self.fans = [0] * 96
        self.heaters = [0] * 96

        self.set_heaters_button = self.SetButton(self, Buttons.HEATERS)
        self.setFansButton = self.SetButton(self, Buttons.FANS)

        self.flat_demand = QSpinBox()
        self.flat_demand.setRange(0, 255)

        self.setConstantButton = QPushButton("Set constant")
        self.setConstantButton.setToolTip("Sets all target values to given constant")
        self.setConstantButton.setDisabled(True)
        self.setConstantButton.clicked.connect(self.set_constant)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setToolTip("Cancel value editing")
        self.cancel_button.setDisabled(True)
        self.cancel_button.clicked.connect(self.cancel)

        command_layout = QGridLayout()
        command_layout.addWidget(self.flat_demand, 0, 0)
        command_layout.addWidget(self.setConstantButton, 0, 1)
        command_layout.addWidget(self.cancel_button, 0, 2, 2, 1)
        command_layout.addWidget(self.set_heaters_button, 1, 0)
        command_layout.addWidget(self.setFansButton, 1, 1)

        hBox = QHBoxLayout()
        hBox.addLayout(command_layout)
        hBox.addStretch()

        layout = QVBoxLayout()

        layout.addWidget(self.data_widget)
        layout.addLayout(hBox)

        self.setLayout(layout)

    @Slot()
    def set_constant(self) -> None:
        self.data_widget.setValues([self.flat_demand.text()] * 96)

    @Slot()
    def cancel(self) -> None:
        self.freezed = False
        self.data_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setConstantButton.setDisabled(True)
        self.setFansButton.setEnabled(True)
        self.setFansButton.cancel()
        self.set_heaters_button.setEnabled(True)
        self.set_heaters_button.cancel()
        self.cancel_button.setDisabled(True)

    async def _heater_fan_demand(self, **kwargs: typing.Any) -> None:
        await command(self, self.m1m3ts.remote.cmd_heater_fan_demand, **kwargs)

    def startEdit(self, kind: Buttons) -> None:
        if kind == Buttons.HEATERS:
            self.update_values(self.heaters, True)
            self.setFansButton.setDisabled(True)
        else:
            self.update_values(self.fans, True)
            self.set_heaters_button.setDisabled(True)

        self.data_widget.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.data_widget.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.setConstantButton.setEnabled(True)

    async def heater_fan_demand(self, kind: Buttons) -> None:
        data = self.data_widget.getValues()
        if kind == Buttons.HEATERS:
            await self._heater_fan_demand(heaterPWM=data, fanRPM=self.fans)
            self.heaters = data
        else:
            await self._heater_fan_demand(heaterPWM=self.heaters, fanRPM=data)
            self.fans = data

        self.cancel()

    def update_values(self, values: typing.Any, freeze: bool = False) -> None:
        if self.freezed:
            return

        self.freezed = freeze

        if values is None:
            self.data_widget.empty()
            return

        self.data_widget.setValues(values)


class ThermalValuePageWidget(TopicWindow):
    """Widget displaying ILC values.

    Parameters
    ----------
    m1m3ts : `MetaSAL`
        SAL TS object
    """

    def __init__(self, m1m3ts: MetaSAL):
        self.command_widget = CommandWidget(m1m3ts)

        super().__init__("Thermal Values", m1m3ts, Thermals(), self.command_widget)

    def update_values(self, data: BaseMsgType) -> None:
        if data is None or self.field is None:
            self.command_widget.update_values(None)
        else:
            self.command_widget.update_values(self.field.getValue(data))
