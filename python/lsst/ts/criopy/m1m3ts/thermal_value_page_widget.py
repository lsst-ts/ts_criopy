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
from math import isnan

from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.tables.m1m3 import FCUTable
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QBrush, QColor
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


class ByteSpin(QSpinBox):
    def __init__(self) -> None:
        super().__init__()
        self.setRange(0, 255)


class DataWidget(QTableWidget):
    """Table with ILC values. Stores ILC values."""

    def __init__(self) -> None:
        super().__init__(10, 10)
        for c in range(10):
            self.setVerticalHeaderItem(c, QTableWidgetItem(str(c * 10)))
        for index in range(96):
            item = QTableWidgetItem("---")
            self.setItem(int(index / 10), index % 10, item)
        self.empty()
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def empty(self) -> None:
        self.set_values(range(1, 97))
        self.reset_background()

    def reset_background(self) -> None:
        d_b = self.palette().base()
        for index in range(96):
            self.get_item(index).setBackground(d_b)

    def get_item(self, index: int) -> QTableWidgetItem:
        return self.item(int(index / 10), index % 10)

    def set_value(self, index: int, value: str) -> None:
        self.get_item(index).setText(str(value))

    def set_values(self, data: BaseMsgType, fmt: str | None = None) -> None:
        r = 0
        c = 0
        for value in data:
            item = self.item(r, c)
            if fmt is None:
                item.setText(str(value))
            else:
                item.setText(fmt.format(v=value))
            c += 1
            if c >= self.columnCount():
                c = 0
                r += 1

    def get_values(self) -> list[int]:
        data: list[int] = []
        for r in range(0, 10):
            for c in range(0, 10):
                index = r * 10 + c
                if index < 96:
                    data.append(int(self.item(r, c).text()))
        return data

    def mask_backround(self, mask: list[bool], brush: QBrush) -> None:
        for index, masked in enumerate(mask):
            if masked:
                self.get_item(index).setBackground(brush)


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
                self._parent.start_edit(self._kind)
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
        self.set_fans_button = self.SetButton(self, Buttons.FANS)

        self.flat_demand = ByteSpin()
        self.m1_demand = ByteSpin()
        self.m3_demand = ByteSpin()

        self.set_constant_button = QPushButton("Set constant")
        self.set_constant_button.setToolTip("Sets all target values to given constant")
        self.set_constant_button.setDisabled(True)
        self.set_constant_button.clicked.connect(self.set_constant)

        self.set_m1_button = QPushButton("Set M1")
        self.set_m1_button.setToolTip("Sets M1 FCUs values to given value")
        self.set_m1_button.setDisabled(True)
        self.set_m1_button.clicked.connect(self.set_m1)

        self.set_m3_button = QPushButton("Set M3")
        self.set_m3_button.setToolTip("Sets M3 FCUs values to given value")
        self.set_m3_button.setDisabled(True)
        self.set_m3_button.clicked.connect(self.set_m3)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setToolTip("Cancel value editing")
        self.cancel_button.setDisabled(True)
        self.cancel_button.clicked.connect(self.cancel)

        command_layout = QGridLayout()
        command_layout.addWidget(self.flat_demand, 0, 0)
        command_layout.addWidget(self.set_constant_button, 0, 1)
        command_layout.addWidget(self.cancel_button, 0, 2, 2, 1)
        command_layout.addWidget(self.set_heaters_button, 1, 0)
        command_layout.addWidget(self.set_fans_button, 1, 1)

        command_layout.addWidget(self.m1_demand, 0, 4)
        command_layout.addWidget(self.m3_demand, 1, 4)
        command_layout.addWidget(self.set_m1_button, 0, 5)
        command_layout.addWidget(self.set_m3_button, 1, 5)

        hBox = QHBoxLayout()
        hBox.addLayout(command_layout)
        hBox.addStretch()

        layout = QVBoxLayout()

        layout.addWidget(self.data_widget)
        layout.addLayout(hBox)

        self.setLayout(layout)

    @Slot()
    def set_constant(self) -> None:
        self.data_widget.set_values([self.flat_demand.text()] * 96)

    @Slot()
    def set_m1(self) -> None:
        value = self.m1_demand.text()
        for fcu in [fcu for fcu in FCUTable if fcu.is_m1()]:
            self.data_widget.set_value(fcu.index, value)

    @Slot()
    def set_m3(self) -> None:
        value = self.m3_demand.text()
        for fcu in [fcu for fcu in FCUTable if fcu.is_m3()]:
            self.data_widget.set_value(fcu.index, value)

    @Slot()
    def cancel(self) -> None:
        self.freezed = False
        self.data_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.set_constant_button.setDisabled(True)
        self.set_m1_button.setDisabled(True)
        self.set_m3_button.setDisabled(True)
        self.set_fans_button.setEnabled(True)
        self.set_fans_button.cancel()
        self.set_heaters_button.setEnabled(True)
        self.set_heaters_button.cancel()
        self.cancel_button.setDisabled(True)

    async def _heater_fan_demand(self, **kwargs: typing.Any) -> None:
        await command(self, self.m1m3ts.remote.cmd_heaterFanDemand, **kwargs)

    def start_edit(self, kind: Buttons) -> None:
        if kind == Buttons.HEATERS:
            self.update_values(self.heaters, True)
            self.set_fans_button.setDisabled(True)
        else:
            self.update_values(self.fans, True)
            self.set_heaters_button.setDisabled(True)

        self.data_widget.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.data_widget.setEnabled(True)
        self.cancel_button.setEnabled(True)
        self.set_constant_button.setEnabled(True)
        self.set_m1_button.setEnabled(True)
        self.set_m3_button.setEnabled(True)

    async def heater_fan_demand(self, kind: Buttons) -> None:
        data = self.data_widget.get_values()
        if kind == Buttons.HEATERS:
            await self._heater_fan_demand(heaterPWM=data, fanRPM=self.fans)
            self.heaters = data
        else:
            await self._heater_fan_demand(heaterPWM=self.heaters, fanRPM=data)
            self.fans = data

        self.cancel()

    def update_values(
        self, values: None | BaseMsgType, freeze: bool = False, fmt: str | None = None
    ) -> None:
        if self.freezed:
            return

        self.freezed = freeze

        if values is None:
            self.data_widget.empty()
            return

        self.data_widget.set_values(values, fmt=fmt)

    def mask_backround(self, mask: list[bool], background: QBrush) -> None:
        self.data_widget.mask_backround(mask, background)


class ThermalValuePageWidget(TopicWindow):
    """Widget displaying ILC values.

    Parameters
    ----------
    m1m3ts : `MetaSAL`
        SAL TS object
    """

    def __init__(self, m1m3ts: MetaSAL):
        self.command_widget = CommandWidget(m1m3ts)

        super().__init__(m1m3ts, Thermals(), self.command_widget)

    def update_values(self, data: BaseMsgType) -> None:
        if data is None or self.field is None:
            self.command_widget.update_values(None)
        else:
            values = self.field.getValue(data)
            self.command_widget.data_widget.reset_background()
            self.command_widget.update_values(values, fmt=self.field.fmt)
            if self.field.field_name in ["heaterPWM"]:
                self.command_widget.mask_backround(
                    [heater == 0 for heater in values], Qt.red
                )
                self.command_widget.mask_backround(
                    [heater == 100 for heater in values], Qt.blue
                )
            if self.field.field_name in "absoluteTemperature":
                self.command_widget.mask_backround(
                    [isnan(t) for t in values], Qt.darkRed
                )
                target = self.comm.remote.evt_appliedSetpoints.get()
                if target is not None and not isnan(target.heatersSetpoint):
                    tt = target.heatersSetpoint
                    t_diff = [t - tt for t in values]
                    self.command_widget.mask_backround(
                        [td < -0.025 for td in t_diff], QColor("#99CCFF")
                    )
                    self.command_widget.mask_backround(
                        [td > 0.025 for td in t_diff], QColor("#FF9999")
                    )
                    self.command_widget.mask_backround(
                        [td < -0.05 for td in t_diff], Qt.blue
                    )
                    self.command_widget.mask_backround(
                        [td > 0.05 for td in t_diff], Qt.red
                    )
            if self.field.field_name in ["heaterPWM", "fanRPM", "absoluteTemperature"]:
                t_w = self.comm.remote.evt_thermalWarning.get()
                if t_w is not None:
                    self.command_widget.mask_backround(
                        t_w.breakerHeater1Error, QBrush(Qt.red, Qt.Dense6Pattern)
                    )
            elif isinstance(values[0], bool):
                self.command_widget.mask_backround(
                    values, QBrush(Qt.red, Qt.Dense3Pattern)
                )
            thermal_settings = self.comm.remote.evt_thermalSettings.get()
            if thermal_settings is not None:
                self.command_widget.mask_backround(
                    [not (d) for d in thermal_settings.enabledFCU], QBrush(Qt.gray)
                )
