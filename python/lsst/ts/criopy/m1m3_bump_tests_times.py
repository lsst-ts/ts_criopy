#!/usr/bin/env python3

# This file is part of ts_criopy
#
# Developed for the LSST Telescope and Site.
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

import argparse
import asyncio
import logging

from astropy.time import Time, TimeDelta
from lsst.ts.criopy.m1m3 import BumpTestTimes
from lsst.ts.xml.tables.m1m3 import force_actuator_from_id
from lsst_efd_client import EfdClient


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""

    now = Time.now()

    parser = argparse.ArgumentParser(description="Queries bump test status.")
    parser.add_argument(
        "start_time",
        type=Time,
        default=now - TimeDelta(7, format="jd"),
        nargs="?",
        help="Start time in a valid format: 'YYYY-MM-DD HH:MM:SSZ'",
    )
    parser.add_argument(
        "end_time",
        type=Time,
        default=now,
        nargs="?",
        help="End time in a valid format: 'YYYY-MM-DD HH:MM:SSZ'",
    )
    parser.add_argument(
        "actuators",
        default=[],
        action="append",
        help="Actuators to query. If empty, list all actuators.",
    )
    parser.add_argument(
        "--efd",
        default="usdf_efd",
        help="EFD name. Defaults to usdf_efd",
    )
    parser.add_argument(
        "-d",
        default=False,
        action="store_true",
        help="Print debug messages",
    )

    return parser.parse_args()


async def run_loop() -> None:
    args = parse_arguments()

    level = logging.INFO

    if args.d:
        level = logging.DEBUG

    logging.basicConfig(format="%(asctime)s %(message)s", level=level)

    btt = BumpTestTimes(EfdClient(args.efd))

    logging.info(f"Looking for bump test times in {args.start_time} to {args.end_time}")

    for aid in [int(a) for a in args.actuators]:
        actuator = force_actuator_from_id(aid)
        logging.info(f"** Actuator {aid} type: {actuator.actuator_type}")
        primary, secondary = await btt.find_times(aid, args.start_time, args.end_time)
        print("Primary bump tests")
        for bump in primary:
            print(bump[0].isot, bump[1].isot)

        print("===================")
        print("Secondary bump tests")
        for bump in secondary:
            print(bump[0].isot, bump[1].isot)


def run() -> None:
    asyncio.run(run_loop())
