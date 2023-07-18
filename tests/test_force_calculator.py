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
from lsst.ts.criopy import M1M3FATable
from lsst.ts.criopy.m1m3.ForceCalculator import ForceCalculator


class ForceCalculatorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.calculator = ForceCalculator(
            pathlib.Path(os.path.dirname(os.path.abspath(__file__))) / "data"
        )

    def test_acceleration(self) -> None:
        acceleration = self.calculator.acceleration([0, 0, 0])

        np.testing.assert_array_equal(
            acceleration.xForces, [0] * M1M3FATable.FATABLE_XFA
        )
        np.testing.assert_array_equal(
            acceleration.yForces, [0] * M1M3FATable.FATABLE_YFA
        )
        np.testing.assert_array_equal(
            acceleration.zForces, [0] * M1M3FATable.FATABLE_ZFA
        )

        acceleration = self.calculator.acceleration([1, 0, 0])

        np.testing.assert_array_equal(
            acceleration.xForces, [0, 1] + [0] * (M1M3FATable.FATABLE_XFA - 3) + [2]
        )
        np.testing.assert_array_equal(
            acceleration.yForces, [0] * M1M3FATable.FATABLE_YFA
        )
        np.testing.assert_array_equal(
            acceleration.zForces, [0] * M1M3FATable.FATABLE_ZFA
        )

    def test_velocity(self) -> None:
        velocity = self.calculator.velocity([0, 0, 0])

        np.testing.assert_array_equal(velocity.xForces, [0] * M1M3FATable.FATABLE_XFA)
        np.testing.assert_array_equal(velocity.yForces, [0] * M1M3FATable.FATABLE_YFA)
        np.testing.assert_array_equal(velocity.zForces, [0] * M1M3FATable.FATABLE_ZFA)

        velocity = self.calculator.velocity([1, 2, 3])

        np.testing.assert_array_equal(
            velocity.xForces, [0, 88] + [0] * (M1M3FATable.FATABLE_XFA - 3) + [18]
        )
        np.testing.assert_array_equal(
            velocity.yForces, [18] + [0] * (M1M3FATable.FATABLE_YFA - 2) + [15]
        )
        np.testing.assert_array_equal(
            velocity.zForces,
            [0, 12] + [0] * (M1M3FATable.FATABLE_ZFA - 8) + [9, 0, 0, 0, 0, 21],
        )


if __name__ == "__main__":
    unittest.main()
