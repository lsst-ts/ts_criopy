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

from .ForceCalculator import AppliedForces, ForceCalculator


class SimulatedTopic:
    def __init__(self, latest: AppliedForces | None = None) -> None:
        self.latest = latest

    def get(self) -> AppliedForces | None:
        return self.latest


class M1M3Remote:
    def __init__(self) -> None:
        pass

    def __getattr__(self, name: str) -> typing.Any:
        return SimulatedTopic()

    def emitted(self, name: str, forces: AppliedForces) -> None:
        setattr(self, name, SimulatedTopic(forces))


class Simulator(QObject):
    appliedAccelerationForces = Signal(map)
    appliedVelocityForces = Signal(map)

    def __init__(self, calculator: ForceCalculator) -> None:
        super().__init__()

        self.force_calculator = calculator

        self.remote = M1M3Remote()

    def acceleration(self, accelerations: list[float]) -> None:
        aaf = self.force_calculator.acceleration(accelerations)
        self.remote.emitted("tel_appliedAccelerationForces", aaf)
        self.appliedAccelerationForces.emit(aaf)

    def velocity(self, velocities: list[float]) -> None:
        avf = self.force_calculator.velocity(velocities)
        self.remote.emitted("tel_appliedVelocityForces", avf)
        self.appliedVelocityForces.emit(avf)
