# This file is part of cRIO GUI.
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

# For an explanation why these next lines are so complicated, see
# https://confluence.lsstcorp.org/pages/viewpage.action?spaceKey=LTS&title=Enabling+Mypy+in+Pytest

__all__ = ["ExitErrorCodes"]

from enum import IntEnum, auto


class ExitErrorCodes(IntEnum):
    """
    Application exit status codes.
    """

    ASYNCIO_LOOP_NOT_RUNNING = auto()
    SAL_NOT_SETUP = auto()
    VMSLOGGER_CANNOT_CHDIR = auto()
    VMSLOGGER_MISSING_H5PY = auto()
    VMSLOGGER_SUBPROCESS_STARTUP = auto()
    WRONG_COMMAND_LINE_ARGUMENTS = auto()
    WRONG_QT_API = auto()
