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

__all__ = ["EfdCacheRequest"]

import logging
from dataclasses import dataclass
from time import monotonic

from astropy.time import Time, TimeDelta
from lsst_efd_client import EfdClient

from .efd_topic_cache import EfdTopicCache


@dataclass
class EfdCacheRequest:
    """
    Holds data for a single EFD request.

    Attributes
    ----------
    topic : `str`
        Name of the topics. As stored in EFD, e.g. telemetry topics without
        prefix, events with logevent_ prefix.
    cache : `EfdTopicCache`
        Cache object associated with the topic.
    start : `Time`
        Start time of the requested interval.
    end : `Time`
        End time of the requested interval.
    max_chunk : `TimeDelta`
        Maximal chunk duration. Used to split loading into smaller chunks, that
        can be handled by EFD.
    """

    csc_name: str
    topic: str
    cache: EfdTopicCache
    start: Time
    end: Time
    max_chunk: TimeDelta

    def is_event(self) -> bool:
        return self.topic.startswith("logevent_")

    async def load(self, efd_client: EfdClient) -> None:
        """
        Fill cache specified in request with data obtained from the EFD.

        Parameters
        ----------
        request : `EfdCacheRequest`
           Request data.
        """

        async def chunk(start: Time, end: Time) -> None:
            logging.debug(
                "Fetching %s - %s to %s.",
                self.topic,
                start.isot,
                end.isot,
            )
            query_start = monotonic()
            data = await efd_client.select_time_series(
                f"lsst.sal.{self.csc_name}.{self.topic}",
                "*, private_sndStamp",
                start,
                end,
            )
            duration = monotonic() - query_start
            self.cache.merge(data)
            data_len = len(data.index)
            logging.info(
                "Fetched %d rows from %s in %.3f seconds - %.2f rows/second.",
                data_len,
                self.topic,
                duration,
                data_len / duration,
            )
            self.cache.update(start, end)

        async def load_interval(interval: TimeDelta) -> None:
            if interval.sec > 0:
                if self.cache.end is not None and self.cache.end != self.start:
                    self.cache.clear()

                i_start = i_end = self.start
                i_end += interval
                while i_start < self.end:
                    i_end = min(i_start + interval, self.end)
                    await chunk(i_start, i_end)
                    i_start = i_end
            else:
                if self.cache.start is not None and self.cache.start != self.end:
                    self.cache.clear()

                i_start = i_end = self.end
                i_start += interval
                while i_start != self.start:
                    i_start = max(i_end + interval, self.start)
                    await chunk(i_start, i_end)
                    i_end = i_start

        async with self.cache.lock:
            if self.cache.start is None or self.end == self.cache.start:
                await load_interval(self.max_chunk)
            else:
                await load_interval(-self.max_chunk)
