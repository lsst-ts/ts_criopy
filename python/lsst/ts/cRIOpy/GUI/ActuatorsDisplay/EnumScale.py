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
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QWidget


class EnumScale(QWidget):
    """Draws gauge with color scale for enumeration (on/off, bump test
    progress,..) values. Subclasses shall implement getValue() and getColor()
    methods.

    Parameters
    ----------
    levels : `{value : (name, color)}`
    """

    def __init__(self, levels):
        super().__init__()
        self.setMinimumSize(100, 100)
        self.setMaximumWidth(200)
        self._levels = levels

    def sizeHint(self):
        """Overridden method."""
        return QSize(100, 100)

    def getLabels(self):
        """Returns array of labels scale represents.

        Returns
        -------
        labels : `[..]`
            Array (in order labels shall be pletted) with all supported values.
        """
        return self._levels.keys()

    def getValue(self, value):
        return self._levels[value][0]

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
        return self._levels[value][1]

    def paintEvent(self, event):
        """Overridden method. Paint gauge as series of lines, and adds text labels."""
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        swidth = self.width()
        sheight = self.height()

        labels = list(self.getLabels())
        l_labels = len(labels)

        t_height = max(5, (sheight / l_labels) / 5)
        x_offset = 5

        def box(y, value):
            painter.setBrush(self.getColor(value))
            painter.drawRect(0, y, swidth, sheight / l_labels)

            painter.setBrush(Qt.white)
            painter.setPen(Qt.black)
            painter.drawRect(
                x_offset, y + 2 * t_height, swidth - 2 * x_offset, t_height
            )

            painter.drawText(
                x_offset,
                y + 2 * t_height,
                swidth - 2 * x_offset,
                t_height,
                Qt.AlignCenter,
                self.getValue(value),
            )

        for i in range(l_labels):
            box(i * sheight / l_labels, labels[i])
