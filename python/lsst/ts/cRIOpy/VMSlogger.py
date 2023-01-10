#!/usr/bin/env python3.8

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

import os
import os.path
import signal
import sys
import numpy as np

import argparse
import asyncio
import click
from datetime import datetime
import logging

from lsst.ts.salobj import Domain, Remote
from . import parseDuration
from .VMS import Cache

TIME_RESERVE = 50  # time cache for 50 second more

try:
    import h5py

    has_h5py = True
except ModuleNotFoundError:
    has_h5py = False


devices = ["M1M3", "M2", "Rotator"]

parser = argparse.ArgumentParser(
    description="Save VMS data to a file, either HDF5 or CSV.",
    epilog="Data are read as they arrive in DDS messages, matched by"
    " timestamps. Only complete (from all accelerometers the device provides)"
    " records are stored. Allows either single or multiple devices recording. Can"
    " be launched as daemon, running on background. Recorded data can be analysed"
    " offline with VMSGUI.",
)
parser.add_argument(
    "devices", type=str, nargs="+", help="name or index of CSC", choices=devices
)
parser.add_argument(
    "-5",
    dest="h5py",
    action="store_true",
    help="save into HDF 5. Requires h5py (pip install h5py). Save to CSV if not provided.",
)
parser.add_argument(
    "--chunk-size",
    dest="chunk_size",
    default=5000,
    type=int,
    help="receiving chunk size. After receiving this number of records, data"
    " are added to HDF5 file (and the file flushed to disk). Has no effect if CSV"
    " (default) format is used. Defaults to 5000.",
)
parser.add_argument(
    "-d", dest="debug", default=0, action="count", help="increase debug level"
)
parser.add_argument(
    "--header", dest="header", action="store_true", help="adds header with column names"
)
parser.add_argument("-p", dest="pidfile", action="store", help="PID file location")
parser.add_argument(
    "-s",
    type=int,
    dest="size",
    default=None,
    help="number of records to save in a file. Default to 86400 seconds"
    " (assuming --rotate isn't specified)",
)
parser.add_argument(
    "-z", action="store_true", dest="zip_file", help="gzip output files"
)
parser.add_argument(
    "--single-shot",
    action="store_true",
    dest="single_shot",
    help="quit after recording single file (with -s records)",
)
parser.add_argument(
    "--template",
    action="store",
    dest="template",
    default="${name}_%Y-%m-%dT%H:%M:%S.${ext}",
    type=str,
    help="template used to construct output file path. Default to"
    " ${name}_%%Y-%%m-%%dT%%H:%%M:%%S.${ext}. strftime (%%) expansions are"
    " performed (see man strftime for details, %%Y for full (4 digit) year, %%m"
    " for calendar month,..) together with custom ${xx} expansion (${name} for"
    " device name, ${ext} for extension - hd5, cvs or cvs.gz). Directories in"
    " expanded file path are created as needed.",
)
parser.add_argument(
    "--workdir",
    action="store",
    dest="workdir",
    default=None,
    help="directory where files will be stored. Default to current directory.",
)
parser.add_argument(
    "--logfile",
    action="store",
    dest="logfile",
    default=None,
    help="write log messages to given file",
)
parser.add_argument(
    "--daemon",
    action="store_true",
    dest="daemon",
    help="starts as daemon (fork to start process).",
)
parser.add_argument(
    "--rotate",
    action="store",
    dest="rotate",
    default=None,
    type=parseDuration,
    help="rotate on given interval. Default to not rotate - rotate on reaching"
    " size number of entries. Can be used only with HDF5 output.",
)
parser.add_argument(
    "--rotate-offset",
    action="store",
    dest="rotate_offset",
    default=0,
    type=parseDuration,
    help="rotate at give offset from rotate interval (--rotate argument)",
)


device_sensors = [3, 6, 3]

logger = logging.getLogger("VMSlogger")


class Collector:
    def __init__(
        self,
        index,
        fn_template,
        size,
        file_type,
        header,
        chunk_size,
        daemonized,
        rotate,
        rotate_offset,
    ):
        self.index = index
        self.fn_template = fn_template
        self.configured_size = size
        self.size = size
        self.file_type = file_type
        self.header = header
        self.configured_chunk_size = chunk_size
        self.daemonized = daemonized
        self.rotate = rotate
        self.rotate_offset = rotate_offset
        self.next_rotate = None
        self.h5file = None

        logger.debug(
            f"Creating cache: index={self.index+1}"
            f" device={device_sensors[self.index]} type={self.file_type}"
        )

        self.cache_size = self.configured_chunk_size + 50000

        self.cache = Cache(self.cache_size, device_sensors[self.index])

    def _need_rotate(self, timestamp):
        if self.rotate is None:
            return False
        elif self.next_rotate is None:
            (q, r) = divmod(timestamp, self.rotate)
            self.next_rotate = (q + 1) * self.rotate + self.rotate_offset
            logger.debug(
                f"Will rotate at {self.next_rotate} - current timestamp is "
                f"{timestamp}, in {self.next_rotate - timestamp} seconds"
            )
            return False
        elif self.next_rotate <= timestamp:
            self.next_rotate += self.rotate
            return True
        return False

    def _get_filename(self, date):
        filename = datetime.strftime(date, self.fn_template)
        repl = [
            ("name", devices[self.index]),
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

    def _create_file(self, date):
        filename = self._get_filename(date)
        logger.info(f"Creating {filename}")

        try:
            dirs = os.path.dirname(filename)
            if dirs != "":
                os.makedirs(dirs)
        except FileExistsError:
            pass

        if "5" in self.file_type:
            self.h5file = h5py.File(filename, "a")
            group_args = {"chunks": (self.chunk_size)}
            if "z" in self.file_type:
                group_args["compression"] = "gzip"
            self.cache.create_hdf5_datasets(self.size, self.h5file, group_args)
        else:
            self.filename = filename

    def _save_hdf5(self):
        if self.h5file is None or len(self.cache) < self.chunk_size:
            return False
        logger.debug(
            f"Saving device {devices[self.index]} data to"
            f" {self.h5file.file.filename} from {self.cache.hdf5_index}"
        )
        self.cache.savehdf5(self.chunk_size)
        self.h5file.flush()
        return True

    def close(self):
        if self.h5file is not None:
            logger.info(f"Closing HDF5 {self.h5file.file.filename}")
            self.h5file.close()

    def _h5_filled(self):
        et = self.cache.endTime()
        if et is not None and self._need_rotate(et):
            return True
        return self.cache.h5_filled()

    async def _sample_daemon(self):
        saved_len = 0
        while True:
            current_len = saved_len + len(self.cache)
            logger.debug(
                f"Waiting {devices[self.index]}.."
                f" {100 * (current_len)/self.size:.02f}% {current_len} of {self.size}"
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

    async def _sample_cli(self):
        async def collect_it(bar):
            last_l = 0

            while True:
                cache_len = len(self.cache)
                if cache_len >= self.size:
                    break
                bar.update(cache_len - last_l)
                last_l = cache_len
                await asyncio.sleep(0.1)
                if self._save_hdf5():
                    bar.update(self.chunk_size - last_l)
                    break

        with click.progressbar(
            length=self.size,
            label=f"Getting data {devices[self.index]}",
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

    async def _sample_file(self):
        if self.daemonized:
            await self._sample_daemon()
        else:
            await self._sample_cli()

        if self.h5file is not None:
            return

        logger.info(f"Saving CSV to {self.filename}")
        kwargs = {"delimiter": ","}
        if self.header:
            kwargs["header"] = ",".join(self.cache.columns())
        self.cache.savetxt(self.filename, self.size, **kwargs)

    async def collect_data(self, single_shot):
        """Create data files, fills them with data.

        Parameters
        ----------
        single_shot : `bool`
            When True, quits after single file is recorded.
        """
        try:
            async with Domain() as domain:
                remote = Remote(domain, "MTVMS", index=self.index + 1, start=False)
                remote.tel_data.callback = lambda data: self.cache.newChunk(data)
                remote.evt_fpgaState.callback = self._fpgaState

                await remote.start()

                await self._fpgaState(remote.evt_fpgaState.get())

                while True:
                    self._create_file(datetime.now())
                    await self._sample_file()
                    if single_shot:
                        break

        except Exception:
            logger.exception(f"Cannot collect data for {devices[self.index]}")

    async def _fpgaState(self, data):
        freq = 1000 if data is None else int(np.ceil(1000.0 / data.period))
        logger.debug(f"New frequency {freq}, period {data.period}")
        if "5" in self.file_type:
            if self.configured_size is None:
                if self.rotate is None:
                    self.size = 86400 * freq
                else:
                    # TIME_RESERVE second more than needed
                    self.size = (self.rotate + TIME_RESERVE) * freq
            self.chunk_size = min(self.configured_chunk_size, self.size - 10)
        else:
            if self.configured_size is None:
                self.size = 86400 * freq
            self.chunk_size = self.size - 10

        self.cache_size = self.chunk_size + 50000

        self.cache.resize(self.cache_size)


async def main(args, pipe=None):
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)

    if args.workdir is not None:
        try:
            os.chdir(args.workdir)
        except OSError as oerr:
            print(f"Cannot chdir to {args.workdir}: {oerr.strerror}")
            sys.exit(2)

    if args.logfile:
        fh = logging.FileHandler(args.logfile)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    if args.debug > 0:
        ch.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
    logger.addHandler(ch)

    tasks = []
    collectors = []

    def cancel_all(signum, frame):
        logger.info(f"Canceling after {signum}")
        for t in tasks:
            t.cancel()

    for signum in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]:
        signal.signal(signum, cancel_all)

    file_type = ""
    if args.zip_file:
        file_type += "z"
    if args.h5py:
        if has_h5py is False:
            logger.error(
                "Python is missing h5py module, saving HDF 5 file is not"
                " supported. Please install h5py first (pip install h5py)."
            )
            sys.exit(1)
        file_type += "5"
    else:
        if args.size is None:
            args.size = 50000

    if args.pidfile:
        f = open(args.pidfile, "w")
        f.write(f"{os.getpid()}\n")
        f.close()

    if args.rotate is not None:
        if not args.h5py:
            raise RuntimeError("--rotate option works only with HDF5 files")

    for d in args.devices:
        logger.info(f"Collecting {d} - template {args.template}")
        c = Collector(
            devices.index(d),
            args.template,
            args.size,
            file_type,
            args.header,
            args.chunk_size,
            args.daemon,
            args.rotate,
            args.rotate_offset,
        )
        collectors.append(c)
        tasks.append(asyncio.create_task(c.collect_data(args.single_shot)))

    if pipe is not None:
        os.write(pipe, b"OK\n")
        os.close(pipe)
    try:
        await asyncio.gather(*tasks)
        logger.info("Done")
    except asyncio.exceptions.CancelledError:
        logger.info("Canceled")

    for c in collectors:
        c.close()


def run():
    args = parser.parse_args()
    if args.daemon:
        import time

        r_pipe, w_pipe = os.pipe2(os.O_NONBLOCK)
        child = os.fork()
        if child == 0:
            os.close(0)
            os.close(1)
            os.close(2)

            dn = os.open("/dev/null", os.O_WRONLY)
            os.dup(dn)
            os.dup(dn)
            os.dup(dn)

            try:
                asyncio.run(main(args, pipe=w_pipe))
            except RuntimeError as re:
                print(str(re))
        else:
            time.sleep(1)
            ret = os.read(r_pipe, 50)
            os.close(r_pipe)
            if ret == b"OK\n":
                sys.exit(0)

            print("Returned: ", ret)
            sys.exit(1)
    else:
        asyncio.run(main(args))
