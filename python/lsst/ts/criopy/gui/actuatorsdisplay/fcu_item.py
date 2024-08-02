# This file is part of M1M3 GUI.
#
# Developed for the LSST Telescope and Site Systems.  This product includes
# software developed by the LSST Project (https://www.lsst.org).  See the
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
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

from lsst.ts.xml.tables.m1m3 import FCUData
from PySide6.QtCore import QPointF, QRect, Qt
from PySide6.QtGui import QBrush, QGuiApplication, QPainter, QPen
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget


class FCUItem(QGraphicsItem):
    """Combines graphical display of an FCU with its data. Record if an
    actuator is selected by a mouse click.

    Value sets (measured, rejected, calculated..) is managed by upper level
    classes.

    Force Actuator can be selected - then it is drawn with highlighting,
    showing it is the selected actuator.

    Parameters
    ----------
    fcu : `FCUData`
        Row from force actuator table.
    data : `float`
        Data associated with the actuator (actual force, calculated force, ..).
    data_index : `int`
        Index in value arrays. Points to selected actuator value.
    scale: `object`
        Object providing getColor(value) method.
    state : `int`
        Force Actuator state. 0 for inactive/unused, 1 for active OK, 2 for
        active warning.
    kind : `FASelection`
        FA kind - normal, selected or neighbour of selected.
    """

    STATE_INACTIVE = 0
    """Force Actuator value is not relevant for the current display (`int`).
    """

    STATE_ACTIVE = 1
    """Force Actuator is active and healthy (`int`).
    """

    STATE_WARNING = 2
    """Force Actuator is active, but the value / actuator has some warning
    attached (`int`).
    """

    def __init__(self, fcu: FCUData):
        super().__init__()
        self.fcu = fcu
        # actuator position
        self._center = QPointF(fcu.x_position * 1000.0, -fcu.y_position * 1000.0)
        # scalign factor. The actuator default size is 20x20 units. As
        # actuators are placed on mirror, the size needs to be adjusted to show
        # properly actuator on display in e.g. mm (where X and Y ranges are
        # ~-4400 .. +4400).
        self._scale_factor = 25

    def boundingRect(self) -> QRect:
        """Returns rectangle occupied by drawing. Overridden method."""
        return QRect(
            self._center.x() - 10 * self._scale_factor,
            self._center.y() - 10 * self._scale_factor,
            20 * self._scale_factor,
            20 * self._scale_factor,
        )

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget
    ) -> None:
        """Paint actuator. Overridden method."""

        palette = QGuiApplication.palette()
        if not self.isEnabled():
            palette.setCurrentColorGroup(palette.Inactive)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        lineStyle = Qt.SolidLine if self.isEnabled() else Qt.DotLine
        painter.setPen(QPen(Qt.red, self._scale_factor, lineStyle))

        # color = self._color_scale.getColor(self._data)
        color = Qt.green
        painter.setBrush(
            QBrush(
                color,
                Qt.SolidPattern if self.isEnabled() else Qt.Dense4Pattern,
            )
        )
        # draw actuator, write value
        painter.drawRect(
            self._center.x() - 8 * self._scale_factor,
            self._center.y() - 8 * self._scale_factor,
            16 * self._scale_factor,
            16 * self._scale_factor,
        )

        painter.setPen(palette.buttonText().color())

        font = painter.font()
        font.setPixelSize(6.5 * self._scale_factor)
        font.setItalic(True)
        painter.setFont(font)
        painter.drawText(
            self._center.x() - 10 * self._scale_factor,
            self._center.y() - 10 * self._scale_factor,
            20 * self._scale_factor,
            10 * self._scale_factor,
            int(Qt.AlignBottom) | int(Qt.AlignHCenter),
            str(self.fcu.name),
        )
