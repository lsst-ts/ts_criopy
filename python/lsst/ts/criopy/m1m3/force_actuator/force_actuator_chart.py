# This file is part of M1M3 SS GUI.
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

import asyncio
from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.tables.m1m3 import ForceActuatorData
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGridLayout, QSizePolicy, QWidget

from ...gui import TimeChart, TimeChartView
from ...salcomm import MetaSAL


class ForceActuatorChart(TimeChartView):
    def __init__(self, fa: ForceActuatorData):
        super().__init__()

        self.fa = fa

        def add_chart()->None:
            axis: list[str] = []
            if fa.x_index is not None:
                axis.append("X")
            if fa.y_index is not None:
                axis.append("Y")
            axis.append("Z")
            items = (
                ["Applied " + a for a in axis] + [None] + ["Measured " + a for a in axis]
            )

            self.setChart(TimeChart({"Force (N)": items}))

        asyncio.get_event_loop().call_soon(add_chart)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

    def applied_forces(self, data: BaseMsgType) -> None:
        """Adds applied forces to graph."""
        chart_data: list[float] = []
        if self.fa.x_index is not None:
            chart_data.append(data.xForces[self.fa.x_index])
        if self.fa.y_index is not None:
            chart_data.append(data.yForces[self.fa.y_index])
        if self.fa.z_index is not None:
            chart_data.append(data.zForces[self.fa.z_index])

        self.chart().append(data.timestamp, chart_data, cache_index=0, update=True)


    def force_actuator_data(self, data: BaseMsgType) -> None:
        """Adds measured forces to graph."""
        chart_data: list[float] = []
        if self.fa.x_index is not None:
            chart_data.append(data.xForce[self.fa.x_index])
        if self.fa.y_index is not None:
            chart_data.append(data.yForce[self.fa.y_index])
        if self.fa.z_index is not None:
            chart_data.append(data.zForce[self.fa.z_index])

        self.chart().append(data.timestamp, chart_data, cache_index=1, update=True)


class ForceChartWidget(QWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()

        self.actuators: dict[int, ForceActuatorChart] = {}

        self.setLayout(QGridLayout())

        m1m3.appliedForces.connect(self.applied_forces)
        m1m3.forceActuatorData.connect(self.force_actuator_data)

    def add(self, fa: ForceActuatorData) -> None:
        for count in range(10):
            if self.layout().itemAtPosition(count % 2, int(count / 2)) is None:
                break

        if count >= 10:
            print("Already too much plots - not adding ", fa.actuator_id)
            return

        chart = ForceActuatorChart(fa)
        self.actuators[fa.actuator_id] = chart

        self.layout().addWidget(chart, count % 2, int(count / 2))

    def remove(self, fa: ForceActuatorData) -> None:
        if fa.actuator_id in self.actuators:
            self.layout().removeWidget(self.actuators[fa.actuator_id])
            self.actuators[fa.actuator_id].hide()
            del self.actuators[fa.actuator_id]

    @Slot()
    def applied_forces(self, data: BaseMsgType) -> None:
        for actuator in self.actuators.values():
            actuator.applied_forces(data)

    @Slot()
    def force_actuator_data(self, data: BaseMsgType) -> None:
        for actuator in self.actuators.values():
            actuator.force_actuator_data(data)
