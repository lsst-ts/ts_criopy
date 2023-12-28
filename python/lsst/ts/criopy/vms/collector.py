# Save VMS data to a file.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org). See the COPYRIGHT file at the top - level directory
# of this distribution for details of code ownership.
#
# This program is free software : you can redistribute it and / or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.If not, see <https://www.gnu.org/licenses/>.

import asyncio
import logging
import os
import time
import typing
from datetime import datetime

import click
import h5py
import numpy as np
from lsst.ts.salobj import BaseMsgType, Domain, Remote

from .cache import Cache

__all__ = ["Collector", "VMS_DEVICES"]

TIME_RESERVE = 50  # time cache for 50 second more

VMS_DEVICES = ["M1M3", "M2", "Rotator"]


class Collector:
    """Class for collecting VMS data.

    Parameters
    ----------

    index : `int`
        Device index. In current LSST mapping, 1 - M1M3, 2 - M2, 3 -
        CameraRotator VMS subsystem.
    fn_template : `str`
        Template for filename. Can contain % for datetime.strftime expansion,
        and ${...} for variable expansion (e.g. ${ext} get expanded to filename
        extension).
    size : `int`, optional
        File size in bytes.
    file_type : `str`, optional
        File type. Defaults to zip compressed hdf5 - "z5".
    header : `bool`, optional
        Print header to text file. Defaults to True.
    chunk_size : `int`, optional
        Number of record in Cache. Defaults to 5000.
    daemonized : `bool`, optional
        True if running on background. Will change logging.  Defaults to False.
    rotate : `float`, optional
        Defaults to None. If specified, rotate output file every rotate
        seconds.
    rotate_offset : `float`, optional
        Rotate offset. Defaults to None. If provided, start new file every n *
        rotate + rotate_offset ctime (from 1-1-1970) seconds.
    """

    def __init__(
        self,
        index: int,
        fn_template: str,
        size: int = -1,
        file_type: str = "z5",
        header: bool = True,
        chunk_size: int = 5000,
        daemonized: bool = False,
        rotate: float | None = None,
        rotate_offset: float = 0,
    ):
        self.log = logging.getLogger("VMSlogger")

        self.index = index
        self.fn_template = fn_template
        self.configured_size = size
        self.size = size
        self.file_type = file_type
        self.header = header
        self.configured_chunk_size = chunk_size
        self.chunk_size = chunk_size
        self.daemonized = daemonized
        self.rotate = rotate
        self.rotate_offset = rotate_offset
        self.next_rotate: float | None = None
        self.h5file = None

        self._bar_index = 0
        self._last_bar = 0
        self._current_file_date = time.time()

        device_sensors = [3, 6, 3]

        self.log.debug(
            f"Creating cache: index={self.index+1}"
            f" device={device_sensors[self.index]} type={self.file_type}"
        )

        self.cache_size = self.configured_chunk_size + 50000

        self.cache = Cache(self.cache_size, device_sensors[self.index])

    def __calculate_next_rotate(self, timestamp: float) -> float:
        # calleres qurantee self.rotate is not None
        assert self.rotate is not None
        (q, r) = divmod(timestamp, self.rotate)
        return (q + 1) * self.rotate + self.rotate_offset

    def _need_rotate(self, timestamp: float) -> bool:
        if self.rotate is None:
            return False
        elif self.next_rotate is None:
            self.next_rotate = self.__calculate_next_rotate(timestamp)
            self.log.debug(
                f"Will rotate at {self.next_rotate} - current timestamp is"
                f" {timestamp:.04f}, in"
                f" {self.next_rotate - timestamp:.04f} seconds"
            )
            return False
        elif self.next_rotate <= timestamp:
            self.next_rotate += self.rotate
            return True
        return False

    def _get_filename(self, date: datetime) -> str:
        filename = datetime.strftime(date, self.fn_template)
        repl = [
            ("name", VMS_DEVICES[self.index]),
            (
                "ext",
                "hdf"
                if "5" in self.file_type
                else "csv.gz"
                if "z" in self.file_type
                else "csv",
            ),
        ]
        for name, value in repl:
            filename = filename.replace("${" + name + "}", value)
        return filename

    def _create_file(self, date: datetime) -> None:
        self.filename = self._get_filename(date)
        self.log.debug(f"Creating {self.filename}")

        try:
            dirs = os.path.dirname(self.filename)
            if dirs != "":
                os.makedirs(dirs)
        except FileExistsError:
            pass

        if "5" in self.file_type:
            self.h5file = h5py.File(self.filename, "a")
            group_args: dict[str, str | int] = {"chunks": (self.chunk_size)}
            if "z" in self.file_type:
                group_args["compression"] = "gzip"
            self.cache.create_hdf5_datasets(self.size, self.h5file, **group_args)

    def _save_hdf5(self) -> bool:
        if self.h5file is None:
            return False
        count = self.chunk_size
        if self.rotate is None:
            if len(self.cache) < self.chunk_size:
                return False
        else:
            if self.next_rotate is None:
                if len(self.cache) == 0:
                    return False
                self._need_rotate(self.cache.startTime())

            next_index = self.cache.timestampIndex(self.next_rotate)
            if next_index is None:
                if len(self.cache) < self.chunk_size:
                    return False
                count = min(count, len(self.cache))
            else:
                count = min(count, next_index)
        if count > 0:
            self.log.debug(
                f"Saving device {VMS_DEVICES[self.index]} data to"
                f" {self.h5file.file.filename} from {self.cache.hdf5_index},"
                f" {count} rows"
            )
            self.cache.savehdf5(count)
            self.h5file.flush()
        return True

    def close(self) -> None:
        if self.h5file is not None:
            self.log.info(f"Closing HDF5 {self.h5file.file.filename}")
            self.h5file.close()

    def _h5_filled(self) -> bool:
        et = self.cache.endTime()
        if et is not None and self._need_rotate(et):
            return True
        return self.cache.h5_filled()

    async def _sample_daemon(self) -> None:
        saved_len = 0
        while True:
            current_len = saved_len + len(self.cache)
            self.log.debug(
                f"Waiting {VMS_DEVICES[self.index]}.."
                f" {100 * (current_len)/self.size:.02f}% {current_len} of"
                f" {self.size}"
            )
            if self.h5file is None:
                if current_len >= self.size:
                    break
            else:
                if self._save_hdf5():
                    saved_len += self.chunk_size
                if self._h5_filled():
                    break
            await asyncio.sleep(0.5)

    async def _sample_cli(self) -> None:
        async def collect_it(bar: typing.Any) -> None:
            while True:
                cur_index = self._bar_index
                bar.update(cur_index - self._last_bar)
                self._last_bar = cur_index
                cache_len = len(self.cache)
                if cache_len >= self.size:
                    break
                await asyncio.sleep(0.1)
                if self._save_hdf5():
                    break

        bar_size: float = 0

        if self.rotate is None:
            bar_size = self.size
        else:
            if self.next_rotate is None:
                bar_size = (
                    self.__calculate_next_rotate(self._current_file_date)
                    - self._current_file_date
                )
            else:
                bar_size = self.rotate
            bar_size = int(np.ceil(bar_size / self.cache.sampleTime))

        with click.progressbar(
            length=bar_size,
            label=(f"{VMS_DEVICES[self.index]} - {os.path.basename(self.filename)}"),
            show_eta=True,
            show_percent=True,
            width=0,
        ) as bar:
            if self.h5file is None:
                await collect_it(bar)
            else:
                while True:
                    await collect_it(bar)
                    if self._h5_filled():
                        break

            bar.update(self.size)

    async def _sample_file(self) -> None:
        if self.daemonized:
            await self._sample_daemon()
        else:
            await self._sample_cli()

        if self.h5file is not None:
            return

        self.log.info(f"Saving CSV to {self.filename}")
        kwargs = {"delimiter": ","}
        if self.header:
            kwargs["header"] = ",".join(self.cache.columns())
        self.cache.savetxt(self.filename, self.size, **kwargs)

    async def collect_data(self, single_shot: bool) -> None:
        """Create data files, fills them with data.

        Parameters
        ----------
        single_shot : `bool`
            When True, quits after single file is recorded.
        """
        try:
            async with Domain() as domain:
                remote = Remote(domain, "MTVMS", index=self.index + 1, start=False)
                remote.tel_data.callback = self._data
                remote.evt_fpgaState.callback = self._fpgaState

                await remote.start()

                await self._fpgaState(remote.evt_fpgaState.get())

                while True:
                    if self.next_rotate is not None and self.rotate is not None:
                        self._current_file_date = self.next_rotate - self.rotate
                    ts = time.localtime(self._current_file_date)
                    self._create_file(datetime(*ts[:6]))
                    await self._sample_file()
                    if single_shot:
                        break

        except Exception:
            self.log.exception(f"Cannot collect data for {VMS_DEVICES[self.index]}")

    async def _data(self, data: BaseMsgType) -> None:
        self.cache.newChunk(data)
        if data.sensor == 1:
            self._bar_index += len(data.accelerationX)

    async def _fpgaState(self, data: BaseMsgType) -> None:
        period = 1 if data is None else data.period
        freq = 1000 if data is None else int(np.ceil(1000.0 / period))
        self.log.info(f"{VMS_DEVICES[self.index]} frequency {freq}, period {period}")
        self.cache.setSampleTime(period / 1000.0)
        if "5" in self.file_type:
            if self.configured_size < 0:
                if self.rotate is None:
                    self.size = 86400 * freq
                else:
                    # TIME_RESERVE second more than needed
                    self.size = int((self.rotate + TIME_RESERVE) * freq)
            self.chunk_size = min(self.configured_chunk_size, self.size - 10)
        else:
            if self.configured_size < 0:
                self.size = 86400 * freq
            self.chunk_size = self.size - 10

        self.cache_size = self.chunk_size + TIME_RESERVE * freq

        self.cache.resize(self.cache_size)
