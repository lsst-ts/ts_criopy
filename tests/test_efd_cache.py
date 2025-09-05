# This file is part of criopy package.
#
# Developed for the LSST Telescope and Site Systems.
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
import sys
import unittest

import vcr
from astropy.time import Time, TimeDelta
from lsst.ts.criopy.salcomm import EfdCache, create
from lsst.ts.salobj import set_test_topic_subname

CASSETTE_DIR = os.path.join(os.path.dirname(__file__), "cassettes")

myvcr = vcr.VCR(
    cassette_library_dir=CASSETTE_DIR,
    record_mode=os.getenv("RECORD_MODE", "none"),
    match_on=["method", "scheme", "host", "port", "path", "query", "body"],
)


class EfdCacheTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        set_test_topic_subname()
        self.sal = create("MTM1M3TS")

    async def test_load(self) -> None:
        with myvcr.use_cassette("test_load.yaml"):
            cache = EfdCache(self.sal, "usdf_efd")

            timepoint = Time("2025-05-19T23:40:00", scale="utc")
            interval = TimeDelta(240, format="sec")

            # expected interval start and end
            i_start = timepoint - TimeDelta(0.05, format="sec")
            i_end = timepoint + interval

            topics: list[str] = []

            for request in cache.new_requests(timepoint, interval):
                topics.append(request.topic)
                assert request.start == i_start
                assert request.end == i_end

                await cache.load(request)

                if request.topic == "thermalData":
                    assert len(cache.tel_thermalData.data) == 479
                    assert request.cache.data.index[0] == Time(
                        "2025-05-19T23:40:00.177549", scale="utc"
                    )
                    assert request.cache.data.index[-1] == Time(
                        "2025-05-19T23:43:59.7599", scale="utc"
                    )

            assert len(topics) == 24


if __name__ == "__main__":
    if "RECORD_MODE" not in os.environ:
        print(
            f"To generate new cassettes with pre-downloaded data use: RECORD_MODE=all python {sys.argv[0]}"
        )
    unittest.main()
