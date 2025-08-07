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

__all__ = ["Player"]

import numpy as np
import pandas as pd
from astropy.time import Time, TimeDelta
from lsst_efd_client import EfdClient
from PySide6.QtCore import QObject

from .meta_sal import MetaSAL


class Player(QObject):
    """Queries EFD for telemetry and events, build up a cache and replay the
    events."""

    def __init__(self, sal: MetaSAL, efd_client: EfdClient):
        super().__init__()
        self.sal = sal
        self.efd_client = efd_client

        self.cache: dict[str, pd.DataFrame] = {}

    async def replay(self, timepoint: Time) -> None:
        time64 = pd.to_datetime(timepoint.isot).value
        for tel in self.sal.telemetry():
            if tel not in self.cache.keys():
                start = timepoint + TimeDelta(10, format="sec")
                end = timepoint + TimeDelta(20, format="sec")
                self.cache[tel] = await self.efd_client.select_time_series(
                    "lsst.sal.MTM1M3." + tel, "*", start, end
                )
            data = self.cache[tel]
            print(data.index)
            row = data[data.index <= time64][0]
            send = {}
            for column in row.columns.values:
                send[column] = row[column]
            getattr(self.sal, tel).emit(send)
