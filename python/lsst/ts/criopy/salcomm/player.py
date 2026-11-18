# This file is part of ts_criopy.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

__all__ = ["Player"]

import asyncio
import logging
import time

from astropy.time import Time, TimeDelta
from lsst_efd_client import EfdClient
from PySide6.QtCore import QObject, Signal

from .efd_cache import EfdCache, EfdCacheRequest, EfdTopicCache
from .meta_sal import MetaSAL


class Player(QObject):
    """
    Queries EFD for telemetry and events, build up a cache and replay the
    events. Queries are executed in parallel, using worker_queue for
    synchronization. The worker_queue is deleted when the close method is
    called.

    Signals
    -------
    downloadStarted
        Emmited when data download starts.
    downloadFinished
        Emmited when data download ends.
    requestStarted(request, worker)
        Emmited when request processing is started.
    requestTerminated(request, worker, Exception)
        Emmited when request processign is terminated (stopped).
    requestFinished(request, worker)
        Emmited when request processing is finished.

    Parameters
    ----------
    sal : `MetaSAL`
        SAL objects to replay. The topics in this fields are used to query EFD.
    cache : `EfdCache | None`
        EfdCache to query for data.
    efd_client : `EfdClient`
        EfdClient to query EFD data.
    efd_name : `str`
        Name of the EfdClient.
    num_tasks: `int`, optional
        Number of allowed parallel tasks. Defaults to 10.
    worker_queue: `asyncio.Queue | None`
        Task queue. If a new chunk has to be downloaded, it needs to be put
        into queue so workers can retrieve it.
    workers: `list[asyncio.Task] | None`
        Workers tasks.
    """

    downloadStarted = Signal()
    downloadFinished = Signal()

    requestStarted = Signal(EfdCacheRequest, int)
    requestTerminated = Signal(EfdCacheRequest, int, Exception)
    requestFinished = Signal(EfdCacheRequest, int)

    def __init__(self, sal: MetaSAL, num_tasks: int = 10):
        super().__init__()

        self.downloads = 0
        self.num_tasks = num_tasks
        self.sal = sal

        self.cache: EfdCache | None = None
        self.efd_client: EfdClient | None = None
        self.efd_name: str = ""

        self.worker_queue: asyncio.Queue[tuple[EfdCacheRequest, Time]] | None = None
        self.workers: list[asyncio.Task] | None = None

    async def worker(self, number: int) -> None:
        """
        Worker thread. Request new tasks from worker_queue and execute those.

        Parameters
        ----------
        number : `int`
            Worker internal number.
        """
        try:
            while True:
                if self.worker_queue is None:
                    return

                request, timepoint = await self.worker_queue.get()
                try:
                    assert self.cache is not None

                    self.requestStarted.emit(request, number)

                    await self.cache.load(request)
                    request.cache.set_current_time(timepoint)
                    self.send_cache(request.topic, request.cache)
                    self.requestFinished.emit(request, number)

                    if self.worker_queue is not None:
                        self.worker_queue.task_done()
                except Exception as ex:
                    self.requestTerminated.emit(request, number, ex)
                finally:
                    self.downloads += 1

        except (asyncio.queues.QueueShutDown, asyncio.CancelledError):
            pass

    def create_workers(self) -> None:
        """
        Create workers to execute EfdCacheRequest from worker_queue.
        """
        self.delete_workers()

        self.worker_queue = asyncio.Queue()
        self.workers = [asyncio.create_task(self.worker(i)) for i in range(self.num_tasks)]

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

    def delete_workers(self) -> None:
        """Shutdown workers queueu and delete the queueu and all workers."""
        if self.worker_queue is not None:
            self.worker_queue.shutdown(True)
            self.worker_queue = None

        if self.workers is not None:
            for worker in self.workers:
                worker.cancel("Deleted")
            self.workers = None

    async def close(self) -> None:
        """Close efd_client connection and delete workers."""
        if self.efd_client is not None:
            await self.efd_client.close()
            self.delete_workers()
            logging.info("Closed connection to %s", self.efd_name)

    async def replay(self, efd_name: str, timepoint: Time, duration: TimeDelta) -> None:
        """
        Load data into cache. Starts multiple tasks to load data to speed up
        the process.

        Parameters
        ----------
        efd_name : `str`
            EFD name.
        timepoint : `Time`
            Requested (exact) time. After replay ends, the call guarantees data
            (telemetry and events) for this time will be loaded in the cache.
        duration : `TimeDelta`
            Interval length. This is the prefered length of the cache around
            timepoint.
        """
        if self.cache is None or self.efd_name != efd_name:
            logging.info("Initializing the EFD connection tp %s.", efd_name)
            self.efd_client = EfdClient(efd_name)
            self.efd_name = efd_name
            self.cache = EfdCache(self.sal, self.efd_client)
            assert self.cache is not None

        await self.cache.cleanup()

        start_time = time.monotonic()
        self.downloads = 0

        reported_ranges: list[tuple[Time, Time]] = []

        self.create_workers()

        assert self.worker_queue is not None

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
        self.delete_workers()

        self.create_workers()
