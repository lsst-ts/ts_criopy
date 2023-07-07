# This file is part of M1M3 SS GUI.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top - level directory of this distribution
# for details of code ownership.
#
# This program is free software : you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

__all__ = ["TimeCache"]

import typing

import h5py
import numpy as np


class TimeCache:
    """Cache for large float data. Holds rolling time window of records. Act as
    dictionary, where keys are specified in items constructor. [] and len
    operators are supported. Assumes a column with name "timestamp" exists and
    contains row timestamps.

    Attributes
    ----------
    current_index : `int`
        Index of last member. If filled is true, current_index + 1 is valid
        value, containing first row in the array.
    filled : `bool`
        True if the array rolled over. Last element in the array contain valid
        value, and values continue from 0 till current_index.
    data : `numpy.array`
        Array containing data.

    Parameters
    ----------
    size : `int`
        Cache size.
    items : [(`str`,`str`)]
        Items stored in the cache.
    """

    def __init__(self, size: int, items: list[tuple[str, str]]):
        self._size = size
        self.data = np.zeros((self._size), items, order="F")
        self.clear()

    def clear(self) -> None:
        """Clear cache."""
        self.current_index = 0
        self.filled = False

    def resize(self, size: int) -> None:
        """Change cache size. Data are preserved - either all rows are used
        when expanding, or the most recent ones are stored when shrinking.

        Parameters
        ----------
        size : `int`
            New size.
        """
        clength = len(self)
        if size == clength:
            return
        newdata = np.zeros(size, self.data.dtype)
        n_current = r = min(clength, size)
        for s in self.rows_reverse():
            r -= 1
            newdata[r] = s
            if r == 0:
                break
        self.filled = (n_current == size) and (clength > 0)
        self.current_index = n_current

        self.data = newdata
        self._size = size

    def append(self, data: tuple[float, ...]) -> None:
        """Append new row to end of data.

        Parameters
        ----------
        data : `(float, ...)`
            New row data. First tuple member is timestamp.
        """
        if self.current_index >= self._size:
            self.current_index = 0
            self.filled = True
        self.data[self.current_index] = data
        self.current_index += 1

    def startTime(self) -> float:
        """Return timestamp of the last data point.

        Returns
        -------
        startTime : `float`
            None if cache is empty. Otherwise timestamp of the first data
            point.

        Raises
        ------
        RuntimeError
            When cache is empty.

        """
        if self.filled is False:
            if self.current_index > 0:
                return self.data[0]["timestamp"]
            raise RuntimeError("Cannot retrieve start time from empty TimeCache.")

        if self.current_index >= self._size:
            return self.data[0]["timestamp"]
        return self.data[self.current_index]["timestamp"]

    def endTime(self) -> float:
        """Return timestamp of the last data point.

        Returns
        -------
        endTime : `float`
            None if cache is empty. Otherwise timestamp of the last data
            point.

        Raises
        ------
        RuntimeError
            When cache is empty.
        """
        if self.current_index == 0:
            if self.filled is False:
                raise RuntimeError("Cannot retrieve end time from empty TimeCache.")
            return self.data[-1]["timestamp"]
        return self.data[self.current_index - 1]["timestamp"]

    def timeRange(self) -> tuple[float, float]:
        """Returns timestamp range.

        Returns
        -------
        startTime : `float`
            Equals startTime() call.
        endTime : `float`
            Equals endTime() call.
        """
        return (self.startTime(), self.endTime())

    def _mapIndex(self, index: int) -> int:
        """Returns array index of item with index (from array start) index.

        Parameters
        ----------
        index : `int`
            Requested index in an array.

        Returns
        -------
        mapped : `int`
            Index in sub-array.
        """
        if self.filled:
            if index < len(self) - self.current_index:
                return index + self.current_index
            return index - len(self) + self.current_index
        return index

    def timestampIndex(self, timestamp: float) -> int | None:
        """Search for row's index with timestamp value bigger than timestamp.

        Parameters
        ----------
        timestamp : `float`
            Value to search.

        Returns
        -------
        index : `int`
            Index of the first element >= timestamp parameter. None if such
            index doesn't exists.
        """
        left, right = 0, len(self) - 1

        left_v = self.data[self._mapIndex(left)]["timestamp"]
        right_v = self.data[self._mapIndex(right)]["timestamp"]

        if timestamp < left_v:
            return left

        if timestamp > right_v:
            if np.isclose(right_v, timestamp):
                return right
            return None

        while left < right:
            middle = (left + right) // 2
            midval = self.data[self._mapIndex(middle)]["timestamp"]
            if np.isclose(midval, timestamp):
                return middle
            if midval < timestamp:
                left = middle + 1
            else:
                right = middle - 1

        return left

    def rows_reverse(self) -> typing.Generator[float, None, None]:
        """Yields reversed row iterator."""
        for r in range(self.current_index - 1, -1, -1):
            yield self.data[r]
        if self.filled:
            for r in range(self._size - 1, self.current_index - 1, -1):
                yield self.data[r]

    def savetxt(
        self, filename: str, size: int | None = None, **kwargs: typing.Any
    ) -> None:
        """Saves data to CSV file. Saved data are forgotten.

        Parameters
        ----------
        filename : `str`
            Filename to save the data.
        size : `int`
            Size of data to store. Defaults to all current data.
        **kwargs : `dict`, optional
            Arguments passed to np.savetxt()
        """

        if size is None:
            size = len(self)

        new_data = np.array(self.data)

        remaining = len(self) - size

        for n in self.data.dtype.names:
            new_data[n][:remaining] = self[n][size:]

        if self.filled:
            data = list(self.data[self.current_index + 1 :]) + list(
                self.data[: self.current_index]
            )
        else:
            data = list(self.data)

        self.filled = False
        self.data = new_data
        self.current_index = remaining

        np.savetxt(filename, data[:size], **kwargs)

    def create_hdf5_datasets(
        self, size: int, group: h5py.Group, **group_args: typing.Any
    ) -> None:
        """Creates HDF5 datasets.

        Parameters
        ----------
        size : `int`
            Total size of records to be created.
        group : `h5py.Group`
            HDF5 group.
        **group_args : `dict`
            Keyword arguments passed to create_group call. It is recommended to
            pass at least chunks=True. Please See h5py.Group.create_dataset for
            details.
        """
        self._hdf5_datasets = {}

        for n in self.data.dtype.names:
            self._hdf5_datasets[n] = group.create_dataset(
                n, (size), self.data.dtype.base[n], **group_args
            )
        self.hdf5_index = 0
        self._hdf5_size = size

    def h5_filled(self) -> bool:
        """Returns True if HDF5 file is filled."""
        return self.hdf5_index >= self._hdf5_size

    def savehdf5(self, size: int) -> None:
        """Save data to H5D group. Saved data are forgotten.

        Parameters
        ----------
        size : `int`
            Size of data to store.
        """
        new_data = np.array(self.data)
        if self.hdf5_index + size > self._hdf5_size:
            size = self._hdf5_size - self.hdf5_index

        remaining = len(self) - size

        for n in self.data.dtype.names:
            d = self[n]
            self._hdf5_datasets[n][self.hdf5_index : self.hdf5_index + size] = d[:size]
            new_data[n][:remaining] = d[size:]

        self.filled = False
        self.data = new_data
        self.current_index = remaining

        self.hdf5_index += size

    def columns(self) -> list[str]:
        """Returns column names.

        Returns
        -------
        columns : `[str]`
            Columns names as specified in constructor.
        """
        return self.data.dtype.names

    def __getitem__(self, key: str) -> list[float]:
        if self.filled:
            return list(self.data[self.current_index :][key]) + list(
                self.data[: self.current_index][key]
            )
        else:
            return list(self.data[: self.current_index][key])

    def __len__(self) -> int:
        return self._size if self.filled else self.current_index
