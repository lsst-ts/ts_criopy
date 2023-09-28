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
from lsst.ts.criopy import m1m3_fa_table
from lsst.ts.criopy.m1m3 import ForceCalculator


class ForceCalculatorTestCase(unittest.TestCase):
    """Tests ForceCalculator."""

    def setUp(self) -> None:
        self.calculator = ForceCalculator(
            pathlib.Path(os.path.dirname(os.path.abspath(__file__))) / "data"
        )

    def test_appliedForces(self) -> None:
        a = self.calculator.get_applied_forces(
            [1] * m1m3_fa_table.FATABLE_XFA,
            [2] * m1m3_fa_table.FATABLE_YFA,
            [3] * m1m3_fa_table.FATABLE_ZFA,
        )
        self.assertEqual(a.fx, 12)
        self.assertEqual(a.fy, 200)
        self.assertEqual(a.fz, 3 * 156)
        self.assertEqual(a.forceMagnitude, np.sqrt(12**2 + 200**2 + (3 * 156) ** 2))

        self.assertEqual(a.mx, 1099.7485905139997)
        self.assertEqual(a.my, 430.0953056310003)
        self.assertEqual(a.mz, -212.0001997679999)

    def test_hardpoints(self) -> None:
        fam = self.calculator.hardpoint_forces_and_moments(
            [100, -100, 200, -200, 300, -300]
        )
        np.testing.assert_array_equal(fam, [-600, -600, 100, -100, -200, -100])

    def test_distribute_forces(self) -> None:
        forces = self.calculator.forces_and_moments_forces(
            [-100, 200, -300, 400, -500, 600]
        )
        np.testing.assert_array_equal(
            forces.xForces, [0, 300] + [0] * (m1m3_fa_table.FATABLE_XFA - 2)
        )

        forces = self.calculator.forces_and_moments_forces(
            [-600, -600, 100, -100, -200, -100]
        )
        np.testing.assert_array_equal(
            forces.xForces, [0, -700] + [0] * (m1m3_fa_table.FATABLE_XFA - 2)
        )

    def test_hardpoint_forces(self) -> None:
        forces = self.calculator.hardpoint_forces([100, -100, 200, -200, 300, -300])
        np.testing.assert_array_equal(
            forces.xForces, [0, -700] + [0] * (m1m3_fa_table.FATABLE_XFA - 2)
        )

    def test_acceleration(self) -> None:
        acceleration = self.calculator.acceleration([0, 0, 0])

        np.testing.assert_array_equal(
            acceleration.xForces, [0] * m1m3_fa_table.FATABLE_XFA
        )
        np.testing.assert_array_equal(
            acceleration.yForces, [0] * m1m3_fa_table.FATABLE_YFA
        )
        np.testing.assert_array_equal(
            acceleration.zForces, [0] * m1m3_fa_table.FATABLE_ZFA
        )

        acceleration = self.calculator.acceleration([1, 0, 0])

        np.testing.assert_array_equal(
            acceleration.xForces, [0, 1] + [0] * (m1m3_fa_table.FATABLE_XFA - 3) + [2]
        )
        np.testing.assert_array_equal(
            acceleration.yForces, [0] * m1m3_fa_table.FATABLE_YFA
        )
        np.testing.assert_array_equal(
            acceleration.zForces, [0] * m1m3_fa_table.FATABLE_ZFA
        )

    def test_velocity(self) -> None:
        velocity = self.calculator.velocity([0, 0, 0])

        np.testing.assert_array_equal(velocity.xForces, [0] * m1m3_fa_table.FATABLE_XFA)
        np.testing.assert_array_equal(velocity.yForces, [0] * m1m3_fa_table.FATABLE_YFA)
        np.testing.assert_array_equal(velocity.zForces, [0] * m1m3_fa_table.FATABLE_ZFA)

        velocity = self.calculator.velocity([1, 2, 3])

        np.testing.assert_array_equal(
            velocity.xForces, [0, 88] + [0] * (m1m3_fa_table.FATABLE_XFA - 3) + [18]
        )
        np.testing.assert_array_equal(
            velocity.yForces, [18] + [0] * (m1m3_fa_table.FATABLE_YFA - 2) + [15]
        )
        np.testing.assert_array_equal(
            velocity.zForces,
            [0, 12] + [0] * (m1m3_fa_table.FATABLE_ZFA - 8) + [9, 0, 0, 0, 0, 21],
        )

    def test_addition(self) -> None:
        velocity = self.calculator.velocity([1, 2, 3])

        acceleration = self.calculator.acceleration([1, 0, 0])

        forces = velocity + acceleration

        np.testing.assert_array_equal(
            forces.xForces, [0, 89] + [0] * (m1m3_fa_table.FATABLE_XFA - 3) + [20]
        )
        np.testing.assert_array_equal(
            forces.yForces, [18] + [0] * (m1m3_fa_table.FATABLE_YFA - 2) + [15]
        )
        np.testing.assert_array_equal(
            forces.zForces,
            [0, 12] + [0] * (m1m3_fa_table.FATABLE_ZFA - 8) + [9, 0, 0, 0, 0, 21],
        )


if __name__ == "__main__":
    unittest.main()
