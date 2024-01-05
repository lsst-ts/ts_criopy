# This file is part of ts_criopy.
#
# Developed for the Rubin Observatory Telescope and Site System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import pathlib
import unittest

import numpy as np
import pandas as pd
from lsst.ts.criopy.m1m3 import AccelerationTransformer


class AccelerationTransformerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.transformer = AccelerationTransformer(
            pathlib.Path(os.path.dirname(os.path.abspath(__file__))) / "data"
        )

    def test_calibrated(self) -> None:
        tested = pd.DataFrame(
            {
                "rawAccelerometer0": [0.1, 0.2],
                "rawAccelerometer1": [0.5, 0.6],
                "rawAccelerometer2": [0.7, 0.1],
                "rawAccelerometer3": [-0.2, -0.3],
                "rawAccelerometer4": [-0.3, 0.7],
                "rawAccelerometer5": [0.2, -0.3],
                "rawAccelerometer6": [0.1, -0.5],
                "rawAccelerometer7": [-0.34, 0.56],
            }
        )

        calibrated = self.transformer.calibrated(tested)

        np.testing.assert_allclose(
            calibrated.accelerometer0, [0.006616, 0.026546], rtol=1e-03
        )
        np.testing.assert_allclose(
            calibrated.accelerometer1, [0.98167, 1.18107], rtol=1e-03
        )


if __name__ == "__main__":
    unittest.main()
