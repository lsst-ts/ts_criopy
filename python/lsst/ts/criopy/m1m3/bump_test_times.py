# This file is part of M1M3 GUI.
#
# Developed for the LSST Telescope and Site Systems.  This product includes
# software developed by the LSST Project (https://www.lsst.org).  See the
# COPYRIGHT file at the top-level directory of this distribution for details of
# code ownership.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

import pandas as pd
from astropy.time import Time, TimeDelta
from lsst.ts.xml.tables.m1m3 import FAType, force_actuator_from_id
from lsst_efd_client import EfdClient


class BumpTestTimes:

    """Returns a set of times for bump tests given the actuator ID and
    an input timespan

    Parameters
    ----------
    client : lsst_efd_client.efd_helper.EfdClient object
        This is used to query the EFD
    """

    def __init__(self, client: EfdClient = EfdClient("summit_efd")):
        super().__init__()
        self.client = client

    async def find_times(
        self,
        actuator_id: int,
        start: Time = (Time.now() - TimeDelta(7, format="jd")),
        end: Time = Time.now(),
    ) -> tuple[list[tuple[float, float]], list[tuple[float | None, float | None]]]:
        """Find bump test query times
        actuator_id : `int`
            Force Actuator identification number. Starting with 101, the first
            number identified segment (1-4). The value ranges up to 443.

        start: 'Time'
            Astropy Time of search start.

        end: Time
            Astropy Time of search end.

        returns: Two nested list of ints, one for the primary bump and one for
            the secondary bump [start,end], [start, end]...]
            These times will be in unix_tai format
        """
        fa = force_actuator_from_id(actuator_id)
        manyBumps = await self.client.select_time_series(
            "lsst.sal.MTM1M3.logevent_forceActuatorBumpTestStatus", "*", start, end
        )

        theseBumps = manyBumps[manyBumps["actuatorId"] == actuator_id]
        # Find the test names
        primaryBump = f"primaryTest{fa.index}"
        if fa.actuator_type == FAType.DAA:
            secondaryBump = f"secondaryTest{fa.s_index}"
        else:
            secondaryBump = None
        # Now find the separate tests
        times = theseBumps["timestamp"].values
        startTimes = []
        endTimes = []
        for i, time in enumerate(times):
            if i == 0:
                startTimes.append(time)
                continue
            if (time - times[i - 1]) > 60.0:
                startTimes.append(time)
                endTimes.append(times[i - 1])
        endTimes.append(times[-1])
        # Now use these to find the bump test start and end times
        primaryTimes: list[tuple[float, float]] = []
        secondaryTimes: list[tuple[float | None, float | None]] = []
        for startTime, endTime in zip(startTimes, endTimes):
            thisBump = theseBumps[
                (theseBumps["timestamp"] >= startTime)
                & (theseBumps["timestamp"] <= endTime)
            ]
            try:
                plotStart = (
                    thisBump[thisBump[primaryBump] == 2]["timestamp"].values[0] - 1.0
                )
                plotEnd = plotStart + 14.0
                primaryTimes.append((plotStart, plotEnd))
                if secondaryBump is not None:
                    plotStart = (
                        thisBump[thisBump[secondaryBump] == 2]["timestamp"].values[0]
                        - 1.0
                    )
                    plotEnd = plotStart + 14.0
                    secondaryTimes.append((plotStart, plotEnd))
                else:
                    secondaryTimes.append((None, None))
            except IndexError:
                continue
        return primaryTimes, secondaryTimes
