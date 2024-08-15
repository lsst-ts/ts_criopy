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

import pandas as pd
from astropy.time import Time
from lsst.ts.xml.tables.m1m3 import FATable, ForceActuatorData
from lsst_efd_client import EfdClient


class ForceActuatorForces:
    """Returns several different summaries of the force actuator
    following errors.

    Parameters
    ----------
    client : lsst_efd_client.efd_helper.EfdClient object, optional
        This is used to query the EFD. Default to summit_efd client.
    start: 'Time', optional
        Astropy Time of search start.
    end: Time, optional
        Astropy Time of search end.
    """

    def __init__(
        self,
        start: Time = None,
        end: Time = None,
        client: EfdClient | None = None,
    ):
        self.start = start
        self.end = end

        self.client = EfdClient("summit_efd") if client is None else client

    async def actuator_following_error(
        self, actuator: ForceActuatorData
    ) -> pd.DataFrame:
        """Find following error for a single FA.

        Parameters
        ----------

        actuator: ForceActuatorData
            Force actuator entry.

        Returns
        -------
        following_errors: pd.DataFrame
            Dataframe with following errors for the actuator.
        """
        fields = [f"primaryCylinderFollowingError{actuator.index}"]
        out = ["primary"]
        if actuator.s_index is not None:
            fields.append(f"secondaryCylinderFollowingError{actuator.s_index}")
            out.append("secondary")

        following_errors = await self.client.select_time_series(
            "lsst.sal.MTM1M3.forceActuatorData", fields, self.start, self.end
        )
        return following_errors.rename(columns=dict(zip(fields, out)))

    async def following_errors(self) -> pd.DataFrame:
        """Find following errors for all FAs

        Returns
        -------
        following_errors: pd.DataFrame
        """
        fields = [f"primaryCylinderFollowingError{fa.index}" for fa in FATable] + [
            f"primaryCylinderFollowingError{fa.s_index}"
            for fa in FATable
            if fa.s_index is not None
        ]

        return await self.client.select_time_series(
            "lsst.sal.MTM1M3.forceActuatorData", fields, self.start, self.end
        )

    async def actuator_forces(self, actuator: ForceActuatorData) -> pd.DataFrame:
        fields = [f"zForce{actuator.z_index}"]

        if actuator.x_index is not None:
            fields.append(f"xForce{actuator.x_index}")

        if actuator.y_index is not None:
            fields.append(f"yForce{actuator.y_index}")

        return await self.client.select_time_series(
            "lsst.sal.MTM1M3.forceActuatorData", fields, self.start, self.end
        )

    async def forces(self) -> pd.DataFrame:
        fields = (
            [f"xForce{fa.x_index}" for fa in FATable if fa.x_index is not None]
            + [f"xForce{fa.y_index}" for fa in FATable if fa.y_index is not None]
            + [f"zForce{fa.z_index}" for fa in FATable]
        )

        return await self.client.select_time_series(
            "lsst.sal.MTM1M3.forceActuatorData", fields, self.start, self.end
        )

    async def cylinder_forces(self) -> pd.DataFrame:
        fields = [f"primaryCylinderForce{fa.index}" for fa in FATable] + [
            f"secondaryCylinderForce{fa.s_index}"
            for fa in FATable
            if fa.s_index is not None
        ]

        return await self.client.select_time_series(
            "lsst.sal.MTM1M3.forceActuatorData", fields, self.start, self.end
        )
