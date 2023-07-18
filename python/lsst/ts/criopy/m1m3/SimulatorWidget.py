# This file is part of M1M3 SS GUI.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org). See the COPYRIGHT file at the top - level directory
# of this distribution for details of code ownership.
#
# This program is free software : you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

__all__ = ["SimulatorWidget"]

import numpy as np
from PySide2.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QPushButton,
    QWidget,
)

from .Simulator import Simulator


class DegreeEntry(QDoubleSpinBox):
    def __init__(self, unit: str):
        super().__init__()
        self.setDecimals(3)
        self.setRange(-6, 6)
        self.setSingleStep(0.01)
        self.setSuffix(unit)
        self.setValue(0)


class AccelVel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.acceleration = DegreeEntry("°/sec")
        self.velocity = DegreeEntry("°/sec**2")

        layout = QHBoxLayout()
        layout.addWidget(self.velocity)
        layout.addWidget(self.acceleration)

        self.setLayout(layout)


class SimulatorWidget(QWidget):
    def __init__(self, simulator: Simulator):
        super().__init__()

        self.simulator = simulator

        layout = QFormLayout()

        self.accelvel = [AccelVel(), AccelVel(), AccelVel()]

        for idx, axis in enumerate("XYZ"):
            layout.addRow(f"{axis}", self.accelvel[idx])

        recalculate = QPushButton("Set")
        recalculate.clicked.connect(self.recalculate)

        layout.addRow(recalculate)

        self.setLayout(layout)

    def recalculate(self) -> None:
        self.simulator.acceleration(
            np.radians([a.acceleration.value() for a in self.accelvel])
        )
        self.simulator.velocity(np.radians([a.velocity.value() for a in self.accelvel]))
