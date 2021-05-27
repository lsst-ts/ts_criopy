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

import numpy as np


class TimeCache:
    """Cache for large float data. Holds rolling time window of records. Act as
    dictionary, where keys are specified in items constructor. [] and len
    operators are supported.

    Parameters
    ----------
    size : `int`
        Cache size.
    items : [(`str`,`str`)]
        Items stored in the cache.
    window : `int`, optional
        Receiving window size. Defaults to 3.
    """

    def __init__(self, size, items, window=3):
        self._size = size
        self._window = window
        self.data = np.zeros((self._size), items, order="F")
        self.clear()

    def clear(self):
        """Clear cache."""
        self.current_index = 0
        self.filled = False

    def resize(self, size):
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

    def append(self, data):
        """Append new row to end of data.

        Parameters
        ----------
        data : `tupple`
            New row data.
        """
        if self.current_index >= self._size:
            self.current_index = 0
            self.filled = True
        self.data[self.current_index] = data
        self.current_index += 1

    def startTime(self):
        """Return timestamp of the last data point.

        Returns
        -------
        endTime : `float`
            None if cache is empty. Otherwise timestamp of the first data point."""
        if self.filled is False:
            if self.current_index > 0:
                return self.data[0]["timestamp"]
            return None

        if self.current_index >= self._size:
            return self.data[0]["timestamp"]
        return self.data[self.current_index]["timestamp"]

    def endTime(self):
        """Return timestamp of the last data point.

        Returns
        -------
        endTime : `float`
            None if cache is empty. Otherwise timestamp of the last data point."""
        if self.current_index == 0:
            if self.filled is False:
                return None
            return self.data[-1]["timestamp"]
        return self.data[self.current_index - 1]["timestamp"]

    def timeRange(self):
        return (self.startTime(), self.endTime())

    def rows_reverse(self):
        """Yelds reversed row iterator."""
        for r in range(self.current_index - 1, -1, -1):
            yield self.data[r]
        if self.filled:
            for r in range(self._size - 1, self.current_index - 1, -1):
                yield self.data[r]

    def savetxt(self, filename, **kwargs):
        """Saves data to file.

        Parameters
        ----------
        filename : `str`
            Filename to save the data.
        **kwargs : `dict`, optional
            Arguments passed to np.savetxt()
        """
        if self.filled:
            np.savetxt(
                filename,
                list(self.data[self.current_index + 1 :])
                + list(self.data[: self.current_index]),
                **kwargs,
            )
        else:
            np.savetxt(filename, self.data[: self.current_index], **kwargs)

    def create_hdf5_datasets(self, size, group, group_args={}):
        """Creates HDF5 datasets.

        Parameters
        ----------
        size : `int`
            Total size of records to be created.
        group : `h5py.Group`
            HDF5 group.
        group_args : `dict`
            Keyword arguments passed to create_group call. It is recommended to
            pass at least chunks=True. Please See h5py.Group.create_dataset for details.
        """
        self._hdf5_datasets = {}

        for n in self.data.dtype.names:
            self._hdf5_datasets[n] = group.create_dataset(
                n, (size), self.data.dtype.base[n], **group_args
            )
        self.hdf5_index = 0
        self._hdf5_size = size

    def h5_filled(self):
        """Returns True if HDF5 files is filled."""
        return self.hdf5_index >= self._hdf5_size

    def savehdf5(self, size):
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

    def columns(self):
        """Returns column names.

        Returns
        -------
        columns : `[str]`
            Columns names as specified in constructor.
        """
        return self.data.dtype.names

    def __getitem__(self, key):
        if self.filled:
            return list(self.data[self.current_index + 1 :][key]) + list(
                self.data[: self.current_index][key]
            )
        else:
            return list(self.data[: self.current_index][key])

    def __len__(self):
        return self._size if self.filled else self.current_index
