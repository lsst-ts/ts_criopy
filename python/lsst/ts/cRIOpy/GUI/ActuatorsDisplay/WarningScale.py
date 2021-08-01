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

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QPainter, QColor, QBrush
from PySide2.QtWidgets import QWidget

from .BipolarScale import BipolarScale


class WarningScale(BipolarScale):
    """Draws gauge with color scale for boolean (on/off) values."""

    def __init__(self):
        super().__init__(False)

    def getValue(self, value):
        if value:
            return "Warning\nError"
        return "OK"

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
        if value:
            return Qt.red
        return Qt.green
