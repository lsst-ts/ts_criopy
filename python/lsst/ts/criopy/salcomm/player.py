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

import asyncio

import pandas as pd
from astropy.time import Time, TimeDelta
from lsst_efd_client import EfdClient
from PySide6.QtCore import QObject

from .efd_cache import EfdCache
from .meta_sal import MetaSAL


class Player(QObject):
    """Queries EFD for telemetry and events, build up a cache and replay the
    events.

    Parameters
    ----------
    sal : MetaSAL
        SAL objects to replay. The topics in this fields are used to query EFD.
    efd_client : EfdClient

    """

    def __init__(self, sal: MetaSAL, efd_client: EfdClient):
        super().__init__()
        self.sal = sal

        self.cache = EfdCache(sal, efd_client)
        self.sem = asyncio.Semaphore(10)

    async def replay(self, timepoint: Time) -> None:
        await self.cache.cleanup()
        for request in self.cache.new_requests(timepoint, TimeDelta(60, format="sec")):
            async with self.sem:
                await self.cache.load(request)

        timestr = timepoint.iso + "+00:00"

        class RowClass:
            def __init__(self, row: pd.Series):
                last = None
                last_len = 0
                for c in row.columns.values:
                    v = row[c].item()
                    if (
                        last is not None
                        and c.startswith(last)
                        and c[last_len].isnumeric()
                    ):
                        getattr(self, last).append(v)
                    elif c[-1] == "0":
                        last = c[:-1]
                        last_len = len(last)
                        setattr(self, last, [v])
                    else:
                        last = None
                        setattr(self, c, v)

        for topic in self.cache.telemetry.keys():
            cache = self.cache[topic]
            if cache is None or cache.empty:
                continue
            assert cache.data is not None

            row = cache.data.loc[:timestr].tail(n=1)  # type:ignore[misc]
            send = RowClass(row)
            getattr(self.sal, topic).emit(send)
