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

from ..M1M3FATable import FATABLE, FATABLE_XFA, FATABLE_YFA, FATABLE_ZFA


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

        fas = config["ForceActuatorSettings"]

        self.accelerations_tables: list[pd.DataFrame] = []
        self.velocity_tables: list[pd.DataFrame] = []

        tables_path = config_dir / "tables"

        for axis in "XYZ":
            self.accelerations_tables.append(
                self.__load_table(
                    tables_path / fas[f"Acceleration{axis}TablePath"],
                    FATABLE_ZFA,
                ),
            )
            self.velocity_tables.append(
                self.__load_table(
                    tables_path / fas[f"Velocity{axis}TablePath"],
                    FATABLE_ZFA,
                ),
            )

    def __load_table(self, filename: str | pathlib.Path, rows: int) -> pd.DataFrame:
        ret = pd.read_csv(filename)
        if len(ret.index) != rows:
            raise RuntimeError(
                f"Expected {rows} in {filename}, found {len(ret.index)}."
            )
        return ret.drop(columns=["ID"])

    def acceleration(self, accelerations: list[float]) -> AppliedForces:
        forces = [[0.0] * FATABLE_ZFA] * 3

        for idx, a in enumerate("XYZ"):
            forces[idx] = (
                pd.DataFrame([t[a] for t in self.accelerations_tables]).T.values
                @ accelerations
            ) / 1000.0

        return AppliedForces(
            list(reduce_to_x(forces[0])), list(reduce_to_y(forces[1])), forces[2]
        )

    def velocity(self, velocities: list[float]) -> AppliedForces:
        pass
