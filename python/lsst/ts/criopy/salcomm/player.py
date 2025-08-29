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
from PySide6.QtCore import QObject, Signal

from .efd_cache import EfdCache, EfdCacheRequest, EfdTopicCache
from .meta_sal import MetaSAL


class Player(QObject):
    """
    Queries EFD for telemetry and events, build up a cache and replay the
    events.

    Signals
    -------
    downloadStarted
        Emmited when data download starts.
    downloadFinished
        Emmited when data download ends.

    Parameters
    ----------
    sal : `MetaSAL`
        SAL objects to replay. The topics in this fields are used to query EFD.
    num_tasks: `int`, optional
        Number of allowed parallel tasks. Defaults to 10.
    """

    downloadStarted = Signal()
    downloadFinished = Signal()

    def __init__(self, sal: MetaSAL, num_tasks: int = 10):
        super().__init__()
        self.sal = sal

        self.cache: EfdCache | None = None

        self.worker_queue: asyncio.Queue[tuple[EfdCacheRequest, Time]] = asyncio.Queue()
        self.workers = [
            asyncio.create_task(self.worker(f"Worker-{i}")) for i in range(num_tasks)
        ]

    async def worker(self, name: str) -> None:
        while True:
            request, timepoint = await self.worker_queue.get()
            assert self.cache is not None
            await self.cache.load(request)
            request.cache.set_current_time(timepoint)
            self.send_cache(request.topic, request.cache)
            self.worker_queue.task_done()

    def send_cache(self, topic: str, cache: EfdTopicCache) -> None:
        if cache is None or cache.empty:
            return
        assert cache.data is not None

        send = cache.get()
        if send is not None and send._changed:
            getattr(self.sal, topic).emit(send)

    async def replay(self, efd: str, timepoint: Time, duration: TimeDelta) -> None:
        """
        Load data into cache. Starts multiple tasks to load data to speed up
        the process.

        Parameters
        ----------
        efd : `str`
            EFD name.
        timepoint : `Time`
            Requested (exact) time. After replay ends, the call guarantees data
            (telemetry and events) for this time will be loaded in the cache.
        duration : `TimeDelta`
            Interval length. This is the prefered length of the cache around
            timepoint.
        """
        if self.cache is None or self.cache.efd != efd:
            logging.info("Initializing the EFD connection client to %s.", efd)
            self.cache = EfdCache(self.sal, efd)

        await self.cache.cleanup()

        start_time = time.monotonic()
        downloads = 0

        reported_ranges: list[tuple[Time, Time]] = []

        for request in self.cache.new_requests(timepoint, duration):
            await self.worker_queue.put((request, timepoint))
            if downloads == 0:
                self.downloadStarted.emit()
            if (request.start, request.end) not in reported_ranges:
                logging.info("Loading %s - %s.", request.start.isot, request.end.isot)
                reported_ranges.append((request.start, request.end))

            downloads += 1

        await self.worker_queue.join()

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

        # When data are update, signals are distributed

        for topic, cache in self.cache.telemetry.items():
            self.send_cache(topic, cache)

        for topic, cache in self.cache.events.items():
            self.send_cache(topic, cache)
