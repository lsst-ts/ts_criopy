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

from astropy.time import Time, TimeDelta
from lsst.ts.xml.tables.m1m3 import FAType, force_actuator_from_id
from lsst_efd_client import EfdClient


class BumpTestTimes:

    """Returns a set of times for bump tests given the actuator ID and
    an input timespan

    Parameters
    ----------
    client : lsst_efd_client.efd_helper.EfdClient object, optional
        This is used to query the EFD. Default to summit_efd client.
    """

    def __init__(self, client: EfdClient | None = None):
        super().__init__()
        self.client = EfdClient("summit_efd") if client is None else client

    async def find_times(
        self,
        actuator_id: int,
        start: Time = (Time.now() - TimeDelta(7, format="jd")),
        end: Time = Time.now(),
    ) -> tuple[list[tuple[Time, Time]], list[tuple[Time, Time]]]:
        """Find bump test query times
        actuator_id : `int`
            Force Actuator identification number. Starting with 101, the first
            number identified segment (1-4). The value ranges up to 443.

        start: 'Time', optional
            Astropy Time of search start. Defaults to week ago.

        end: Time
            Astropy Time of search end. Defaults to current time.

        returns: Two nested list of Time, one for the primary bump and one for
            the secondary bump [start,end], [start, end]...].
        """
        fa = force_actuator_from_id(actuator_id)

        # Find the test names
        primary_bump = f"primaryTest{fa.index}"
        query_fields = "time, actuatorId, " + primary_bump
        if fa.actuator_type == FAType.DAA:
            secondary_bump = f"secondaryTest{fa.s_index}"
            query_fields += ", " + secondary_bump
        else:
            secondary_bump = None

        bumps = await self.client.influx_client.query(
            f"SELECT {query_fields} "
            'FROM "efd"."autogen"."lsst.sal.MTM1M3.logevent_forceActuatorBumpTestStatus" '
            f"WHERE time >= '{start.isot}+00:00' AND time <= '{end.isot}+00:00' "
            f"AND actuatorId = {actuator_id}"
        )

        print(bumps)

        # Now find the separate tests
        times = bumps.index
        start_times = []
        end_times = []
        for i, time in enumerate(times):
            if i == 0:
                start_times.append(time)
                continue
            if (time - times[i - 1]) > TimeDelta(60.0, format="sec"):
                start_times.append(time)
                end_times.append(times[i - 1])
        end_times.append(times[-1])
        # Now use these to find the bump test start and end times
        primary_times: list[tuple[Time, Time]] = []
        secondary_times: list[tuple[Time, Time]] = []
        for start_time, end_time in zip(start_times, end_times):
            this_bump = bumps[(bumps.index >= start_time) & (bumps.index <= end_time)]
            try:
                plot_start = Time(
                    this_bump[this_bump[primary_bump] == 2].index[0]
                ) - TimeDelta(1, format="sec")
                plot_end = plot_start + TimeDelta(14, format="sec")
                primary_times.append((plot_start, plot_end))
                if secondary_bump is not None:
                    plot_start = Time(
                        this_bump[this_bump[secondary_bump] == 2].index[0]
                    ) - TimeDelta(1, format="sec")
                    plot_end = plot_start + TimeDelta(14, format="sec")
                    secondary_times.append((plot_start, plot_end))
            except IndexError:
                continue
        return primary_times, secondary_times
