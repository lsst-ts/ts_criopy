# This file is part of ts_cRIOpy.
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

import argparse
import unittest

from lsst.ts.cRIOpy import parseDuration


class ParseDurationTestCase(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(parseDuration("1"), 1)
        self.assertEqual(parseDuration("1 "), 1)
        self.assertEqual(parseDuration(" 1"), 1)
        self.assertEqual(parseDuration(" 1 D "), 86400)
        self.assertEqual(parseDuration("2h3m6s"), 2 * 3600 + 3 * 60 + 6)
        self.assertEqual(
            parseDuration(" 10h 67   m 12345s"), 10 * 3600 + 67 * 60 + 12345
        )
        self.assertEqual(
            parseDuration(" 10h 67   m 12345"), 10 * 3600 + 67 * 60 + 12345
        )

    def test_failures(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            parseDuration("1d")
            parseDuration("1Dd")
            parseDuration("239  Dd")
            parseDuration("2m@")
            parseDuration(" 2m  3 S")


if __name__ == "__main__":
    unittest.main()
