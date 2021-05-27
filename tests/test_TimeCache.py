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

import unittest

from lsst.ts.cRIOpy import TimeCache


class TimeCacheTestCase(unittest.TestCase):
    def test_clear(self):
        cache = TimeCache(5, [("timestamp", "f8"), ("df", "f8"), ("di", "i4")])

        self.assertEqual(cache.columns(), ("timestamp", "df", "di"))

        self.assertEqual(len(cache), 0)
        self.assertIsNone(cache.startTime())
        self.assertIsNone(cache.endTime())

        cache.append((1, 0.5, 2))
        self.assertEqual(len(cache), 1)
        self.assertEqual(cache.startTime(), 1)
        self.assertEqual(cache.endTime(), 1)

        self.assertEqual(cache['timestamp'], [1])
        self.assertEqual(cache['df'], [0.5])
        self.assertEqual(cache['di'], [2])

        cache.clear()
        self.assertEqual(len(cache), 0)
        self.assertIsNone(cache.startTime())
        self.assertIsNone(cache.endTime())


if __name__ == "__main__":
    unittest.main()
