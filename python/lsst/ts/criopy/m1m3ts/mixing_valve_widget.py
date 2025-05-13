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

import math

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

from ..gui import DataDegC, DataFormWidget, Percent, TimeChart, TimeChartView, Volt
from ..salcomm import MetaSAL, command


class MixingValveWidget(QWidget):
    """Displays Mixing Valve data, allows mixing valve control.

    Parameters
    ----------
    m1m3ts : `MetaSAL`
        M1M3 thermal system SAL client.
    """

    def __init__(self, m1m3ts: MetaSAL):
        super().__init__()
        self.m1m3ts = m1m3ts

        selection_group = QGroupBox("Mixing valve control")
        self.command_mixing_valve = QRadioButton("&Raw")
        self.command_temperature = QRadioButton("&Temperature")

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

        def temperature_target() -> QDoubleSpinBox:
            temperature_target_box = QDoubleSpinBox()
            temperature_target_box.setRange(-40, 50)
            temperature_target_box.setSingleStep(0.05)
            temperature_target_box.setDecimals(2)
            temperature_target_box.setSuffix("°C")
            return temperature_target_box

        self.glycol_target = temperature_target()
        self.heaters_target = temperature_target()

        command_layout.addRow("Glycol setpoint", self.glycol_target)
        command_layout.addRow("Heaters setpoint", self.heaters_target)

        set_mixing_valve = QPushButton("Set")
        set_mixing_valve.clicked.connect(self._set)
        command_layout.addRow(set_mixing_valve)

        self.delta_t = temperature_target()
        command_layout.addRow("\u0394 T", self.delta_t)
        self.set_delta_t = QPushButton("Do \u0394 T")
        self.set_delta_t.clicked.connect(self._delta)
        command_layout.addRow(self.set_delta_t)

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

        vlayout.addWidget(
            DataFormWidget(
                m1m3ts.appliedSetpoints,
                [
                    ("Glycol Setpoint", DataDegC(field="glycolSetpoint")),
                    ("Heaters Setpoint", DataDegC(field="heatersSetpoint")),
                ],
            )
        )
        vlayout.addWidget(
            DataFormWidget(
                m1m3ts.glycolLoopTemperature,
                [
                    ("Above Mirror", DataDegC(field="aboveMirrorTemperature")),
                    ("Inside 1", DataDegC(field="insideCellTemperature1")),
                    ("Inside 2", DataDegC(field="insideCellTemperature2")),
                    ("Inside 3", DataDegC(field="insideCellTemperature3")),
                    (
                        "Telescope Supply",
                        DataDegC(field="telescopeCoolantSupplyTemperature"),
                    ),
                    ("Cell Supply", DataDegC(field="mirrorCoolantSupplyTemperature")),
                    ("Cell Return", DataDegC(field="mirrorCoolantReturnTemperature")),
                    (
                        "Telescope Return",
                        DataDegC(field="telescopeCoolantReturnTemperature"),
                    ),
                ],
            )
        )

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

        self.command_mixing_valve.toggled.connect(self._temperature_control)
        self.command_mixing_valve.setChecked(True)

        self.m1m3ts.mixingValve.connect(self.mixing_valve)
        self.m1m3ts.appliedSetpoints.connect(self.applied_setpoints)

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
    def applied_setpoints(self, data: BaseMsgType) -> None:
        if math.isnan(data.glycolSetpoint):
            self.command_temperature.setChecked(False)
        else:
            self.command_temperature.setChecked(True)
            self.glycol_target.setValue(data.glycolSetpoint)
            self.heaters_target.setValue(data.heatersSetpoint)

    @Slot()
    def _temperature_control(self, checked: bool) -> None:
        self.mixing_valve_target.setEnabled(checked)
        self.glycol_target.setEnabled(not (checked))
        self.heaters_target.setEnabled(not (checked))
        self.delta_t.setEnabled(not (checked))
        self.set_delta_t.setEnabled(not (checked))

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
                self.m1m3ts.remote.cmd_applySetpoints,
                glycolSetpoint=float("nan"),
                heatersSetpoint=float("nan"),
            )
        else:
            await command(
                self,
                self.m1m3ts.remote.cmd_applySetpoints,
                glycolSetpoint=self.glycol_target.value(),
                heatersSetpoint=self.heaters_target.value(),
            )

    @asyncSlot()
    async def _delta(self) -> None:
        self.glycol_target.setValue(self.glycol_target.value() + self.delta_t.value())
        self.heaters_target.setValue(self.heaters_target.value() + self.delta_t.value())
        await command(
            self,
            self.m1m3ts.remote.cmd_applySetpoints,
            glycolSetpoint=self.glycol_target.value(),
            heatersSetpoint=self.heaters_target.value(),
        )
