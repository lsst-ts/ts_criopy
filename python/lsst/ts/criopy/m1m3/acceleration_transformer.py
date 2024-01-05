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

__all__ = ["AccelerationTransformer"]

import pathlib
from typing import Any

import pandas as pd
import yaml

# there are 4 2 axis accelerometers, totalling 8 channels
N_ACCELEROMETERS = 8


class AccelerationTransformer:
    """
    Reads M1M3 configuration. Transform raw values into calibrated values, and
    X Y Z accelerations.

    Paramaters
    ==========
    config_dir : `None | str | pathlib.Path = None`
        Configuration directory.
    """

    class Accelerometer:
        def __init__(self, config: Any):
            self.bias = config["Bias"]
            self.sensitivity = config["Sensitivity"]
            self.offset = config["Offset"]
            self.scalar = config["Scalar"]

        def __matmul__(self, value: Any) -> Any:
            return (value - self.bias) * self.sensitivity * self.scalar - self.offset

    def __init__(self, config_dir: None | str | pathlib.Path = None):
        self.accelerometeres: list[Any] = []
        self.distances: list[float] = [0, 0, 0]

        if config_dir is not None:
            self.load_config(config_dir)

    def load_config(self, config_dir: str | pathlib.Path) -> None:
        """Load M1M3 configuration files.

        Parameters
        ----------
        config_dir : `str | pathlib.Path`
            Directory where to look for configuration files.
        """
        config_dir = pathlib.Path(config_dir)
        config_file = config_dir / "_init.yaml"

        with open(config_file, "r") as file:
            config = yaml.safe_load(file)

        ac = config["AccelerometerSettings"]

        self.accelerometeres = []

        for accelerometer in range(N_ACCELEROMETERS):
            self.accelerometeres.append(
                self.Accelerometer(ac[f"Accelerometer{accelerometer + 1}"])
            )

        self.distances = [
            ac["AngularAccelerationXDistance"],
            ac["AngularAccelerationYDistance"],
            ac["AngularAccelerationZDistance"],
        ]

    def calibrated(self, raw: pd.DataFrame) -> pd.DataFrame:
        ret = pd.DataFrame()
        for acc in range(N_ACCELEROMETERS):
            ret[f"accelerometer{acc}"] = (
                self.accelerometeres[acc] @ raw[f"rawAccelerometer{acc}"]
            )

        return ret

    def xyz(self, calibrated: pd.DataFrame) -> pd.DataFrame:
        # calculating an angular acceleration from the difference of two linear
        # acceleration measured at two locations with different radial distance
        # to the center of rotation.
        return pd.DataFrame(
            {
                "accelerationX": (calibrated.accelerometer5 - calibrated.accelerometer7)
                / self.distances[0],
                "accelerationY": (calibrated.accelerometer2 - calibrated.accelerometer0)
                / self.distances[1],
                "accelerationZ": (calibrated.accelerometer4 - calibrated.accelerometer0)
                / self.distances[2],
            }
        )
