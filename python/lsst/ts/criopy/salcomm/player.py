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
import logging
import time

from astropy.time import Time, TimeDelta
from lsst_efd_client import EfdClient
from PySide6.QtCore import QObject, Signal

from .efd_cache import EfdCache, EfdTopicCache
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

    downloadStarted = Signal()
    downloadFinished = Signal()

    def __init__(self, sal: MetaSAL, efd: str):
        super().__init__()
        self.sal = sal

        logging.info("Initializing the EFD connection client.")
        self.cache = EfdCache(sal, EfdClient(efd))

    async def replay(self, timepoint: Time, duration: TimeDelta) -> None:
        await self.cache.cleanup()

        start_time = time.monotonic()
        downloads = 0

        reported_ranges: list[tuple[Time, Time]] = []

        async with asyncio.TaskGroup() as tg:
            for request in self.cache.new_requests(timepoint, duration):
                tg.create_task(self.cache.load(request))
                if downloads == 0:
                    self.downloadStarted.emit()
                if (request.start, request.end) not in reported_ranges:
                    logging.info(
                        "Loading %s - %s.", request.start.isot, request.end.isot
                    )
                    reported_ranges.append((request.start, request.end))

                downloads += 1

        if downloads > 0:
            duration = time.monotonic() - start_time
            logging.info(
                "Downloaded %d topics in %.2f seconds (%.2f topics/second).",
                downloads,
                duration,
                downloads / duration,
            )
            self.downloadFinished.emit()

        # First, the cached topics must be updated to contain actual new data.
        for topic, cache in self.cache.telemetry.items():
            cache.set_current_time(timepoint)

        for topic, cache in self.cache.events.items():
            cache.set_current_time(timepoint)

        # When data are update, signals are distributed -

        def send_cache(topic: str, cache: EfdTopicCache) -> None:
            if cache is None or cache.empty:
                return
            assert cache.data is not None

            send = cache.get()
            if send is not None and send._changed:
                getattr(self.sal, topic).emit(send)

        for topic, cache in self.cache.telemetry.items():
            send_cache(topic, cache)

        for topic, cache in self.cache.events.items():
            send_cache(topic, cache)
