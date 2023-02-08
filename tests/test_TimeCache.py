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

        self.assertEqual(cache["timestamp"], [1])
        self.assertEqual(cache["df"], [0.5])
        self.assertEqual(cache["di"], [2])

        cache.clear()
        self.assertEqual(len(cache), 0)
        self.assertIsNone(cache.startTime())
        self.assertIsNone(cache.endTime())

    def test_append(self):
        cache = TimeCache(5, [("timestamp", "i4"), ("data1", "i4"), ("data2", "i4")])

        self.assertEqual(cache.columns(), ("timestamp", "data1", "data2"))

        for i in range(103):
            cache.append((i, i * 2, i**2))

        self.assertEqual(len(cache), 5)
        for i in range(5):
            testValue = i + 98
            self.assertEqual(cache["timestamp"][i], testValue)
            self.assertEqual(cache["data1"][i], testValue * 2)
            self.assertEqual(cache["data2"][i], testValue**2)

    def test_resize(self):
        cache = TimeCache(5, [("timestamp", "i4"), ("data1", "i4"), ("data2", "i4")])

        self.assertEqual(cache.columns(), ("timestamp", "data1", "data2"))

        for i in range(1025):
            cache.append((i**2, i * 2, i * 3))

        self.assertEqual(len(cache), 5)
        for i in range(5):
            testValue = i + 1020
            self.assertEqual(cache["timestamp"][i], testValue**2)
            self.assertEqual(cache["data1"][i], testValue * 2)
            self.assertEqual(cache["data2"][i], testValue * 3)

        cache.resize(1000)

        for i in range(995):
            self.assertEqual(len(cache), 5 + i)
            cache.append((i * 4, i**2, i * 5))

        self.assertEqual(len(cache), 1000)
        for i in range(5):
            testvalue = i + 1020
            self.assertEqual(cache["timestamp"][i], testvalue**2)
            self.assertEqual(cache["data1"][i], testvalue * 2)
            self.assertEqual(cache["data2"][i], testvalue * 3)

        for i in range(5, 1000):
            testvalue = i - 5
            self.assertEqual(cache["timestamp"][i], testvalue * 4)
            self.assertEqual(cache["data1"][i], testvalue**2)
            self.assertEqual(cache["data2"][i], testvalue * 5)

        for i in range(14568):
            self.assertEqual(len(cache), 1000)
            cache.append((i, i * 2, i * 3))

        for i in range(1000):
            testvalue = i + 13568
            self.assertEqual(cache["timestamp"][i], testvalue)
            self.assertEqual(cache["data1"][i], testvalue * 2)
            self.assertEqual(cache["data2"][i], testvalue * 3)

        cache.resize(25)
        for i in range(25):
            testvalue = i + 13568 + 975
            self.assertEqual(cache["timestamp"][i], testvalue)
            self.assertEqual(cache["data1"][i], testvalue * 2)
            self.assertEqual(cache["data2"][i], testvalue * 3)

        for i in range(14568):
            self.assertEqual(len(cache), 25)
            cache.append((i * 3, i**2, i * 6))

        for i in range(25):
            testvalue = i + 14543
            self.assertEqual(cache["timestamp"][i], testvalue * 3)
            self.assertEqual(cache["data1"][i], testvalue**2)
            self.assertEqual(cache["data2"][i], testvalue * 6)

    def test_timestampIndex(self):
        cache = TimeCache(10, [("timestamp", "f8"), ("data1", "i4"), ("data2", "i4")])

        timestamp = 10

        def addValues(vals):
            nonlocal cache, timestamp
            for i in range(vals):
                cache.append((timestamp, timestamp * 2, timestamp * 3))
                timestamp += 0.1

        addValues(10)
        self.assertEqual(len(cache), 10)
        self.assertEqual(cache.filled, False)

        self.assertEqual(cache.timestampIndex(9), 0)
        self.assertEqual(cache.timestampIndex(10), 0)
        self.assertEqual(cache.timestampIndex(10.1), 1)
        self.assertEqual(cache.timestampIndex(10.2), 2)
        self.assertEqual(cache.timestampIndex(10.3), 3)
        self.assertEqual(cache.timestampIndex(10.4), 4)
        self.assertEqual(cache.timestampIndex(10.5), 5)
        self.assertEqual(cache.timestampIndex(10.6), 6)
        self.assertEqual(cache.timestampIndex(10.7), 7)
        self.assertEqual(cache.timestampIndex(10.8), 8)
        self.assertEqual(cache.timestampIndex(10.9), 9)
        self.assertEqual(cache.timestampIndex(10.95), None)
        self.assertEqual(cache.timestampIndex(11.0), None)

        addValues(1)
        self.assertEqual(len(cache), 10)
        self.assertEqual(cache.filled, True)

        self.assertEqual(cache.timestampIndex(10), 0)
        self.assertEqual(cache.timestampIndex(10.1), 0)
        self.assertEqual(cache.timestampIndex(10.2), 1)
        self.assertEqual(cache.timestampIndex(10.3), 2)
        self.assertEqual(cache.timestampIndex(10.4), 3)
        self.assertEqual(cache.timestampIndex(10.5), 4)
        self.assertEqual(cache.timestampIndex(10.6), 5)
        self.assertEqual(cache.timestampIndex(10.7), 6)
        self.assertEqual(cache.timestampIndex(10.8), 7)
        self.assertEqual(cache.timestampIndex(10.85), 8)
        self.assertEqual(cache.timestampIndex(10.9), 8)
        self.assertEqual(cache.timestampIndex(10.95), 9)
        self.assertEqual(cache.timestampIndex(11.0), 9)
        self.assertEqual(cache.timestampIndex(11.1), None)


if __name__ == "__main__":
    unittest.main()
