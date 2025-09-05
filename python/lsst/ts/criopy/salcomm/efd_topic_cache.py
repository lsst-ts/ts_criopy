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

__all__ = ["EfdTopicCache"]

import asyncio
import logging
from typing import Any

import pandas as pd
from astropy.time import Time, TimeDelta


class EfdTopic:
    """
    Contains single topic data. The constructor sets class attributes, so
    the EFD row (pandas.Series) si transformed to SAL Topic-like structure.
    This class objects can be passed to emit function to send data around as
    SAL signal.  Assuming SAL triggered updates are disabled (see the
    `MetaSAL.freeze` method), this highjack the SAL topics to send to EUI
    historic data instead of the latest observatory telemetry.

    Attributes
    ----------
    topic_name.. : `float | int | str | list[float] | list[int]`
        Topics extracted from EFD row data. Created dynamically as encountred
        in the passed row parametr to the constructor.

    Parameters
    ----------
    row : `pd.Series`
        Data serie representing EFD row. This is transformed to SAL Topic-like
        structure, with EFD columns-stored arrays turned into array attributes.
    changed : `bool`
        If True, data were changed from tha last call. This is stored as
        _changed attribute.
    """

    def __init__(self, row: pd.Series, changed: bool):
        self._changed = changed
        self.private_sndStamp = None

        last = None
        last_len = 0
        current_map: dict[int, Any] = {}

        def add_map(last: str) -> None:
            arr = [None] * len(current_map)
            for i in range(len(current_map)):
                if i in current_map.keys():
                    arr[i] = current_map[i]
                else:
                    arr[i] = None
                    logging.warn(
                        "Uncomplete array in EFD data - %s map %s",
                        last,
                        current_map,
                    )
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
    """
    Caches single EFD topic. Stores EFD data. Provides access to the current
    row / SAL Topic-like EfdTopic object. Manages reloading new data blocks
    from the EFD. Implements get method (and can implement other methods, if
    needed) to replace SAL Topic object used in GUIs.

    Attributes
    ----------
    data : `pd.DataFrame | None`
        Cached EFD data.
    current_data : `EfdTopic | None`
        Current row. Updated with a call to set_current_time method.
    start : `Time | None`
        Cache start time. Used to record cache extend.
    end : `Time | none`
        Cache end time. Included for the same reason as start time.
    """

    data: pd.DataFrame | None = None
    current_data: EfdTopic | None = None
    start: Time | None = None
    end: Time | None = None

    def __init__(self) -> None:
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
        """
        Returns true when the cache is empty.

        Returns
        -------
        empty : bool
            True if cache is empty.
        """
        return self.data is None or self.data.empty

    def get(self) -> EfdTopic | None:
        """
        Retrieves current data. Mimics SAL Topic get method, but returns
        EfdTopic.

        Retuns
        ------
        data : EfdTopic
            Current (as set with call to set_current_time) data.

        See also
        --------
        lsst.ts.salobj.topics.ReadTopic.get()
        """
        return self.current_data

    def set_current_time(self, timepoint: Time) -> None:
        """
        Sets current timepoint in historical data.

        Parameters
        ----------
        timepoint : `Time`
            The cache topic entry will be set to mimics SAL topic at the given
            time.
        """
        if self.empty:
            self.current_data = None
            return

        assert self.data is not None
        timestr = timepoint.iso + "+00:00"

        row = self.data.loc[:timestr].tail(n=1)
        if row.empty:
            self.current_data = None
            return

        changed = True

        if self.current_data is not None:
            if self.current_data.private_sndStamp == row["private_sndStamp"].item():
                changed = False

        self.current_data = EfdTopic(row, changed)

    def clear(self) -> None:
        """
        Clear cached data.
        """
        self.data = None

    def merge(self, data: pd.DataFrame) -> None:
        """
        Merge current date with a new EFD data frame.

        Parameters
        ----------
        data : `pd.DataFrame`
            Newly added data frame. Data
        """
        if self.empty:
            self.data = data
        elif data.empty:
            return
        else:
            assert self.data is not None
            try:
                if data.index[0] == self.data.index[-1]:
                    data.drop(data.index[0], inplace=True)
                elif self.data.index[0] == data.index[-1]:
                    data.drop(data.index[-1], inplace=True)
                self.data = pd.concat([self.data, data], sort=True)
            except Exception as er:
                logging.error("Exception when merging two DataFrames: %", str(er))

    def update(self, start: Time, end: Time) -> None:
        """
        Updates cache start and end times. Data retrieved from the EFD for the
        given time range shall be merged to Cache by calling the merge method.

        Parameters
        ----------
        start : `Time`
            Newly added block start time.
        end : `Time`
            Newly added block end time.
        """
        if self.start is None or start < self.start:
            self.start = start
        if self.end is None or end > self.end:
            self.end = end
        if self.current_data is None:
            self.set_current_time(self.start)
