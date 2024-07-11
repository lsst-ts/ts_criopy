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

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPaintEvent
from PySide6.QtWidgets import QWidget


class GaugeScale(QWidget):
    """Draws gauge with color scale.

    Parameters
    ----------
    fmt: `str`


    """

    def __init__(self, fmt: str = ".02f"):
        super().__init__()
        self._min: float = 1
        self._max: float = 1
        self._fmt = fmt
        self.setMinimumSize(100, 100)
        self.setMaximumWidth(200)

    def setRange(self, min_range: float, max_range: float) -> None:
        """Set value range. Color is mapped between min and max values, using
        change in hue.

        Parameters
        ----------
        min_range : `float`
               Minimal data range.
        max_range : `float`
               Maximal data range.
        """
        self._min = min_range
        self._max = max_range
        self.update()

    def sizeHint(self) -> None:
        """Overridden method."""
        return QSize(100, 100)

    def formatValue(self, value: float) -> str:
        return f"{value:{self._fmt}}"

    def getColor(self, value: float) -> QColor | None:
        """Returns color for given value.

        Parameters
        ----------
        value : `float`
            Value for which color shall be returned.

        Returns
        -------
        color : `QColor`
            QColor representing the value on scale. None - use default color.
        """
        if self._min == self._max:
            return None
        # draw using value as index into possible colors in HSV model
        hue = 1 - (value - self._min) / (self._max - self._min)
        return self.getHueColor(hue)

    def getHueColor(self, hue: float) -> QColor:
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

    def paintEvent(self, event: QPaintEvent) -> None:
        """Overridden method. Paint gauge as series of lines, and adds text
        labels."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
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
                    int(Qt.AlignCenter),
                    self.formatValue(self._min),
                )
            return

        for x in range(0, sheight):
            painter.setPen(self.getHueColor(x / sheight))
            painter.drawLine(0, x, swidth, x)

        painter.setPen(Qt.black)
        painter.drawText(
            0,
            0,
            self.width() - swidth,
            30,
            int(Qt.AlignCenter),
            self.formatValue(self._max),
        )
        painter.drawText(
            0,
            sheight / 2.0 - 30,
            self.width() - swidth,
            30,
            int(Qt.AlignCenter),
            self.formatValue((self._max + self._min) / 2.0),
        )
        painter.drawText(
            0,
            sheight - 30,
            self.width() - swidth,
            30,
            int(Qt.AlignCenter),
            self.formatValue(self._min),
        )
