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

import numpy as np
import pandas as pd
from lsst.ts.xml.tables.m1m3 import FATABLE_XFA, FATABLE_YFA, FATABLE_ZFA


class AccelerationAndVelocityFitter:
    """Class handling acceleration and velocities fits.

    Parameters
    ----------
    values: `pd.DataFrame`
        Value frame. Shall contain
        "[elevation|azimuth]_{kind}[Position|Velocity|Acceleration]" and
        "accelerometers_angularAcceleration[XYZ]" fields.
    kind: `str`
        Velocities kind. Expected either actual or demand for TMA values.
        Actual are preferred.
    acceleration_kind: `str`
        Velocities and accelerations kind. Expected either meters for DC
        accelerometer, or actual or demand for TMA. Meters are preferred.
    """

    def __init__(self, values: pd.DataFrame, kind: str, acceleration_kind: str):
        el_sin = np.sin(np.radians(values[f"elevation_{kind}Position"]))
        el_cos = np.cos(np.radians(values[f"elevation_{kind}Position"]))

        D2RAD = np.radians(1)

        V_azimuth = values[f"azimuth_{kind}Velocity"].mul(D2RAD)

        self.velocities = pd.DataFrame(
            {
                "X": values[f"elevation_{kind}Velocity"].mul(D2RAD),
                "Y": V_azimuth.mul(el_cos),
                "Z": V_azimuth.mul(el_sin),
            }
        )

        if acceleration_kind == "meters":
            self.accelerations = pd.DataFrame(
                {
                    "X": values[f"accelerometers_angularAccelerationX"].mul(D2RAD),
                    "Y": values[f"accelerometers_angularAccelerationY"].mul(D2RAD),
                    "Z": values[f"accelerometers_angularAccelerationZ"].mul(D2RAD),
                }
            )
        else:
            A_azimuth = values[f"azimuth_{kind}Acceleration"].mul(D2RAD)

            self.accelerations = pd.DataFrame(
                {
                    "X": values[f"elevation_{kind}Acceleration"].mul(D2RAD),
                    "Y": A_azimuth.mul(el_cos),
                    "Z": A_azimuth.mul(el_sin),
                }
            )

        self.aav = pd.DataFrame(
            {
                "V_x2": self.velocities["X"].pow(2),
                "V_y2": self.velocities["Y"].pow(2),
                "V_z2": self.velocities["Z"].pow(2),
                "V_xz": self.velocities["X"].mul(self.velocities["Z"]),
                "V_yz": self.velocities["Y"].mul(self.velocities["Z"]),
                "A_x": self.accelerations["X"],
                "A_y": self.accelerations["Y"],
                "A_z": self.accelerations["Z"],
            }
        )

        self.aav.fillna(0, inplace=True)

    def do_fit(self, mirror_forces: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Fit right hand side (mirror forces).

        Parameters
        ----------
        mirror_forces: pd.DataFrame
            Contains mirror forces. Columns with keys "X{x_index}",
            "Y{y_index}" and "Z{z_index}" forms rights side of equation
            self.aav @ x = {forces}, where x are the fitted coefficients.
        """
        coefficients = {}
        residuals = {}

        for fa in (
            [f"X{x}" for x in range(FATABLE_XFA)]
            + [f"Y{y}" for y in range(FATABLE_YFA)]
            + [f"Z{z}" for z in range(FATABLE_ZFA)]
        ):
            B = mirror_forces[fa] * -1000.0
            coefficients[fa], residuals[fa], rank, s = np.linalg.lstsq(
                self.aav, B, rcond=None
            )

        return (pd.DataFrame(coefficients), pd.DataFrame(residuals))
