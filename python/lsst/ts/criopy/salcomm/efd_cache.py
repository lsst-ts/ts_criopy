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

__all__ = ["EfdCache"]

import asyncio
import logging
import traceback
from dataclasses import dataclass
from time import monotonic
from typing import TYPE_CHECKING, Any, Iterable

import pandas as pd
from astropy.time import Time, TimeDelta
from lsst_efd_client import EfdClient

if TYPE_CHECKING:
    from .meta_sal import MetaSAL


class RowClass:
    def __init__(self, row: pd.Series, changed: bool):
        self._changed = changed
        self.private_sndStamp = None

        last = None
        last_len = 0
        current_map: dict[int, Any] = {}

        def add_map(last) -> None:
            arr = [None] * len(current_map)
            for i in range(len(current_map)):
                if i in current_map.keys():
                    arr[i] = current_map[i]
                else:
                    logging.warn(
                        "Uncomplete array in EFD data - %s map %s",
                        last,
                        current_map,
                    )
                    return
            setattr(self, last, arr)

        for c in row.columns.values:
            v = row[c].item()
            # see if an array shall be created, appended or this is a new
            # attribute
            if last is not None and c.startswith(last) and c[last_len:].isnumeric():
                current_map[int(c[last_len:])] = v
            else:
                if last is not None:
                    add_map(last)

                if c[-1] == "0":

                    last = c[:-1]
                    last_len = len(last)
                    current_map = {0: v}
                else:
                    last = None
                    setattr(self, c, v)

        if last is not None:
            add_map(last)


class EfdTopicCache:
    data: pd.DataFrame | None = None
    current_data: RowClass | None = None
    start: Time | None = None
    end: Time | None = None

    def __init__(self):
        super().__init__()
        self.lock = asyncio.Lock()

    def interval(
        self, timepoint: Time, min_duration: TimeDelta, max_span: TimeDelta
    ) -> tuple[Time | None, Time | None]:
        """Returns new interval to be queried or None if no new data are
        required.

        Parameters
        ----------
        timepoint : Time
            Timepoint that needs to be included in the interval.
        min_duration : TimeDelta
            Minimal duration of the interval.
        max_span : TimeDelta
            Maximal distance between new and existing (cached) interval. If the
            proposed interval is above that parameter from the existing
            (cached) data, new_interval in return will be set to True and time
            around timepoint will be returned..

        Returns
        -------
        start : Time | None
            Starting interval, or None if timepoint is already cached.
        end : Time | None
            Ending interval, or None if timepoint is already cached.
        """
        half_duration = min_duration / 2

        new_start = timepoint - TimeDelta(0.05, format="sec")
        new_end = timepoint + min_duration

        if self.start is None or self.end is None:
            return new_start, new_end
        elif timepoint < self.start:
            duration = self.start - timepoint
            if duration >= max_span:
                return new_start, new_end
            if duration < min_duration:
                return (
                    self.start - min_duration,
                    self.start,
                )
            return timepoint - half_duration, self.start
        elif timepoint > self.end:
            duration = timepoint - self.end
            if duration >= max_span:
                return new_start, new_end
            if duration < min_duration:
                return self.end, self.end + min_duration
            return self.end, timepoint + half_duration
        return None, None

    @property
    def empty(self) -> bool:
        return self.data is None or self.data.empty

    def get(self) -> RowClass | None:
        return self.current_data

    def set_current_time(self, timepoint: Time) -> None:
        if self.empty:
            self.current_data = None
            return

        assert self.data is not None
        timestr = timepoint.iso + "+00:00"

        row = self.data.loc[:timestr].tail(n=1)
        if row.empty:
            self.current_data = None
            return

        changed = False

        if self.current_data is not None:
            if self.current_data.private_sndStamp != row["private_sndStamp"].item():
                changed = True

        self.current_data = RowClass(row, changed)

    def clear(self) -> None:
        self.data = None

    def merge(self, data: pd.DataFrame) -> None:
        if self.data is None:
            self.data = data
        elif not (data.empty):
            try:
                if data.index[0] == self.data.index[-1]:
                    data.drop(data.index[0], inplace=True)
                elif self.data.index[0] == data.index[-1]:
                    data.drop(data.index[-1], inplace=True)

                self.data = pd.merge_ordered(self.data, data, how="left")
                self.data.sort_index(inplace=True)
            except Exception:
                print(
                    "Merge\n",
                    self.data,
                    "\n++++++++++++++++",
                    data,
                    "\n=======================",
                )
                traceback.print_exc()

    def update(self, start: Time, end: Time) -> None:
        if self.start is None or start < self.start:
            self.start = start
        if self.end is None or end > self.end:
            self.end = end
        if self.current_data is None:
            self.set_current_time(self.start)


@dataclass
class EfdCacheRequest:
    topic: str
    cache: EfdTopicCache
    start: Time
    end: Time
    interval: TimeDelta

    def is_event(self) -> bool:
        return self.topic.startswith("logevent_")


class EfdCache:
    """Caches data available from SAL, so those can be quickly accessed in
    downloaded DataFrames."""

    def __init__(self, sal: "MetaSAL", efd_client: EfdClient):
        super().__init__()
        self.name = sal.remote.salinfo.name
        self.efd_client = efd_client
        self.max_span = TimeDelta(65, format="sec")
        self.sem = asyncio.Semaphore(10)

        self.telemetry = {t: EfdTopicCache() for t in sal.telemetry()}
        self.events = {e: EfdTopicCache() for e in sal.events()}
        self.shall_delete: list[EfdCacheRequest] = []
        self.delete_lock = asyncio.Lock()

    def __getitem__(self, key: str) -> EfdTopicCache | None:
        if key in self.telemetry.keys():
            return self.telemetry[key]
        elif key in self.events.keys():
            return self.events[key]
        return None

    def __getattr__(self, name: str) -> EfdTopicCache | None:
        key = name[4:]
        if name.startswith("tel_"):
            return self.telemetry[key]
        elif name.startswith("evt_"):
            return self.events[key]
        raise AttributeError(f"Unknow cache attribute: {name}")

    async def load(self, request: EfdCacheRequest) -> None:
        async def chunk(request, start, end) -> None:
            try:
                logging.debug(
                    "Fetching %s - %s to %s.",
                    request.topic,
                    start.isot,
                    end.isot,
                )
                query_start = monotonic()
                data = await self.efd_client.select_time_series(
                    f"lsst.sal.{self.name}.{request.topic}",
                    "*, private_sndStamp",
                    start,
                    end,
                )
                duration = monotonic() - query_start
                request.cache.merge(data)
                data_len = len(data.index)
                logging.info(
                    "Fetched %d rows from %s in %.3f seconds - %.2f rows/second.",
                    data_len,
                    request.topic,
                    duration,
                    data_len / duration,
                )
                request.cache.update(start, end)
            except ValueError as er:
                logging.warn(
                    "Event %s is not in the efd - will be ignored: %s.",
                    request.topic,
                    str(er),
                )
                async with self.delete_lock:
                    if request.topic not in [r.topic for r in self.shall_delete]:
                        self.shall_delete.append(request)

        async def load_interval(request: EfdCacheRequest, interval: TimeDelta) -> None:
            if interval > TimeDelta(0, format="sec"):
                if request.cache.end is not None and request.cache.end != request.start:
                    request.cache.clear()

                i_start = i_end = request.start
                i_end += interval
                while i_start < i_end:
                    i_end = min(i_start + interval, request.end)
                    await chunk(request, i_start, i_end)
                    i_start = i_end
            else:
                if (
                    request.cache.start is not None
                    and request.cache.start != request.end
                ):
                    request.cache.clear()

                i_start = i_end = request.end
                i_start += interval
                while i_start != i_end:
                    i_start = max(i_end + interval, request.start)
                    await chunk(request, i_start, i_end)
                    i_end = i_start

        async with self.sem:
            async with request.cache.lock:
                if request.cache.start is None or request.end == request.cache.start:
                    await load_interval(request, request.interval)
                else:
                    await load_interval(request, -request.interval)

    async def cleanup(self) -> None:
        async with self.delete_lock:
            for r in self.shall_delete:
                if r.is_event():
                    del self.events[r.topic[9:]]
                else:
                    del self.telemetry[r.topic]
            self.shall_delete = []

    def new_requests(
        self, timepoint: Time, interval: TimeDelta
    ) -> Iterable[EfdCacheRequest]:
        """Retuns new EfdCacheRequest needed to load data in the interval.
        Parameters
        ----------
        timepoint : Time
        interval : TimeDelta

        Returns
        -------
        requests : [EfdCacheRequest]
        """
        for t, c in self.telemetry.items():
            if t != "forceActuatorData":
                continue

            start, end = c.interval(timepoint, interval, self.max_span)
            if start is None:
                logging.debug("Already fetched %s at time %s.", t, timepoint.isot)
                continue
            yield EfdCacheRequest(
                t, c, start, end, interval + TimeDelta(0.05, format="sec")
            )
        return

        for e, c in self.events.items():
            start, end = c.interval(timepoint, interval, self.max_span)
            if start is None:
                logging.debug("Already fetched logevent_%s at time %s.", t, timepoint)
                continue
            yield EfdCacheRequest(
                "logevent_" + e, c, start, end, interval + TimeDelta(0.05, format="sec")
            )
