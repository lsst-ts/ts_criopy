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

__all__ = ["ForceCalculator"]

import pathlib
from typing import Generator

import numpy as np
import pandas as pd
import yaml

from ..M1M3FATable import FATABLE, FATABLE_XFA, FATABLE_YFA, FATABLE_ZFA, HP_COUNT


def calculate_forces_and_moments(
    x_forces: list[float] = [0] * FATABLE_XFA,
    y_forces: list[float] = [0] * FATABLE_YFA,
    z_forces: list[float] = [0] * FATABLE_ZFA,
) -> list[float]:
    ret = [np.sum(x_forces), np.sum(y_forces), np.sum(z_forces), 0.0, 0.0, 0.0]

    for row in FATABLE:
        fx = 0.0 if row.x_index is None else x_forces[row.x_index]
        fy = 0.0 if row.y_index is None else y_forces[row.y_index]
        fz = z_forces[row.z_index]

        ret += [
            fx,
            fy,
            fz,
            (fz * row.y_position) - (fy * row.z_position),
            (fx * row.z_position) - (fz * row.x_position),
            (fy * row.x_position) - (fx * row.y_position),
        ]

    return ret


def reduce_to_x(forces: list[float]) -> Generator[float, None, None]:
    for fa in FATABLE:
        if fa.x_index is not None:
            yield forces[fa.index]


def reduce_to_y(forces: list[float]) -> Generator[float, None, None]:
    for fa in FATABLE:
        if fa.y_index is not None:
            yield forces[fa.index]


class AppliedForces:
    def __init__(
        self, x_forces: list[float], y_forces: list[float], z_forces: list[float]
    ):
        self.timestamp = 0
        self.xForces = x_forces
        self.yForces = y_forces
        self.zForces = z_forces

        fam = calculate_forces_and_moments(x_forces, y_forces, z_forces)
        self.fx = fam[0]
        self.fy = fam[1]
        self.fz = fam[2]
        self.mx = fam[3]
        self.my = fam[4]
        self.mz = fam[5]


class AppliedFullMirrorForces(AppliedForces):
    def __init__(self, forces: list[list[float]]):
        super().__init__(
            list(reduce_to_x(forces[0])), list(reduce_to_y(forces[1])), forces[2]
        )


class ForceCalculator:
    """
    Reads M1M3 configuration, load tables and performs various transformation
    between hardpoints and forces.
    """

    def __init__(self, config_dir: None | str | pathlib.Path = None):
        if config_dir is not None:
            self.load_config(config_dir)

    def load_config(self, config_dir: str | pathlib.Path) -> None:
        config_dir = pathlib.Path(config_dir)
        config_file = config_dir / "_init.yaml"

        with open(config_file, "r") as file:
            config = yaml.safe_load(file)

        self.fas = config["ForceActuatorSettings"]

        self.forces_and_moments_to_mirror: list[pd.DataFrame] = []
        self.accelerations_tables: list[pd.DataFrame] = []
        self.velocity_tables: list[pd.DataFrame] = []

        tables_path = config_dir / "tables"

        self.hardpoint_to_forces_moments = self.__load_table(
            tables_path / self.fas["HardpointForceMomentTablePath"], HP_COUNT
        )

        for axis in "XYZ":
            fam = self.__load_table(
                tables_path / self.fas[f"ForceDistribution{axis}TablePath"], FATABLE_ZFA
            )
            fam[["mX", "mY", "mZ"]] = self.__load_table(
                tables_path / self.fas[f"MomentDistribution{axis}TablePath"],
                FATABLE_ZFA,
            )
            self.forces_and_moments_to_mirror.append(fam)

            self.accelerations_tables.append(
                self.__load_table(
                    tables_path / self.fas[f"Acceleration{axis}TablePath"],
                    FATABLE_ZFA,
                ),
            )
            self.velocity_tables.append(
                self.__load_table(
                    tables_path / self.fas[f"Velocity{axis}TablePath"],
                    FATABLE_ZFA,
                ),
            )

        for axis in "XY":
            self.velocity_tables.append(
                self.__load_table(
                    tables_path / self.fas[f"Velocity{axis}ZTablePath"],
                    FATABLE_ZFA,
                ),
            )

        self.convert_tables()

    def save(self, out_dir: pathlib.Path) -> None:
        """Save modified table to out_dir.

        Parameters
        ----------
        out_dir: `pathlib.Path`
            Path where table shall be saved.
        """
        for i, axis in enumerate("XYZ"):
            self.accelerations_tables[i].to_csv(
                out_dir / self.fas[f"Acceleration{axis}TablePath"]
            )
            self.velocity_tables[i].to_csv(
                out_dir / self.fas[f"Velocity{axis}TablePath"]
            )

        for i, axis in enumerate("XY"):
            self.velocity_tables[i + 3].to_csv(
                out_dir / self.fas[f"Velocity{axis}ZTablePath"]
            )

    def convert_tables(self) -> None:
        # convert tables for efficient calculation
        self._acceleration_computation: list[pd.DataFrame] = []
        self._velocity_computation: list[pd.DataFrame] = []
        for axis in "XYZ":
            self._acceleration_computation.append(
                pd.DataFrame([(t[axis] / 1000.0) for t in self.accelerations_tables]).T
            )
            self._velocity_computation.append(
                pd.DataFrame([(t[axis] / 1000.0) for t in self.velocity_tables]).T
            )

    def __load_table(self, filename: str | pathlib.Path, rows: int) -> pd.DataFrame:
        ret = pd.read_csv(filename)
        if len(ret.index) != rows:
            raise RuntimeError(
                f"Expected {rows} in {filename}, found {len(ret.index)}."
            )
        return ret.drop(columns=["ID"])

    def hardpoint_forces_and_moments(self, hardpoints: list[float]) -> pd.DataFrame:
        return self.hardpoint_to_forces_moments @ hardpoints

    def forces_and_moments_forces(self, fam: list[float]) -> AppliedForces:
        forces = []
        for m in self.forces_and_moments_to_mirror:
            forces.append(m @ fam)

        return AppliedFullMirrorForces(forces)

    def hardpoint_forces(self, hardpoints: list[float]) -> AppliedForces:
        return self.forces_and_moments_forces(
            self.hardpoint_forces_and_moments(hardpoints).values
        )

    def acceleration(self, accelerations: list[float]) -> AppliedForces:
        forces = []
        for m in self._acceleration_computation:
            forces.append(m @ accelerations)

        return AppliedFullMirrorForces(forces)

    def update_acceleration_and_velocity(self, updates: pd.DataFrame) -> None:
        for row in FATABLE:
            def write_accel_vel(a:str, idx: int, coeff: pd.Series ) -> None:
                for tab in range(5):
                    self.velocity_tables[tab][a][idx] = coeff[i]
                for tab in range(3):
                    self.accelerations_tables[tab][a][idx] = coeff[i + 5]
            if row.x_index is not None:
                write_accel_vel("X", row.index, updates[f"X{row.x_index}"])
            if row.y_index is not None:
                write_accel_vel("Y", row.index, updates[f"Y{row.y_index}"])
            write_accel_vel("Z", row.index, updates[f"Z{row.z_index}"])

    def velocity(self, velocities: list[float]) -> AppliedForces:
        vector = np.hstack(
            [
                np.square(velocities),
                [
                    velocities[0] * velocities[2],
                    velocities[1] * velocities[2],
                ],
            ]
        )
        forces = []
        for m in self._velocity_computation:
            forces.append(m @ vector)

        return AppliedFullMirrorForces(forces)
