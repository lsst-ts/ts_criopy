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

        start: 'Time', optional
            Astropy Time of search start. Defaults to week ago.

        end: Time
            Astropy Time of search end. Defaults to current time.

        returns: Two nested list of ints, one for the primary bump and one for
            the secondary bump [start,end], [start, end]...]
            These times will be in unix_tai format
        """
        fa = force_actuator_from_id(actuator_id)
        many_bumps = await self.client.select_time_series(
            "lsst.sal.MTM1M3.logevent_forceActuatorBumpTestStatus", "*", start, end
        )

        these_bumps = many_bumps[many_bumps["actuatorId"] == actuator_id]
        # Find the test names
        primary_bump = f"primaryTest{fa.index}"
        if fa.actuator_type == FAType.DAA:
            secondary_bump = f"secondaryTest{fa.s_index}"
        else:
            secondary_bump = None
        # Now find the separate tests
        times = these_bumps["timestamp"].values
        start_times = []
        end_times = []
        for i, time in enumerate(times):
            if i == 0:
                start_times.append(time)
                continue
            if (time - times[i - 1]) > 60.0:
                start_times.append(time)
                end_times.append(times[i - 1])
        end_times.append(times[-1])
        # Now use these to find the bump test start and end times
        primary_times: list[tuple[float, float]] = []
        secondary_times: list[tuple[float | None, float | None]] = []
        for start_time, end_time in zip(start_times, end_times):
            this_bump = these_bumps[
                (these_bumps["timestamp"] >= start_time)
                & (these_bumps["timestamp"] <= end_time)
            ]
            try:
                plot_start = (
                    this_bump[this_bump[primary_bump] == 2]["timestamp"].values[0] - 1.0
                )
                plot_end = plot_start + 14.0
                primary_times.append((plot_start, plot_end))
                if secondary_bump is not None:
                    plot_start = (
                        this_bump[this_bump[secondary_bump] == 2]["timestamp"].values[0]
                        - 1.0
                    )
                    plot_end = plot_start + 14.0
                    secondary_times.append((plot_start, plot_end))
                else:
                    secondary_times.append((None, None))
            except IndexError:
                continue
        return primary_times, secondary_times
