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

from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ..gui import DataDegC, DataFormWidget, Percent, Volt
from ..gui.sal import Axis, ChartWidget
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

        command_layout = QFormLayout()

        self.mixing_valve_target = QDoubleSpinBox()
        self.mixing_valve_target.setRange(0, 100)
        self.mixing_valve_target.setSingleStep(1)
        self.mixing_valve_target.setDecimals(2)
        self.mixing_valve_target.setSuffix("%")
        command_layout.addRow("Target", self.mixing_valve_target)

        set_mixing_valve = QPushButton("Set &Mixing Valve")
        set_mixing_valve.clicked.connect(self._set_mixing_valve)
        command_layout.addRow(set_mixing_valve)

        def temperature_target() -> QDoubleSpinBox:
            temperature_target_box = QDoubleSpinBox()
            temperature_target_box.setRange(-40, 50)
            temperature_target_box.setSingleStep(0.05)
            temperature_target_box.setDecimals(2)
            temperature_target_box.setSuffix("°C")
            return temperature_target_box

        self.glycol_target = temperature_target()
        self.heaters_target = temperature_target()

        command_layout.addRow("Glycol Setpoint", self.glycol_target)
        command_layout.addRow("Heaters Setpoint", self.heaters_target)

        set_setpoints = QPushButton("Set &Setpoints")
        set_setpoints.clicked.connect(self._set_setpoints)
        command_layout.addRow(set_setpoints)

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
                    ("Raw Position", Volt(field="rawValvePosition", fmt="0.05f")),
                    ("Position", Percent(field="valvePosition")),
                ],
            )
        )

        vlayout.addSpacing(20)

        sel_help = QLabel(
            "Setpoint control is used in non-engineering mode. "
            "Mixing valve control is active in engineering mode."
        )
        sel_help.setWordWrap(True)
        vlayout.addWidget(sel_help)
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

        plot_layout = QVBoxLayout()

        plot_layout.addWidget(
            ChartWidget(
                Axis("Raw (V)", m1m3ts.mixingValve).addValue("Raw", "rawValvePosition"),
                Axis("Percent (%)", m1m3ts.mixingValve).addValue("Percent", "valvePosition"),
            )
        )

        plot_layout.addWidget(
            ChartWidget(
                Axis("M1M3 Glycol (\u00b0C)", m1m3ts.glycolLoopTemperature)
                .addValue("M1M3 Supply", "mirrorCoolantSupplyTemperature")
                .addValue("M1M3 Return", "mirrorCoolantReturnTemperature")
            )
        )

        plot_layout.addWidget(
            ChartWidget(
                Axis("Telescope Glycol (\u00b0C)", m1m3ts.glycolLoopTemperature)
                .addValue("Telescope Supply", "telescopeCoolantSupplyTemperature")
                .addValue("Telescope Return", "telescopeCoolantReturnTemperature")
            )
        )

        hlayout.addLayout(plot_layout)

        self.setLayout(hlayout)

    @asyncSlot()
    async def _set_mixing_valve(self) -> None:
        await command(
            self,
            self.m1m3ts.remote.cmd_setMixingValve,
            mixingValveTarget=self.mixing_valve_target.value(),
        )

    @asyncSlot()
    async def _set_setpoints(self) -> None:
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
