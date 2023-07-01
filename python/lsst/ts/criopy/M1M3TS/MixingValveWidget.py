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

import typing

from asyncqt import asyncSlot
from PySide2.QtCore import Slot
from PySide2.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..GUI import DataFormWidget, DockWindow, Percent, TimeChart, TimeChartView, Volt
from ..salcomm import MetaSAL, command


class MixingValveWidget(DockWindow):
    """Displays Mixing Valve data."""

    def __init__(self, m1m3ts: MetaSAL):
        super().__init__("Mixing valve")
        self.m1m3ts = m1m3ts

        commandLayout = QFormLayout()

        self.target = QDoubleSpinBox()
        self.target.setRange(0, 100)
        self.target.setSingleStep(1)
        self.target.setDecimals(2)
        self.target.setSuffix("%")
        commandLayout.addRow("Target", self.target)

        setMixingValve = QPushButton("Set")
        setMixingValve.clicked.connect(self._setMixingValve)
        commandLayout.addRow(setMixingValve)

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
        vlayout.addLayout(commandLayout)
        vlayout.addStretch()

        hlayout = QHBoxLayout()
        hlayout.addLayout(vlayout)

        self.mixingValveChart = TimeChart(
            {
                "Raw (V)": ["Raw Position"],
                "Percent (%)": ["Position"],
            }
        )

        hlayout.addWidget(TimeChartView(self.mixingValveChart))

        widget = QWidget()
        widget.setLayout(hlayout)

        self.setWidget(widget)

        self.m1m3ts.mixingValve.connect(self.mixingValve)

    @Slot()
    def mixingValve(self, data: typing.Any) -> None:
        self.mixingValveChart.append(
            data.private_sndStamp,
            [data.rawValvePosition],
            axis_index=0,
        )

        self.mixingValveChart.append(
            data.private_sndStamp,
            [data.valvePosition],
            axis_index=1,
        )

    @asyncSlot()
    async def _setMixingValve(self) -> None:
        await command(
            self,
            self.m1m3ts.remote.cmd_setMixingValve,
            mixingValveTarget=self.target.value(),
        )
