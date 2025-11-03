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
from PySide6.QtGui import QGuiApplication, QPainter, QPen
from PySide6.QtWidgets import QStyleOptionGraphicsItem, QWidget

from .data_item import DataItem, DataItemState
from .gauge_scale import GaugeScale


class FCUItem(DataItem):
    """Combines graphical display of an FCU with its data. Record if an
    actuator is selected by a mouse click.

    Value sets (measured, rejected, calculated..) is managed by upper level
    classes.

    Force Actuator can be selected - then it is drawn with highlighting,
    showing it is the selected actuator.

    Parameters
    ----------
    fcu : FCUData
        Row from force actuator table.
    state : DataItemState
        Force Actuator state. 0 for inactive/unused, 1 for active OK, 2 for
        active warning.
    """

    def __init__(self, fcu: FCUData, state: DataItemState):
        super().__init__(state)
        self.fcu = fcu
        # actuator position
        self._center = QPointF(fcu.x_position * 1000.0, -fcu.y_position * 1000.0)
        # scale. Provides get_brush(data) object, returning brush to fill data
        # scalign factor. The actuator default size is 20x20 units. As
        # actuators are placed on mirror, the size needs to be adjusted to show
        # properly actuator on display in e.g. mm (where X and Y ranges are
        # ~-4400 .. +4400).
        self._scale_factor = 25

    def set_color_scale(self, scale: GaugeScale) -> None:
        """Set actuator data display scale. This is used for setting display
        color and formatting values.

        Parameters
        ----------
        scale : `object`
            Scaling object. Should provide format_value() and get_brush()
            methods."""
        self._color_scale = scale
        self.update()

    def boundingRect(self) -> QRect:
        """Returns rectangle occupied by drawing. Overridden method."""
        return QRect(
            self._center.x() - 10 * self._scale_factor,
            self._center.y() - 10 * self._scale_factor,
            20 * self._scale_factor,
            20 * self._scale_factor,
        )

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        """Paint actuator. Overridden method."""
        assert self._color_scale is not None

        palette = QGuiApplication.palette()
        if not self.isEnabled():
            palette.setCurrentColorGroup(palette.Inactive)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        lineStyle = Qt.SolidLine if self.isEnabled() else Qt.DotLine
        painter.setPen(QPen(Qt.red, self._scale_factor, lineStyle))

        brush = self._color_scale.get_brush(self._data)
        painter.setBrush(brush)

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

        vstr = self.get_value()
        if len(vstr) > 6:
            font.setPixelSize(3.5 * self._scale_factor)
        elif len(vstr) > 3:
            font.setPixelSize(4.5 * self._scale_factor)

        font.setItalic(False)
        font.setBold(True)
        painter.setFont(font)
        # draw value
        painter.drawText(
            self._center.x() - 10 * self._scale_factor,
            self._center.y(),
            20 * self._scale_factor,
            10 * self._scale_factor,
            int(Qt.AlignTop) | int(Qt.AlignHCenter),
            vstr,
        )
