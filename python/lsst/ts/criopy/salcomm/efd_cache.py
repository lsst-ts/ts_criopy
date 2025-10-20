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

import logging
from typing import TYPE_CHECKING, Iterable

from astropy.time import Time, TimeDelta
from lsst_efd_client import EfdClient

from .efd_cache_request import EfdCacheRequest
from .efd_topic_cache import EfdTopicCache

if TYPE_CHECKING:
    from .meta_sal import MetaSAL


class EfdCache:
    """Caches data available from SAL, so those can be quickly accessed in
    downloaded DataFrames. Substitutes SAL Remote when SAL ingest hijacking is
    active.

    Implements both __getitem__ (for dictionary-like access) and __getattr__
    (for record-like access).

    Parameters
    ----------
    sal : `MetaSAL`
        SAL object. Provideds topics names.
    efd : `str`
        EFD name.
    max_span : `float`, optional
        Maximum cache size in seconds. When data further from the current cache
        start or end are requested, the cache content will be deleted. Default
        to 600 seconds = 10 minutes.

    Attributes
    ----------
    name : `str`
        SAL remote name. Used in query to query the right data.
    efd_client : `EfdClient`
        EFD access client.
    """

    def __init__(
        self,
        sal: "MetaSAL",
        efd: str,
        max_span: float = 600,
        num_tasks: int = 10,
    ):
        super().__init__()
        self.name = sal.remote.salinfo.name
        self.efd = efd

        self.efd_client = EfdClient(self.efd)
        self.max_span = TimeDelta(max_span, format="sec")

        self.telemetry = {t: EfdTopicCache() for t in sal.telemetry()}
        self.events = {e: EfdTopicCache() for e in sal.events()}
        self.__shall_delete: list[EfdCacheRequest] = []

    def __getitem__(self, key: str) -> EfdTopicCache | None:
        """
        Access topics as class dictionary entries. Provides convenient way to
        access topics by names without prefix.

        Parameters
        ----------
        key : `str`
            Topic name in EFD. Without any prefix.
        """

        if key in self.telemetry.keys():
            return self.telemetry[key]
        elif key in self.events.keys():
            return self.events[key]
        return None

    def __getattr__(self, name: str) -> EfdTopicCache | None:
        """
        Implements record-like access to topics stored in Cache. This is needed
        so the EfdCache can be used in lieu of the SAL Remote for SAL
        hijacking.

        Parameters
        ----------
        name : `str`
            Requested topic name. As SAL uses prefixes (evt_ for logevents and
            tel_ for telemetry), those are strip from the name. If topic is
            hold by the cache, it is returned.
        """
        key = name[4:]
        if name.startswith("tel_"):
            return self.telemetry[key]
        elif name.startswith("evt_"):
            return self.events[key]
        raise AttributeError(f"Unknow cache attribute: {name}")

    async def load(self, request: EfdCacheRequest) -> None:
        try:
            await request.load(self.efd_client)
        except ValueError as er:
            logging.warn(
                "Event %s is not in the efd - will be ignored: %s.",
                request.topic,
                str(er),
            )
            if request.topic not in [r.topic for r in self.__shall_delete]:
                self.__shall_delete.append(request)
        except Exception as ex:
            logging.error(
                "Error while fetching %s - no data retrieved: %s",
                request.topic,
                str(ex),
            )

    async def cleanup(self) -> None:
        """
        Called after data are loaded to clean any bad topic. EFD doesn't create
        timeseries for SAL topics that were defined in XML schemas but never
        published. Calling cleanup assures EfdTopicCache entries for those
        topics are removed from future processing.
        """

        for r in self.__shall_delete:
            if r.is_event():
                del self.events[r.topic[9:]]
            else:
                del self.telemetry[r.topic]
        self.__shall_delete = []

    def new_requests(self, timepoint: Time, interval: TimeDelta) -> Iterable[EfdCacheRequest]:
        """
        Retuns new EfdCacheRequest needed to load data in the interval
        around timepoint. If a topic's cache is empty or its data are too far
        from the requested timepoint, assumes (timepoint - small offset,
        timepoint + interval) would be needed.

        Parameters
        ----------
        timepoint : Time
            Requested time.
        interval : TimeDelta
            Expected length of the interval.

        Returns
        -------
        requests : [EfdCacheRequest]
            Requests for new topic data. Those shall be passed to load
            function, running as tasks from the controlling process.
        """
        for t, c in self.telemetry.items():
            start, end = c.interval(timepoint, interval, self.max_span)
            if start is None:
                logging.debug(
                    "Already fetched %s at time %s for %s seconds.",
                    t,
                    timepoint.isot,
                    interval.sec,
                )
                continue
            yield EfdCacheRequest(self.name, t, c, start, end, TimeDelta(120.05, format="sec"))

        for e, c in self.events.items():
            start, end = c.interval(timepoint, interval, self.max_span)
            if start is None:
                logging.debug(
                    "Already fetched logevent_%s at time %s for %s seconds.",
                    t,
                    timepoint,
                    interval.sec,
                )
                continue
            yield EfdCacheRequest(
                self.name,
                "logevent_" + e,
                c,
                start,
                end,
                TimeDelta(600.05, format="sec"),
            )
