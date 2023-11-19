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

__all__ = ["Simulator"]

import typing

from PySide2.QtCore import QObject, Signal

from .force_calculator import ForceCalculator


class SimulatedTopic:
    """Class simulating topic. Provides get method, to simulate salobj
    read_topic get method.

    Parameters
    latest: `ForceCalculator.AppliedForces`, optional
        Latest topic data.
    """

    def __init__(self, latest: ForceCalculator.AppliedForces | None = None) -> None:
        self.latest = latest

    def get(self) -> ForceCalculator.AppliedForces | None:
        """Simulate salobj get method.

        Returns
        -------
        topic: `ForceCalculator.AppliedForces`
            Current topic value.
        """
        return self.latest


class M1M3Remote:
    def __init__(self) -> None:
        pass

    def __getattr__(self, name: str) -> typing.Any:
        return SimulatedTopic()

    def emitted(self, name: str, forces: ForceCalculator.AppliedForces) -> None:
        setattr(self, name, SimulatedTopic(forces))


class Simulator(QObject):
    """This is the engine behind simulated control code. This approach is used
    to faciliate possible integration of additional features (like replay of
    system reactions from EFD data).

    Parameters
    ----------
    calculator: `ForceCalculator`
        Force calculator doing the hard work - calculating the forces.
    """

    appliedAccelerationForces = Signal(map)
    appliedBalanceForces = Signal(map)
    appliedForces = Signal(map)
    appliedOffsetForces = Signal(map)
    appliedVelocityForces = Signal(map)

    def __init__(self, calculator: ForceCalculator) -> None:
        super().__init__()

        self.force_calculator = calculator

        self.aaf = ForceCalculator.AppliedForces()
        self.abf = ForceCalculator.AppliedForces()
        self.avf = ForceCalculator.AppliedForces()
        self.all_forces = ForceCalculator.AppliedForces()
        self.offsets = ForceCalculator.AppliedForces()

        self.remote = M1M3Remote()

    def acceleration(self, accelerations: list[float]) -> None:
        """Calculate acceleration forces. Forces will be transmitted in
        appliedAccelerationForces pseudo-SAL signal.

        Parameters
        ----------
        acceleration: `[float]`
            Vector of three (XYZ) angular accelerations, in rad/sec^2.
        """
        self.aaf = self.force_calculator.acceleration(accelerations)
        self.remote.emitted("tel_appliedAccelerationForces", self.aaf)
        self.appliedAccelerationForces.emit(self.aaf)

    def applied_forces(self) -> None:
        """Calculate and distyribute appliedForces, sum of all applied forces."""
        self.all_forces = self.aaf  + self.abf + self.avf + self.offsets
        self.remote.emitted("tel_appliedForces", self.all_forces)
        self.appliedForces.emit(self.all_forces)


    def hardpoint_fam(self, fam: list[float]) -> None:
        """Calculate forces from hardpoint forces and moments. Those will be
        transmitted in appliedOffsetForces pseudo-SAL signal.

        Parameters
        ----------
        fam : `[float]`
            Vector of 3 (XYZ) forces and moments - fx, fy, fz, mx, my and mz.
        """
        self.offsets = self.force_calculator.forces_and_moments_forces(fam)
        self.remote.emitted("evt_appliedOffsetForces", self.offsets)
        self.appliedOffsetForces.emit(self.offsets)

    def hardpoint_forces(self, hardpoints: list[float]) -> None:
        """Calculate balance forces from hardpoints input. Simulates balance
        forces distribution (full conversion from hardpoint forces to per-FA
        forces). Results are published as appliedBalanceForces pseudo-SAL
        signal.

        Parameters
        ----------
        hardpoints : `[float]`
            Vector of 6 hardpoint forces, measured on M1M3 in load cells on top
            of the hardpoints.
        """
        self.abf = self.force_calculator.hardpoint_forces(hardpoints)
        self.remote.emitted("tel_appliedBalanceForces", self.abf)
        self.appliedBalanceForces.emit(self.abf)

    def velocity(self, velocities: list[float]) -> None:
        """Provide velocity compensation. Results are published in
        appliedVelocityForces pseudo-SAL signal.

        Parameters
        ----------
        velocities : `[float]`
            Vector of 3 angular velocities (XYZ), in rad/sec.
        """
        self.avf = self.force_calculator.velocity(velocities)
        self.remote.emitted("tel_appliedVelocityForces", self.avf)
        self.appliedVelocityForces.emit(self.avf)
