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

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QPainter, QPaintEvent

from .gauge_scale import GaugeScale


class IntegerScale(GaugeScale):
    """Draws gauge with integer range scale."""

    def __init__(self) -> None:
        super().__init__(".0f")

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
                    self.format_value(self._min),
                )
            return

        for x in range(0, sheight):
            painter.setPen(self.get_color(round(x / sheight)))
            painter.drawLine(0, x, swidth, x)

        painter.setPen(Qt.black)
        painter.drawText(
            0,
            0,
            self.width() - swidth,
            30,
            int(Qt.AlignCenter),
            self.format_value(self._max),
        )
        painter.drawText(
            0,
            sheight / 2.0 - 30,
            self.width() - swidth,
            30,
            int(Qt.AlignCenter),
            self.format_value((self._max + self._min) / 2.0),
        )
        painter.drawText(
            0,
            sheight - 30,
            self.width() - swidth,
            30,
            int(Qt.AlignCenter),
            self.format_value(self._min),
        )
