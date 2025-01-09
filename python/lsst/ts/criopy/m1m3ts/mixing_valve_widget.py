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


from lsst.ts.salobj import BaseMsgType
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ..gui import DataFormWidget, Percent, TimeChart, TimeChartView, Volt
from ..salcomm import MetaSAL, command


class MixingValveWidget(QWidget):
    """Displays Mixing Valve data."""

    def __init__(self, m1m3ts: MetaSAL):
        super().__init__()
        self.m1m3ts = m1m3ts

        selection_group = QGroupBox("Mixing valve control")
        self.command_mixing_valve = QRadioButton("&Raw")
        self.command_temperature = QRadioButton("&Temperature")

        self.command_mixing_valve.setChecked(True)

        selection_layout = QVBoxLayout()
        selection_layout.addWidget(self.command_mixing_valve)
        selection_layout.addWidget(self.command_temperature)
        selection_group.setLayout(selection_layout)

        command_layout = QFormLayout()

        self.mixing_valve_target = QDoubleSpinBox()
        self.mixing_valve_target.setRange(0, 100)
        self.mixing_valve_target.setSingleStep(1)
        self.mixing_valve_target.setDecimals(2)
        self.mixing_valve_target.setSuffix("%")
        command_layout.addRow("Target", self.mixing_valve_target)

        self.temperature_target = QDoubleSpinBox()
        self.temperature_target.setRange(-40, 50)
        self.temperature_target.setSingleStep(1)
        self.temperature_target.setDecimals(2)
        self.temperature_target.setSuffix("°C")
        command_layout.addRow("Setpoint", self.temperature_target)

        set_mixing_valve = QPushButton("Set")
        set_mixing_valve.clicked.connect(self._set)
        command_layout.addRow(set_mixing_valve)

        vlayout = QVBoxLayout()
        vlayout.addWidget(
            DataFormWidget(
                m1m3ts.mixingValve,
                [
                    ("Raw Position", Volt(field="rawValvePosition")),
                    ("Position", Percent(field="valvePosition")),
                ],
            )
        )
        vlayout.addSpacing(20)
        vlayout.addWidget(selection_group)
        vlayout.addLayout(command_layout)
        vlayout.addStretch()

        hlayout = QHBoxLayout()
        hlayout.addLayout(vlayout)

        self.mixing_valve_chart = TimeChart(
            {
                "Raw (V)": ["Raw Position"],
                "Percent (%)": ["Position"],
            }
        )

        hlayout.addWidget(TimeChartView(self.mixing_valve_chart))

        self.setLayout(hlayout)

        self.m1m3ts.mixingValve.connect(self.mixing_valve)
        self.m1m3ts.appliedSetpoint.connect(self.applied_setpoint)

    @Slot()
    def mixing_valve(self, data: BaseMsgType) -> None:
        self.mixing_valve_chart.append(
            data.private_sndStamp,
            [data.rawValvePosition],
            axis_index=0,
        )

        self.mixing_valve_chart.append(
            data.private_sndStamp,
            [data.valvePosition],
            axis_index=1,
        )

    @Slot()
    def applied_setpoint(self, data: BaseMsgType) -> None:
        self.temperature_target.setValue(data.setpoint)

    @asyncSlot()
    async def _set(self) -> None:
        if self.command_mixing_valve.isChecked():
            await command(
                self,
                self.m1m3ts.remote.cmd_setMixingValve,
                mixingValveTarget=self.mixing_valve_target.value(),
            )
            await command(
                self,
                self.m1m3ts.remote.cmd_applySetpoint,
                setpoint=float("nan"),
            )
        else:
            await command(
                self,
                self.m1m3ts.remote.cmd_applySetpoint,
                setpoint=self.temperature_target.value(),
            )
