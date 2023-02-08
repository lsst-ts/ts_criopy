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

__all__ = ["parseDuration"]

import argparse


def parseDuration(duration):
    """Accept string depicting duration.

    Numbers can be suffixed with character, denomination their lengths.

    Length denominators
    -------------------
    D : days (86400 seconds)
    h : hours (3600 seconds)
    m : minutesa (60 seconds)
    s : seconds (1 second)

    Examples
    --------
    '1D 1m' = 86460 seconds
    '1h 1m 30s' = 3690 seconds

    Parameters
    ----------
    duration : `str`
        Duration string. Numbers with know suffixed. Non-sufficed number will
        be treated as seconds.

    Returns
    -------
    seconds : `int`
        Number of seconds in string.
    """
    muls = {"D": 86400, "h": 3600, "m": 60, "s": 1}
    ret = 0
    current = 0
    for s in duration:
        if "0" <= s <= "9":
            current = current * 10 + int(s)
        elif s == " ":
            pass
        else:
            try:
                ret += current * muls[s]
                current = 0
            except KeyError:
                raise argparse.ArgumentTypeError(f"Unknown suffix: {s}")
    return ret + current
