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

from PySide2.QtCore import QRect, Qt, QPointF
from PySide2.QtGui import QPen, QPainter, QBrush, QTransform, QGuiApplication
from PySide2.QtWidgets import QGraphicsItem

import enum


class FASelection(enum.IntEnum):
    NORMAL = 1
    SELECTED = 2
    NEAR_NEIGHBOR = 3
    FAR_NEIGHBOR = 4


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
    index : `int`
        Force actuator index (0-155).
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
    """Force Actuator is active, but the value / actuator has some warning attached (`int`).
    """

    def __init__(self, id, index, x, y, orientation, data, dataIndex, state, kind):
        super().__init__()
        self.id = id
        self.index = index
        # actuator position
        self._center = QPointF(x, y)
        self._orientation = orientation
        # actuator data
        self._data = data
        self.dataIndex = dataIndex
        self._state = state
        self._kind = kind
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

    def setKind(self, kind):
        """Set actuator kind."""
        self._kind = kind
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

    def getValue(self):
        """Returns current value, string formated to scale."""
        return self.formatValue(self.data)

    def formatValue(self, v):
        return self._color_scale.formatValue(v)

    def paint(self, painter, option, widget):
        """Paint actuator. Overridden method."""
        # if scale isn't set, don't draw
        if self._color_scale is None:
            return

        palette = QGuiApplication.palette()
        if not self.isEnabled():
            palette.setCurrentColorGroup(palette.Inactive)

        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        # paint grayed circle for actuators not providing the selected value
        if self._state == self.STATE_INACTIVE:
            painter.setPen(QPen(Qt.gray, self._scale_factor, Qt.DotLine))
            painter.drawEllipse(
                self._center, 10 * self._scale_factor, 10 * self._scale_factor
            )
            return
        lineStyle = Qt.SolidLine if self.isEnabled() else Qt.DotLine
        # draw rectangle around selected actuator
        if self._kind == FASelection.SELECTED:
            painter.setPen(QPen(Qt.black, self._scale_factor, lineStyle))
            painter.drawRect(self.boundingRect())
        elif self._kind == FASelection.NEAR_NEIGHBOR:
            painter.setPen(QPen(Qt.darkBlue, self._scale_factor * 2, lineStyle))
        elif self._kind == FASelection.FAR_NEIGHBOR:
            painter.setPen(QPen(Qt.blue, self._scale_factor * 2, lineStyle))
        else:
            painter.setPen(QPen(Qt.red, self._scale_factor, lineStyle))

        # draw actuator with warning in red color
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
                painter.setBrush(
                    QBrush(
                        color, Qt.SolidPattern if self.isEnabled() else Qt.Dense4Pattern
                    )
                )
        # draw actuator, write value
        painter.drawEllipse(
            self._center, 10 * self._scale_factor, 10 * self._scale_factor
        )

        painter.setPen(palette.color(palette.ButtonText))

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

        vstr = self.getValue()
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
