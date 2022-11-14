# This file is part of T&S cRIO Python library
#
# Developed for the LSST Telescope and Site Systems. This product includes
# software developed by the LSST Project (https://www.lsst.org). See the
# COPYRIGHT file at the top-level directory of this distribution for details of
# code ownership.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

from PySide2.QtCore import Qt

from lsst.ts.idl.enums.MTM1M3 import BumpTest

from .EnumScale import EnumScale
from ...GUI import Colors


class BumpTestScale(EnumScale):
    """Draws gauge with color scale for bump test progress."""

    def __init__(self):
        super().__init__(
            {
                BumpTest.NOTTESTED: ("Not Tested", Qt.gray),
                BumpTest.TESTINGPOSITIVE: ("Testing +", Qt.blue),
                BumpTest.TESTINGPOSITIVEWAIT: ("Testing + Wait", Qt.darkBlue),
                BumpTest.TESTINGNEGATIVE: ("Testing -", Qt.yellow),
                BumpTest.TESTINGNEGATIVEWAIT: ("Testing - Wait", Qt.darkYellow),
                BumpTest.PASSED: ("Passed", Colors.OK),
                BumpTest.FAILED: ("Failed", Colors.ERROR),
            }
        )
