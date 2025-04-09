#!/usr/bin/env python3

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

import argparse
import asyncio
import importlib
import logging
import os
import signal
import sys
import time
import typing

from . import ExitErrorCodes, parseDuration
from .vms import VMS_DEVICES, Collector

try:
    importlib.import_module("h5py")
    has_h5py = True
except ModuleNotFoundError:
    has_h5py = False


parser = argparse.ArgumentParser(
    description="Save VMS data to a file, either HDF5 or CSV.",
    epilog=(
        "Data are read as they arrive in DDS messages, matched by timestamps. "
        "Only complete (from all accelerometers the device provides) records "
        "are stored. Allows either single or multiple devices recording. On "
        "Linux it can be launched as daemon, running on background. "
        "Recorded data can be analysed offline with VMSGUI."
    ),
)
parser.add_argument(
    "devices",
    type=str,
    nargs="+",
    help="name or index of CSC",
    choices=VMS_DEVICES,
)
parser.add_argument(
    "-5",
    dest="h5py",
    action="store_true",
    help=(
        "save into HDF 5. Requires h5py (pip install h5py). Save to CSV if not"
        " provided."
    ),
)
parser.add_argument(
    "--chunk-size",
    dest="chunk_size",
    default=5000,
    type=int,
    help=(
        "receiving chunk size. After receiving this number of records, data are"
        " added to HDF5 file (and the file flushed to disk). Has no effect if"
        " CSV (default) format is used. Defaults to 5000."
    ),
)
parser.add_argument(
    "-d", dest="debug", default=0, action="count", help="increase debug level"
)
parser.add_argument(
    "--header",
    dest="header",
    action="store_true",
    help="adds header with column names",
)
parser.add_argument("-p", dest="pidfile", action="store", help="PID file location")
parser.add_argument(
    "-s",
    type=int,
    dest="size",
    default=-1,
    help=(
        "number of records to save in a file. Default to 86400 seconds"
        " (assuming --rotate isn't specified)"
    ),
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
    help=(
        "template used to construct output file path. Default to"
        " ${name}_%%Y-%%m-%%dT%%H:%%M:%%S.${ext}. strftime (%%) expansions are"
        " performed (see man strftime for details, %%Y for full (4 digit) year,"
        " %%m for calendar month,..) together with custom ${xx} expansion"
        " (${name} for device name, ${ext} for extension - hd5, cvs or cvs.gz)."
        " Directories in expanded file path are created as needed."
    ),
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

if sys.platform == "linux":
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
    help=(
        "rotate on given interval. Default to not rotate - rotate on reaching"
        " size number of entries. Can be used only with HDF5 output."
    ),
)
parser.add_argument(
    "--rotate-offset",
    action="store",
    dest="rotate_offset",
    default=0,
    type=parseDuration,
    help="rotate at give offset from rotate interval (--rotate argument)",
)


async def main(args: typing.Any, pipe: typing.Any = None) -> None:
    logger = logging.getLogger("VMSlogger")
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
            sys.exit(ExitErrorCodes.VMSLOGGER_CANNOT_CHDIR)

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

    tasks: list[asyncio.Task] = []
    collectors = []

    def cancel_all(signum: int, frame: typing.Any) -> None:
        logger.info(f"Canceling after {signum}")
        for t in tasks:
            t.cancel()

    signals = [signal.SIGINT, signal.SIGTERM]
    if sys.platform == "linux":
        signals += [signal.SIGHUP]

    for signum in signals:
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
            sys.exit(ExitErrorCodes.VMSLOGGER_MISSING_H5PY)
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
            VMS_DEVICES.index(d),
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


def run() -> None:
    args = parser.parse_args()
    if sys.platform == "linux" and args.daemon:
        r_pipe, w_pipe = os.pipe2(os.O_NONBLOCK)  # type: ignore
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
                sys.exit(os.EX_OK)

            print("Returned: ", ret)
            sys.exit(ExitErrorCodes.VMSLOGGER_SUBPROCESS_STARTUP)
    else:
        asyncio.run(main(args))
