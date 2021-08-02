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

from .EnumScale import EnumScale

from lsst.ts.idl.enums import MTM1M3


class BumpTestScale(EnumScale):
    """Draws gauge with color scale for bump test progress."""

    def __init__(self):
        super().__init__()

    def getValue(self, value):
        strs = {
            MTM1M3.NOTTESTED: "Not Tested",
            MTM1M3.TESTINGPOSITIVE: "Testing +",
            MTM1M3.TESTINGPOSITIVEWAIT: "Testing + Wait",
            MTM1M3.TESTINGNEGATIVE: "Testing -",
            MTM1M3.TESTINGNEGATIVEWAIT: "Testing - Wait",
            MTM1M3.PASSED: "Passed",
            MTM1M3.FAILED: "Failed",
        }
        try:
            return strs[value]
        except KeyError:
            return f"Unknown {value}"

    def getColor(self, value):
        """Returns color value.

        Parameters
        ----------
        value : `bool`
            Value for which color shall be returned. True is assumed to be good (=green).

        Returns
        -------
        color : `QColor`
            Color for value.
        """
        cols = {
            MTM1M3.NOTTESTED: Qt.gray,
            MTM1M3.TESTINGPOSITIVE: Qt.blue,
            MTM1M3.TESTINGPOSITIVEWAIT: Qt.darkBlue,
            MTM1M3.TESTINGNEGATIVE: Qt.yellow,
            MTM1M3.TESTINGNEGATIVEWAIT: Qt.darkYellow,
            MTM1M3.PASSED: Qt.green,
            MTM1M3.FAILED: Qt.red,
        }
        try:
            return cols[value]
        except KeyError:
            return Qt.darkRed
