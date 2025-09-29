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

import typing

import numpy as np
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QBrush, QGuiApplication, QPainter, QPaintEvent, QPalette
from PySide6.QtWidgets import QWidget


class EnumScale(QWidget):
    """Draws gauge with color scale for enumeration (on/off, bump test
    progress,..) values. Subclasses shall implement format_value() and
    get_brush() methods.

    Parameters
    ----------
    levels : `{value : (name, color)}`
    """

    def __init__(self, levels: dict[typing.Any, tuple[str, QBrush]]):
        super().__init__()
        self.setMinimumSize(100, 100)
        self.setMaximumWidth(200)
        self._levels = levels

    def sizeHint(self) -> None:
        """Overridden method."""
        return QSize(100, 100)

    def getLabels(self) -> list[typing.Any]:
        """Returns array of labels scale represents.

        Returns
        -------
        labels : `[..]`
            Array (in order labels shall be pletted) with all supported values.
        """
        return list(self._levels.keys())

    def format_value(self, value: int) -> str:
        try:
            return self._levels[value][0]
        except KeyError:
            return str(value)

    def get_brush(self, value: typing.Any) -> QBrush:
        """Returns color value.

        Parameters
        ----------
        value : `Any`
            Value for which color shall be returned.

        Returns
        -------
        brush : QBrush
            Brush for value.
        """
        if np.isnan(value):
            return QBrush(Qt.gray, Qt.Dense5Pattern)

        return self._levels[value][1]

    def paintEvent(self, event: QPaintEvent) -> None:
        """Overridden method. Paint gauge as series of lines, and adds text
        labels."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        palette = QGuiApplication.palette()
        palette.setCurrentColorGroup(
            QPalette.Active if self.isEnabled() else QPalette.Inactive
        )

        swidth = self.width()
        sheight = self.height()

        labels = list(self.getLabels())
        l_labels = len(labels)

        t_height = max(5, (sheight / l_labels) / 5)
        x_offset = 5

        def box(y: float, value: typing.Any) -> None:
            painter.setBrush(self.get_brush(value))
            painter.drawRect(0, y, swidth, sheight / l_labels)

            painter.setBrush(palette.window())
            painter.setPen(palette.windowText().color())
            painter.drawRect(
                x_offset, y + 2 * t_height, swidth - 2 * x_offset, t_height
            )

            painter.drawText(
                x_offset,
                y + 2 * t_height,
                swidth - 2 * x_offset,
                t_height,
                int(Qt.AlignCenter),
                self.format_value(value),
            )

        for i in range(l_labels):
            box(i * sheight / l_labels, labels[i])
