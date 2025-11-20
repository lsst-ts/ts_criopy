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
from lsst.ts.m1m3.utils import ForceCalculator
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .simulator import Simulator


class DegreeEntry(QDoubleSpinBox):
    """Entry for degrees input."""

    def __init__(self) -> None:
        super().__init__()
        self.setDecimals(3)
        self.setRange(-30, 190)
        self.setSingleStep(1)
        self.setSuffix(" °")
        self.setValue(90)


class DegreeTimeEntry(QDoubleSpinBox):
    """Entry for degrees/time (sec, sec^2) input."""

    def __init__(self, unit: str):
        super().__init__()
        self.setDecimals(3)
        self.setRange(-30, 30)
        self.setSingleStep(0.01)
        self.setSuffix(unit)
        self.setValue(0)


class ForceStatistics(QWidget):
    """Display per-quadrant statistics"""

    def __init__(self) -> None:
        super().__init__()

        layout = QGridLayout()
        layout.addWidget(QLabel("Force X"), 0, 1)
        layout.addWidget(QLabel("Force Y"), 0, 2)
        layout.addWidget(QLabel("Force Z"), 0, 3)
        layout.addWidget(QLabel("Moment X"), 0, 4)
        layout.addWidget(QLabel("Moment Y"), 0, 5)
        layout.addWidget(QLabel("Moment Z"), 0, 6)
        layout.addWidget(QLabel("Total"), 0, 7)

        layout.addWidget(QLabel("Q/off"), 0, 0)
        layout.addWidget(QLabel("1st"), 1, 0)
        layout.addWidget(QLabel("2nd"), 2, 0)
        layout.addWidget(QLabel("3rd"), 3, 0)
        layout.addWidget(QLabel("4th"), 4, 0)
        layout.addWidget(QLabel("X off"), 5, 0)
        layout.addWidget(QLabel("Y off"), 6, 0)
        layout.addWidget(QLabel("Z off"), 7, 0)

        self.labels = [[QLabel() for col in range(7)] for row in range(7)]

        for row in range(7):
            for col in range(7):
                layout.addWidget(self.labels[row][col], row + 1, col + 1)

        self.setLayout(layout)

    def set_forces(self, forces: ForceCalculator.AppliedForces) -> None:
        def populate_row(row: int, f: ForceCalculator.AppliedForces) -> None:
            for col, field in enumerate(["fx", "fy", "fz", "mx", "my", "mz", "forceMagnitude"]):
                self.labels[row][col].setText(f"{getattr(f, field):.2f}")

        for quadrant in range(1, 5):
            populate_row(
                quadrant - 1,
                forces.clear_quadrants(*[q for q in range(1, 5) if q != quadrant]),
            )

        populate_row(
            4,
            ForceCalculator.AppliedForces(y_forces=forces.yForces, z_forces=forces.zForces),
        )

        populate_row(
            5,
            ForceCalculator.AppliedForces(x_forces=forces.xForces, z_forces=forces.zForces),
        )

        populate_row(
            6,
            ForceCalculator.AppliedForces(x_forces=forces.xForces, y_forces=forces.yForces),
        )


class HardpointForceEntry(QDoubleSpinBox):
    """Entry for mirror forces."""

    def __init__(self) -> None:
        super().__init__()
        self.setDecimals(1)
        self.setRange(-99000, 99000)
        self.setSingleStep(10)
        self.setSuffix(" N")
        self.setValue(0)


class HardpointMomentEntry(HardpointForceEntry):
    """Entry for mirror moments."""

    def __init__(self) -> None:
        super().__init__()
        self.setSuffix(" Nm")


class SimulatorWidget(QWidget):
    """Displays fields to enter values for simulator.

    Parameters
    ----------
    simulator : Simulator
        Simulator instance - controller.
    """

    def __init__(self, simulator: Simulator):
        super().__init__()

        self.simulator = simulator

        layout = QVBoxLayout()

        form = QFormLayout()

        self.elevation = DegreeEntry()

        form.addRow("Elevation", self.elevation)

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
            DegreeTimeEntry(" °/sec"),
            DegreeTimeEntry(" °/sec"),
            DegreeTimeEntry(" °/sec"),
        ]
        self.accelerations = [
            DegreeTimeEntry(" °/sec\u00b2"),
            DegreeTimeEntry(" °/sec\u00b2"),
            DegreeTimeEntry(" °/sec\u00b2"),
        ]

        for hp in range(6):
            form.addRow(f"Hardpoint {hp + 1}", self.hardpoints[hp])

        for idx, axis in enumerate("XYZ"):
            form.addRow(f"Offset Force {axis}", self.hp_fam[idx])

        for idx, axis in enumerate("XYZ"):
            form.addRow(f"Offset Moment {axis}", self.hp_fam[idx + 3])

        for idx, axis in enumerate("XYZ"):
            form.addRow(f"{axis} Velocity", self.velocities[idx])

        for idx, axis in enumerate("XYZ"):
            form.addRow(f"{axis} Acceleration", self.accelerations[idx])

        recalculate = QPushButton("Set")
        recalculate.clicked.connect(self.recalculate)

        form.addRow(recalculate)

        self._force_statistics = ForceStatistics()

        form_hbox = QHBoxLayout()
        form_hbox.addLayout(form)
        form_hbox.addStretch()

        layout.addLayout(form_hbox)
        layout.addWidget(self._force_statistics)
        layout.addStretch()

        self.setLayout(layout)

    def recalculate(self) -> None:
        """Called when new forces shall be calculated."""
        self.simulator.acceleration(np.radians([a.value() for a in self.accelerations]))
        self.simulator.elevation(self.elevation.value())
        self.simulator.hardpoint_fam([hp.value() for hp in self.hp_fam])
        self.simulator.hardpoint_forces([hp.value() for hp in self.hardpoints])
        self.simulator.velocity(np.radians([v.value() for v in self.velocities]))
        self.simulator.applied_forces()
        self._force_statistics.set_forces(self.simulator.all_forces)
