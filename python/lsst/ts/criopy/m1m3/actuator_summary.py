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
# version#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

import enum
import pandas as pd
from astropy.time import Time
from lsst.ts.xml.tables.m1m3 import FATable, force_actuator_from_id
from lsst_efd_client import EfdClient
from lsst.summit.utils.tmaUtils import TMAEvent


class ActuatorSummary:

    """Returns several different summaries of the force actuator
    following errors

    Parameters
    ----------
    client : lsst_efd_client.efd_helper.EfdClient object, optional
        This is used to query the EFD. Default to summit_efd client.
    """

    def __init__(self, client: EfdClient | None = None):
        super().__init__()
        self.client = EfdClient("summit_efd") if client is None else client

    def find_times(
        self,
        event: TMAEvent | None = None,
        start: Time | None = None,
        end: Time | None = None
    ) -> None:
        """Find query times
        Must specify either  TMAEvent or start and end times
        event : TMAEvent, optional
            TMAEvent to be used to find the start and end times
        start: 'Time', optional
            Astropy Time of search start.
        end: Time, optional
            Astropy Time of search end.
        returns: None
        """
        if event:
            self.start = event.begin; self.end = event.end;
        elif start and end:
            self.start = start; self.end = end;
        else:
            raise RuntimeError("Must specify either TMAEvent, or start and end")
        return

    async def following_error_by_id(
        self,
        id: int,
        event: TMAEvent | None = None,
        start: Time | None = None,
        end: Time | None = None,
        output: str | None = 'Mean',
        describe: bool | None = False,
    ) -> enum.auto():
        """Find following error for a single FA
        id: int, Force actuator ID - runs up to 443
        event : TMAEvent, optional
            TMAEvent to be used to find the start and end times
        start: 'Time', optional
            Astropy Time of search start.
        end: Time, optional
            Astropy Time of search end.
        output: What to output.  options are 'Mean' and 'MinMax'.
        describe: Whether to print out a summary of statistics
        returns: For output = 'MinMax, nested list of floats, 
            one for the primary bump and one for
            the secondary bump [[max, min], [max, min]].
            For output = 'Mean', a single list [abs mean, abs mean].
        """
        self.find_times(event, start, end)
        fa = force_actuator_from_id(id)
        primary_follow = f"primaryCylinderFollowingError{fa.index}"
        if fa.actuator_type.name == 'DAA':
            secondary_follow = f"secondaryCylinderFollowingError{fa.s_index}"
        else:
            secondary_follow = None

        errors = await self.client.select_time_series("lsst.sal.MTM1M3.forceActuatorData", \
                                                 [primary_follow, secondary_follow], self.start, self.end)
        if describe:
            print(errors.abs().describe())
        primaryMean = errors[primary_follow].abs().mean()
        primaryMin = errors[primary_follow].min()
        primaryMax = errors[primary_follow].max()
        if secondary_follow:
            secondaryMean = errors[secondary_follow].abs().mean()
            secondaryMin = errors[secondary_follow].min()
            secondaryMax = errors[secondary_follow].max()
        else:
            secondaryMean = None
            secondaryMin = None
            secondaryMax = None
        if output == 'Mean':
            return [primaryMean, secondaryMean]
        elif output == 'MinMax':
            return [[primaryMin, primaryMax], [secondaryMin, secondaryMax]]


    async def following_errors(
        self,
        event: TMAEvent | None = None,
        start: Time | None = None,
        end: Time | None = None,
        output: str | None = 'Mean',
        describe: bool | None = False,
    ) -> enum.auto():
        """Find following errors for all FAs
        event : TMAEvent, optional
            TMAEvent to be used to find the start and end times
        start: 'Time', optional
            Astropy Time of search start.
        end: Time, optional
            Astropy Time of search end.
        output: What to output.  options are 'Mean' and 'MinMax'.
        describe: Whether to print out a summary of statistics
        returns: For output = 'MinMax, nested list of floats, 
            one for the primary bump and one for
            the secondary bump [[max, min], [max, min]].
            For output = 'Mean', a single list [abs mean, abs mean].
        """
        self.find_times(event, start, end)

        primary_follows = []
        secondary_follows = []
        for index in range(len(FATable)):
            id = FATable[index].actuator_id
            fa = force_actuator_from_id(id)
            primary_follow = f"primaryCylinderFollowingError{fa.index}"
            primary_follows.append(primary_follow)
            if fa.actuator_type.name == 'DAA':
                secondary_follow = f"secondaryCylinderFollowingError{fa.s_index}"
                secondary_follows.append(secondary_follow)
        follows = primary_follows + secondary_follows
        errors = await self.client.select_time_series("lsst.sal.MTM1M3.forceActuatorData", \
                                                      follows, self.start, self.end)
        if output == 'Mean':
            primary_errors = pd.DataFrame(errors[primary_follows].abs().values.reshape(-1))
            secondary_errors = pd.DataFrame(errors[secondary_follows].abs().values.reshape(-1))

            if describe:
                print("Primary")
                print(primary_errors.describe())
                print("Secondary")
                print(secondary_errors.describe())
            primaryMean = primary_errors.mean().to_list()[0]
            secondaryMean = secondary_errors.mean().to_list()[0]
            return [primaryMean, secondaryMean]

        elif output == 'MinMax':
            primary_errors = pd.DataFrame(errors[primary_follows].values.reshape(-1))
            secondary_errors = pd.DataFrame(errors[secondary_follows].values.reshape(-1))
            if describe:
                print("Primary")
                print(primary_errors.describe())
                print("Secondary")
                print(secondary_errors.describe())
            primaryMin = primary_errors.min().to_list()[0]
            primaryMax = primary_errors.max().to_list()[0]
            secondaryMin = secondary_errors.min().to_list()[0]
            secondaryMax = secondary_errors.max().to_list()[0]
            return [[primaryMin, primaryMax], [secondaryMin, secondaryMax]]

