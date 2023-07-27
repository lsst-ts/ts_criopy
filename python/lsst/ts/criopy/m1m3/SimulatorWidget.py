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
from PySide2.QtWidgets import QDoubleSpinBox, QFormLayout, QPushButton, QWidget

from .Simulator import Simulator


class DegreeEntry(QDoubleSpinBox):
    def __init__(self, unit: str):
        super().__init__()
        self.setDecimals(3)
        self.setRange(-30, 30)
        self.setSingleStep(0.01)
        self.setSuffix(unit)
        self.setValue(0)


class HardpointForceEntry(QDoubleSpinBox):
    def __init__(self) -> None:
        super().__init__()
        self.setDecimals(1)
        self.setRange(-99000, 99000)
        self.setSingleStep(10)
        self.setSuffix(" N")
        self.setValue(0)


class HardpointMomentEntry(HardpointForceEntry):
    def __init__(self) -> None:
        super().__init__()
        self.setSuffix(" Nm")


class SimulatorWidget(QWidget):
    def __init__(self, simulator: Simulator):
        super().__init__()

        self.simulator = simulator

        layout = QFormLayout()

        self.hardpoints = [
            HardpointForceEntry(),
            HardpointForceEntry(),
            HardpointForceEntry(),
            HardpointForceEntry(),
            HardpointForceEntry(),
            HardpointForceEntry(),
        ]
        self.hp_fam = [
            HardpointForceEntry(),
            HardpointForceEntry(),
            HardpointForceEntry(),
            HardpointMomentEntry(),
            HardpointMomentEntry(),
            HardpointMomentEntry(),
        ]
        self.velocities = [
            DegreeEntry(" °/sec"),
            DegreeEntry(" °/sec"),
            DegreeEntry(" °/sec"),
        ]
        self.accelerations = [
            DegreeEntry(" °/sec\u00B2"),
            DegreeEntry(" °/sec\u00B2"),
            DegreeEntry(" °/sec\u00B2"),
        ]

        for hp in range(6):
            layout.addRow(f"Hardpoint {hp+1}", self.hardpoints[hp])

        for idx, axis in enumerate("XYZ"):
            layout.addRow(f"Offset Force {axis}", self.hp_fam[idx])

        for idx, axis in enumerate("XYZ"):
            layout.addRow(f"Offset Moment {axis}", self.hp_fam[idx + 3])

        for idx, axis in enumerate("XYZ"):
            layout.addRow(f"{axis} Velocity", self.velocities[idx])

        for idx, axis in enumerate("XYZ"):
            layout.addRow(f"{axis} Acceleration", self.accelerations[idx])

        recalculate = QPushButton("Set")
        recalculate.clicked.connect(self.recalculate)

        layout.addRow(recalculate)

        self.setLayout(layout)

    def recalculate(self) -> None:
        self.simulator.acceleration(np.radians([a.value() for a in self.accelerations]))
        self.simulator.hardpoint_fam([hp.value() for hp in self.hp_fam])
        self.simulator.hardpoint_forces([hp.value() for hp in self.hardpoints])
        self.simulator.velocity(np.radians([v.value() for v in self.velocities]))
