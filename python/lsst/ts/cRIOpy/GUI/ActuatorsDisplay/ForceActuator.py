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

from PySide2.QtCore import QRect, Qt, QPointF
from PySide2.QtGui import QPen, QPainter, QColor, QBrush, QTransform
from PySide2.QtWidgets import QGraphicsItem


class ForceActuator(QGraphicsItem):
    """Combines graphical display of an actuator with its data. Record if an
    actuator is selected by a mouse click.

    Value sets (measured, rejected, calculated..) is managed by upper level
    classes.

    Force Actuator can be selected - then it is drawn with highlighting,
    showing it is the selected actuator.

    Parameters
    ----------
    id : `int`
        Force Actuator identification number. Starting with 101, the first
        number identified segment (1-4). The value ranges up to 443.
    x : `float`
        Force Actuator X coordinate (in mm).
    y : `float`
        Force Actuator Y coordinate (in mm).
    orientation : `str`
         Secondary orientation. Either NA, +Y, -Y, +X or -X.
    data : `float`
        Data associated with the actuator (actual force, calculated force, ..).
    dataIndex : `int`
        Index in value arrays. Points to selected actuator value.
    scale: `object`
        Object providing getColor(value) method.
    state : `int`
        Force Actuator state. 0 for inactive/unused, 1 for active OK, 2 for
        active warning.
    selected : `bool`
        True if the actuator is selected.
    """

    STATE_INACTIVE = 0
    """Force Actuator value is not relevant for the current display (`int`).
    """

    STATE_ACTIVE = 1
    """Force Actuator is active and healthy (`int`).
    """

    STATE_WARNING = 2
    """Force Actuator is active, but the value / actuator has some warning attached (`int`).
    """

    def __init__(self, id, x, y, orientation, data, dataIndex, state, selected):
        super().__init__()
        self.id = id
        # actuator position
        self._center = QPointF(x, y)
        self._orientation = orientation
        # actuator data
        self._data = data
        self.dataIndex = dataIndex
        self._selected = selected
        self._state = state
        # scale. Provides getColor(data) object, returning brush to fill data
        self._color_scale = None
        # scalign factor. The actuator default size is 20x20 units. As
        # actuators are placed on mirror, the size needs to be adjusted to show
        # properly actuator on display in e.g. mm (where X and Y ranges are
        # ~-4400 .. +4400).
        self._scale_factor = 25

    def updateData(self, data, state):
        """Updates actuator data.

        If new data differs from the current data, calls update() to force actuator redraw.

        Parameters
        ----------
        data : `float`
             New data associated with the actuator (actual force, calculated force, ..).
        state : `state`
             New actuator state value.
        """
        if self._data != data or self._state != state:
            self._data = data
            self._state = state
            self.update()

    def setSelected(self, selected):
        """Set actuator selection status."""
        self._selected = selected
        self.update()

    @property
    def data(self):
        """Value associated with the actuator (`float`)."""
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self.update()

    @property
    def warning(self):
        """If actuator is in warning state (`bool`)."""
        return self._state == self.STATE_WARNING

    @property
    def active(self):
        """If actuator is active (`bool`)."""
        return not (self._state == self.STATE_INACTIVE)

    def setColorScale(self, scale):
        """Set actuator data display scale. This is used for setting display color."""
        self._color_scale = scale
        self.update()

    def boundingRect(self):
        """Returns rectangle occupied by drawing. Overridden method."""
        return QRect(
            self._center.x() - 10 * self._scale_factor,
            self._center.y() - 10 * self._scale_factor,
            20 * self._scale_factor,
            20 * self._scale_factor,
        )

    def paint(self, painter, option, widget):
        """Paint actuator. Overridden method."""
        # if scale isn't set, don't draw
        if self._color_scale is None:
            return

        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        # paint grayed circle for actuators not providing the selected value
        if self._state == self.STATE_INACTIVE:
            painter.setPen(QPen(Qt.gray, self._scale_factor, Qt.DotLine))
            painter.drawEllipse(
                self._center, 10 * self._scale_factor, 10 * self._scale_factor
            )
            return
        # draw rectangle around selected actuator
        if self._selected:
            painter.setPen(QPen(Qt.black, self._scale_factor))
            painter.drawRect(self.boundingRect())
        else:
            painter.setPen(QPen(Qt.red, self._scale_factor))

        # draw selected actuator in red color
        if self._state == self.STATE_WARNING:
            painter.setBrush(Qt.red)
        else:
            color = self._color_scale.getColor(self._data)
            if color is None:
                brush = QBrush(Qt.red, Qt.DiagCrossPattern)
                brush.setTransform(
                    QTransform().scale(self._scale_factor / 3, self._scale_factor / 3)
                )
                painter.setBrush(brush)
            else:
                painter.setBrush(color)
        # draw actuator, write value
        painter.drawEllipse(
            self._center, 10 * self._scale_factor, 10 * self._scale_factor
        )

        painter.setPen(Qt.black)

        font = painter.font()
        font.setPixelSize(6.5 * self._scale_factor)
        font.setItalic(True)
        painter.setFont(font)
        painter.drawText(
            self._center.x() - 10 * self._scale_factor,
            self._center.y() - 10 * self._scale_factor,
            20 * self._scale_factor,
            10 * self._scale_factor,
            Qt.AlignBottom | Qt.AlignHCenter,
            str(self.id),
        )

        vstr = f"{self.data:.2f}"
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
            Qt.AlignTop | Qt.AlignHCenter,
            vstr,
        )
