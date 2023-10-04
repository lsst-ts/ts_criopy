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
from typing import Any, Generator

import numpy as np
import pandas as pd
import yaml
from lsst.ts.xml.tables.m1m3 import (
    FATABLE_XFA,
    FATABLE_YFA,
    FATABLE_ZFA,
    HP_COUNT,
    FATable,
)


def reduce_to_x(forces: list[float]) -> Generator[float, None, None]:
    """Reduces list of 156 forces used to store parameters into 12 X values.

    Parameters
    ----------
    forces : `[float]`
        156 value vector, with most values 0/ignored.

    Returns
    -------
    x_forces : `[float]`
        12 X forces values.
    """
    for fa in FATable:
        if fa.x_index is not None:
            yield forces[fa.index]


def reduce_to_y(forces: list[float]) -> Generator[float, None, None]:
    """Reduces list of 156 forces used to store parameters into 12 X values.

    Parameters
    ----------
    forces : `[float]`
        156 value vector, with some values 0/ignored for Z indices without Y
        force actuator.

    Returns
    -------
    y_forces : `[float]`
        100 Y forces values.
    """
    for fa in FATable:
        if fa.y_index is not None:
            yield forces[fa.index]


class ForceCalculator:
    """
    Reads M1M3 configuration, load tables and performs various transformation
    between hardpoints and forces.
    """

    fas: dict[str, Any] | None = None

    class AppliedForces:
        """Class simulating applied forces event data. Used as parameter for
        simulated force telemetry messages.

        All forces are usually in N, all moments in Nm.

        Parameters
        ----------
        x_forces: `[float]`
            Vector of X forces.
        y_forces: `[float]`
            Vector of Y forces.
        z_forces: `[float]`
            Vector of Z forces.
        fas: `{str, Any}`, optional
            Force Actuator Settings map. Holds MirrorCenterOfGravity values.

        Attributes
        ----------
        xForces : `[float]`
            Applied X forces. 12 values.
        yForces : `[float]`
            Applied Y forces. 100 values.
        zForces : `[float]`
            Applied Z forces. 156 values.
        fx : `float`
            Total X force, Sum of all X forces.
        fy : `float`
            Total Y force. Sum of all Y forces.
        fz : `float`
            Total Z force. Sum of all Z forces.
        mx : `float`
            Moment along X axis. Calculated from sum of individual
            contribution.
        my : `float`
            Moment along Y axis. Calculated from sum of individual
            contribution.
        mz : `float`
            Moment along Z axis. Calculated from sum of individual
            contribution.
        forceMagnitude : `float`
            Total force. Square root (
        """

        def __init__(
            self,
            x_forces: list[float],
            y_forces: list[float],
            z_forces: list[float],
            fas: dict[str, Any] | None = None,
        ):
            assert len(x_forces) == FATABLE_XFA
            assert len(y_forces) == FATABLE_YFA
            assert len(z_forces) == FATABLE_ZFA

            self.timestamp = 0
            # those values need to have same name as in SAL/DDS (including
            # capitalization style)
            self.xForces = x_forces
            self.yForces = y_forces
            self.zForces = z_forces

            self.fas = fas

            self.__calculate_forces_and_moments()

        def __calculate_forces_and_moments(self) -> None:
            self.fx = 0.0
            self.fy = 0.0
            self.fz = 0.0
            self.mx = 0.0
            self.my = 0.0
            self.mz = 0.0

            for row in FATable:
                fa_fx = 0.0 if row.x_index is None else self.xForces[row.x_index]
                fa_fy = 0.0 if row.y_index is None else self.yForces[row.y_index]
                fa_fz = self.zForces[row.z_index]

                rx = row.x_position
                ry = row.y_position
                rz = row.z_position

                if self.fas is not None:
                    rx -= self.fas["MirrorCenterOfGravityX"]
                    ry -= self.fas["MirrorCenterOfGravityY"]
                    rz -= self.fas["MirrorCenterOfGravityZ"]

                self.fx += fa_fx
                self.fy += fa_fy
                self.fz += fa_fz
                self.mx += (fa_fz * ry) - (fa_fy * rz)
                self.my += (fa_fx * rz) - (fa_fz * rx)
                self.mz += (fa_fy * rx) - (fa_fx * ry)

            self.forceMagnitude = np.sqrt(self.fx**2 + self.fy**2 + self.fz**2)

        def __add__(self, obj2: Any) -> "ForceCalculator.AppliedForces":
            if isinstance(obj2, ForceCalculator.AppliedForces):
                return ForceCalculator.AppliedForces(
                    np.array(self.xForces) + np.array(obj2.xForces),
                    np.array(self.yForces) + np.array(obj2.yForces),
                    np.array(self.zForces) + np.array(obj2.zForces),
                    self.fas,
                )
            return NotImplemented

    def __init__(self, config_dir: None | str | pathlib.Path = None):
        self.forces_to_mirror: list[pd.DataFrame] = []
        self.moments_to_mirror: list[pd.DataFrame] = []
        self.acceleration_tables: list[pd.DataFrame] = []
        self.velocity_tables: list[pd.DataFrame] = []

        if config_dir is not None:
            self.load_config(config_dir)

    def get_applied_forces(
        self, x_forces: list[float], y_forces: list[float], z_forces: list[float]
    ) -> AppliedForces:
        """Return ForceCalculator.AppliedForces, constructed from vector
        source.

        Parameters
        ----------
        x_forces: `[float]`
            Vector of X forces. 12, FATABLE_XFA values.
        y_forces: `[float]`
            Vector of Y forces. 100, FATABLE_YFA values.
        z_forces: `[float]`
            Vector of Z forces. 156, FATABLE_ZFA values.

        Returns
        -------
        applied_forces : `AppliedForces`
            AppliedForces class holding forces details.
        """
        return ForceCalculator.AppliedForces(x_forces, y_forces, z_forces, self.fas)

    def get_applied_forces_from_mirror(
        self, forces: list[list[float]]
    ) -> AppliedForces:
        """Return ForceCalculator.AppliedForces from mirror forces. Each passed
        array shall have length equal to FATABLE_ZFA (156).

        Parameters
        ----------
        forces: `[[float]]`
            Mirror forces. Vector of three (XYZ) mirror forces (length of each
            array equals to FATABLE_ZFA, 156).
        """
        for i in range(3):
            assert len(forces[i]) == FATABLE_ZFA

        return self.get_applied_forces(
            list(reduce_to_x(forces[0])),
            list(reduce_to_y(forces[1])),
            forces[2],
        )

    def get_applied_forces_from_series(self, forces: pd.Series) -> pd.Series:
        return self.get_applied_forces(
            forces[:FATABLE_XFA].values,
            forces[FATABLE_XFA : FATABLE_XFA + FATABLE_YFA].values,
            forces[FATABLE_XFA + FATABLE_YFA :].values,
        )

    def load_config(self, config_dir: str | pathlib.Path) -> None:
        """Load ForceActuator configuration files. A standard MTM1M3
        configuration file structure, used by the M1M3 SS CSC, is expected. A
        directory with _init.yaml file, and required tables in its tables
        subdirectory.

        Parameters
        ----------
        config_dir : `str | pathlib.Path`
            Directory where to look for configuration files.
        """
        config_dir = pathlib.Path(config_dir)
        config_file = config_dir / "_init.yaml"

        with open(config_file, "r") as file:
            config = yaml.safe_load(file)

        self.fas = config["ForceActuatorSettings"]
        assert self.fas is not None

        self.forces_to_mirror = []
        self.moments_to_mirror = []
        self.acceleration_tables = []
        self.velocity_tables = []

        tables_path = config_dir / "tables"

        self.hardpoint_to_forces_moments = self.__load_table(
            tables_path / self.fas["HardpointForceMomentTablePath"], HP_COUNT
        ).drop(columns="ID")

        for axis in "XYZ":
            self.forces_to_mirror.append(
                self.__load_table(
                    tables_path / self.fas[f"ForceDistribution{axis}TablePath"],
                    FATABLE_ZFA,
                ),
            )
            self.moments_to_mirror.append(
                self.__load_table(
                    tables_path / self.fas[f"MomentDistribution{axis}TablePath"],
                    FATABLE_ZFA,
                ),
            )
            self.acceleration_tables.append(
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

        self.__convert_tables()

    def save(self, out_dir: pathlib.Path) -> None:
        """Save modified tables to out_dir.

        Parameters
        ----------
        out_dir: `pathlib.Path`
            Path where table shall be saved.
        """
        assert self.fas is not None

        for i, axis in enumerate("XYZ"):
            self.acceleration_tables[i].to_csv(
                out_dir / self.fas[f"Acceleration{axis}TablePath"],
                index=False,
            )
            self.velocity_tables[i].to_csv(
                out_dir / self.fas[f"Velocity{axis}TablePath"],
                index=False,
            )

        for i, axis in enumerate("XY"):
            self.velocity_tables[i + 3].to_csv(
                out_dir / self.fas[f"Velocity{axis}ZTablePath"],
                index=False,
            )

    def __convert_tables(self) -> None:
        """Convert tables for efficient calculations."""
        self._fam_computation: list[pd.DataFrame] = []
        self._acceleration_computation: list[pd.DataFrame] = []
        self._velocity_computation: list[pd.DataFrame] = []
        for axis in "XYZ":
            self._fam_computation.append(
                pd.DataFrame(
                    [t[axis] for t in self.forces_to_mirror]
                    + [t[axis] for t in self.moments_to_mirror]
                ).T
            )
            self._acceleration_computation.append(
                pd.DataFrame([(t[axis] / 1000.0) for t in self.acceleration_tables]).T
            )
            self._velocity_computation.append(
                pd.DataFrame([(t[axis] / 1000.0) for t in self.velocity_tables]).T
            )

    def __load_table(self, filename: str | pathlib.Path, rows: int) -> pd.DataFrame:
        """Load table from CSV.

        Parameters
        ----------
        filename : `str | pathlib.Path`
            Load table data from that CSV file.
        rows : `int`
            Expected number of rows.

        Throws
        ------
        RuntimeError
            When number of rows in table doesn't match rows argument.
        """
        ret = pd.read_csv(filename)
        if len(ret.index) != rows:
            raise RuntimeError(
                f"Expected {rows} in {filename}, found {len(ret.index)}."
            )
        return ret

    def hardpoint_forces_and_moments(self, hardpoints: list[float]) -> pd.DataFrame:
        return self.hardpoint_to_forces_moments @ hardpoints

    def forces_and_moments_forces(self, fam: list[float]) -> AppliedForces:
        forces = []
        for m in self._fam_computation:
            forces.append(m @ fam)

        return self.get_applied_forces_from_mirror(forces)

    def hardpoint_forces(self, hardpoints: list[float]) -> AppliedForces:
        return self.forces_and_moments_forces(
            self.hardpoint_forces_and_moments(hardpoints).values
        )

    def acceleration(self, accelerations: list[float]) -> AppliedForces:
        """Calculates acceleration forces.

        Parameters
        ----------
        accelerations: list[float]
            3D (XYZ) angular acceleration vector, as provide by TMA (velocity
            derivation) or accelerometers. In radians per second square.

        Returns
        -------
        accelerations_forces: AppliedForces
            Calculated acceleration forces.
        """
        forces = []
        for m in self._acceleration_computation:
            forces.append(m @ accelerations)

        return self.get_applied_forces_from_mirror(forces)

    def set_acceleration_and_velocity(self, sets: pd.DataFrame) -> None:
        """Set acceleration and velocities coefficients from fitted dataset.
        Used to override force calculator inertial model with calculated
        values. This can be used to check model's fit.

        Parameters
        ----------
        sets : pd.DataFrame
            New acceleration and velocities coefficients. Set of 8 member
            vectors (XX, YY, ZZ, XZ and YZ angular velocities coefficients,
            followed by X, Y and Z angular acceleration values). 12 X, 100 Y
            and 156 Z vectors in columns, marked X0..11, Y0..99 and Z0..156.
        """
        self.acceleration_tables = []
        self.velocity_tables = []

        def make_zero() -> pd.DataFrame:
            return pd.DataFrame(
                {
                    "ID": [fa.index for fa in FATable],
                    "X": [0] * FATABLE_ZFA,
                    "Y": [0] * FATABLE_ZFA,
                    "Z": [0] * FATABLE_ZFA,
                }
            )

        for tab in range(3):
            self.acceleration_tables.append(make_zero())

        for tab in range(5):
            self.velocity_tables.append(make_zero())

        for row in FATable:

            def do_update(a: str, idx: int, coeff: pd.Series) -> None:
                for tab in range(5):
                    self.velocity_tables[tab].loc[idx, a] += coeff[tab]
                for tab in range(3):
                    self.acceleration_tables[tab].loc[idx, a] += coeff[tab + 5]

            if row.x_index is not None:
                do_update("X", row.index, sets[f"X{row.x_index}"])
            if row.y_index is not None:
                do_update("Y", row.index, sets[f"Y{row.y_index}"])
            do_update("Z", row.index, sets[f"Z{row.z_index}"])

        self.__convert_tables()

    def update_acceleration_and_velocity(self, updates: pd.DataFrame) -> None:
        """Update current acceleration and velocities coefficients. Should be
        used to iteratively update

        Parameters
        ----------
        updates : pd.DataFrame
        """
        for row in FATable:

            def do_update(a: str, idx: int, coeff: pd.Series) -> None:
                for tab in range(5):
                    self.velocity_tables[tab].loc[idx, a] += coeff[tab]
                for tab in range(3):
                    self.acceleration_tables[tab].loc[idx, a] += coeff[tab + 5]

            if row.x_index is not None:
                do_update("X", row.index, updates[f"X{row.x_index}"])
            if row.y_index is not None:
                do_update("Y", row.index, updates[f"Y{row.y_index}"])
            do_update("Z", row.index, updates[f"Z{row.z_index}"])

        self.__convert_tables()

    def velocity(self, velocities: list[float]) -> AppliedForces:
        """Calculate velocity forces.

        Parameters
        ----------
        velocities: `[float]`
            3D angular velocity vector (XYZ). In radians per seccond.

        Returns
        -------
        velocity_forces: `AppliedForces`
            Applied velocity forces.
        """
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

        return self.get_applied_forces_from_mirror(forces)
