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
    requestStarted(request, worker)
        Emmited when request processing is started.
    requestTerminated(request, worker)
        Emmited when request processign is terminated (stopped).
    requestFinished(request, worker)
        Emmited when request processing is finished.

    Parameters
    ----------
    sal : `MetaSAL`
        SAL objects to replay. The topics in this fields are used to query EFD.
    num_tasks: `int`, optional
        Number of allowed parallel tasks. Defaults to 10.
    """

    downloadStarted = Signal()
    downloadFinished = Signal()

    requestStarted = Signal(EfdCacheRequest, int)
    requestTerminated = Signal(EfdCacheRequest, int)
    requestFinished = Signal(EfdCacheRequest, int)

    def __init__(self, sal: MetaSAL, num_tasks: int = 10):
        super().__init__()

        self.downloads = 0
        self.num_tasks = num_tasks
        self.sal = sal

        self.cache: EfdCache | None = None

        self.worker_queue: asyncio.Queue[tuple[EfdCacheRequest, Time]] = asyncio.Queue()
        self.create_workers()

    async def worker(self, number: int) -> None:
        """
        Worker thread. Request new tasks from worker_queue and execute those.

        Parameters
        ----------
        number : `int`
            Worker internal number.
        """
        while True:
            request, timepoint = await self.worker_queue.get()
            try:
                assert self.cache is not None

                self.requestStarted.emit(request, number)

                await self.cache.load(request)
                request.cache.set_current_time(timepoint)
                self.send_cache(request.topic, request.cache)
                self.requestFinished.emit(request, number)
            except asyncio.CancelledError:
                self.requestTerminated.emit(request, number)
            except Exception as ex:
                logging.warn(
                    "While loading %s (%s to %s): %s.",
                    request.topic,
                    request.start.isot,
                    request.end.isot,
                    str(ex),
                )
                self.requestTerminated.emit(request, number)
            finally:
                if request.topic == "logevent_ilcWarning":
                    print("ILC warning fin")

                self.downloads += 1
                self.worker_queue.task_done()

    def create_workers(self) -> None:
        """
        Create workers to execute EfdCacheRequest from worker_queue.
        """
        self.workers = [
            asyncio.create_task(self.worker(i)) for i in range(self.num_tasks)
        ]

    def send_cache(self, topic: str, cache: EfdTopicCache) -> None:
        """
        Send cached values to EUI. Emits signal associated with the topic, with
        data from the cache.

        Parameters
        ----------
        topic : `str`
            Topic name.
        cache : `EfdTopicCache`
            Cache content.
        """
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

        async def create_efd_cache(efd: str) -> None:
            self.cache = EfdCache(self.sal, efd)

        if self.cache is None or self.cache.efd != efd:
            logging.info("Initializing the EFD connection client to %s.", efd)
            cache_create_task = asyncio.create_task(create_efd_cache(efd))
            await cache_create_task
            assert self.cache is not None

        await self.cache.cleanup()

        start_time = time.monotonic()
        self.downloads = 0

        reported_ranges: list[tuple[Time, Time]] = []

        for request in self.cache.new_requests(timepoint, duration):
            await self.worker_queue.put((request, timepoint))
            if self.downloads == 0:
                self.downloadStarted.emit()
            if (request.start, request.end) not in reported_ranges:
                logging.info("Loading %s - %s.", request.start.isot, request.end.isot)
                reported_ranges.append((request.start, request.end))

        await self.worker_queue.join()

        if self.downloads > 0:
            duration = time.monotonic() - start_time
            logging.info(
                "Downloaded %d topics in %.2f seconds (%.2f topics/second).",
                self.downloads,
                duration,
                self.downloads / duration,
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

    def stop(self) -> None:
        """
        Stops all requests.
        """
        while not self.worker_queue.empty():
            self.worker_queue.get_nowait()
            self.worker_queue.task_done()

        for worker in self.workers:
            worker.cancel("Requested to stop download.")

        self.create_workers()
