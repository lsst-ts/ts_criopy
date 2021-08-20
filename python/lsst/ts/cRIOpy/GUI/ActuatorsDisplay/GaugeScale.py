# This file is part of M1M3 SS GUI.
#
# Developed for the LSST Telescope and Site Systems.
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

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QPainter, QColor, QBrush
from PySide2.QtWidgets import QWidget


class GaugeScale(QWidget):
    """Draws gauge with color scale."""

    def __init__(self):
        super().__init__()
        self._min = None
        self._max = None
        self.setMinimumSize(100, 100)
        self.setMaximumWidth(200)

    def setRange(self, min, max):
        """Set value range. Color is mapped between min and max values, using change in hue.

        Parameters
        ----------
        min : `float`
               Minimal data range.
        max : `float`
               Maximal data range.
        """
        self._min = min
        self._max = max
        self.update()

    def sizeHint(self):
        """Overridden method."""
        return QSize(100, 100)

    def formatValue(self, value):
        return f"{value:.2f}"

    def getColor(self, value):
        """Returns color for given value.

        Parameters
        ----------
        value : `float`
            Value for which color shall be returned.

        Returns
        -------
        color : `QColor`
            QColor representing the value on scale.
        """
        if self._min == self._max:
            return None
        # draw using value as index into possible colors in HSV model
        hue = 1 - (value - self._min) / (self._max - self._min)
        return self.getHueColor(hue)

    def getHueColor(self, hue):
        """Returns color from "hue" (0-1 range).

        Parameters
        ----------
        hue : `float`
            "Hue" value (in 0.0 - 1.0 range)

        Returns
        -------
        color : `QColor`
            Color for hue value.
        """
        return QColor.fromHsvF(hue * 0.7, min(1, 1.5 - hue), 1)

    def paintEvent(self, event):
        """Overridden method. Paint gauge as series of lines, and adds text labels."""
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        swidth = max(self.width() - 100, 20)
        sheight = self.height()
        if self._min == self._max:
            painter.setBrush(QBrush(Qt.red, Qt.DiagCrossPattern))
            painter.drawRect(0, 0, swidth, sheight)
            painter.setPen(Qt.black)
            if self._min is not None:
                painter.drawText(
                    0,
                    0,
                    self.width() - swidth,
                    sheight,
                    Qt.AlignCenter,
                    "{0:.2f}".format(self._min),
                )
            return

        for x in range(0, sheight):
            painter.setPen(self.getHueColor(x / sheight))
            painter.drawLine(0, x, swidth, x)

        painter.setPen(Qt.black)
        painter.drawText(
            0, 0, self.width() - swidth, 30, Qt.AlignCenter, self.formatValue(self._max)
        )
        painter.drawText(
            0,
            sheight - 30,
            self.width() - swidth,
            30,
            Qt.AlignCenter,
            self.formatValue(self._min),
        )
