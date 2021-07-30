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


class OnOffScale(QWidget):
    """Draws gauge with color scale for boolean (on/off) values."""

    def __init__(self):
        super().__init__()
        self.setMinimumSize(100, 100)
        self.setMaximumWidth(200)

    def sizeHint(self):
        """Overridden method."""
        return QSize(100, 100)

    def getValue(self, value):
        if value:
            return "On"
        return "Off"

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
            return Qt.green
        return Qt.red

    def paintEvent(self, event):
        """Overridden method. Paint gauge as series of lines, and adds text labels."""
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        swidth = max(self.width() - 100, 20)
        sheight = self.height()

        def box(y, value):
            painter.setBrush(self.getColor(value))
            painter.drawRect(0, y, swidth, sheight / 2)
            painter.setPen(Qt.black)
            painter.drawText(
                0,
                y,
                self.width() - swidth,
                sheight / 2,
                Qt.AlignCenter,
                self.getValue(value),
            )

        box(0, True)
        box(sheight / 2, False)
