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

import enum

from lsst.ts.xml.tables.m1m3 import ForceActuatorData
from PySide6.QtCore import QPointF, QRect, Qt
from PySide6.QtGui import QGuiApplication, QPainter, QPalette, QPen
from PySide6.QtWidgets import QStyleOptionGraphicsItem, QWidget

from ...gui import Colors
from .data_item import DataItem, DataItemState
from .gauge_scale import GaugeScale


class FASelection(enum.IntEnum):
    NORMAL = 1
    SELECTED = 2
    NEAR_NEIGHBOR = 3
    FAR_NEIGHBOR = 4


class ForceActuatorItem(DataItem):
    """Combines graphical display of an actuator with its data. Record if an
    actuator is selected by a mouse click.

    Value sets (measured, rejected, calculated..) is managed by upper level
    classes.

    Force Actuator can be selected - then it is drawn with highlighting,
    showing it is the selected actuator.

    Parameters
    ----------
    actuator : `ForceActuatorData`
        Row from force actuator table.
    data : `float`
        Data associated with the actuator (actual force, calculated force, ..).
    state : DataItemState
        Force Actuator state.
    kind : `FASelection`
        FA kind - normal, selected or neighbour of selected.
    """

    def __init__(
        self,
        actuator: ForceActuatorData,
        state: DataItemState = DataItemState.INACTIVE,
        kind: FASelection = FASelection.NORMAL,
    ):
        super().__init__(state)
        self.actuator = actuator
        # actuator position
        self._center = QPointF(
            actuator.x_position * 1000.0, -actuator.y_position * 1000.0
        )
        self._kind = kind
        # scale. Provides get_brush(data) object, returning brush to fill data
        self._color_scale: None | GaugeScale = None
        # scalign factor. The actuator default size is 20x20 units. As
        # actuators are placed on mirror, the size needs to be adjusted to show
        # properly actuator on display in e.g. mm (where X and Y ranges are
        # ~-4400 .. +4400).
        self._scale_factor = 25

    def setKind(self, kind: FASelection) -> None:
        """Set actuator kind (selection status).

        Parameters
        ----------
        kind : `FASelection`
            New selection status.
        """
        self._kind = kind
        try:
            self.update()
        except RuntimeError:
            pass

    @property
    def data(self) -> float:
        """Value associated with the actuator (`float`)."""
        assert self._data is not None
        return self._data

    @data.setter
    def data(self, data: float) -> None:
        self._data = data
        self.update()

    @property
    def warning(self) -> bool:
        """If actuator is in warning state (`bool`)."""
        return self._state == DataItemState.WARNING

    @property
    def active(self) -> bool:
        """If actuator is active (`bool`)."""
        return not (self._state == DataItemState.INACTIVE)

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

    def get_value(self) -> str:
        """Returns current value, string formated to scale.

        Returns
        -------
        format_value : `str`
           Current value formatted by the currently used color scale."""
        return self.format_value(self.data)

    def format_value(self, v: float) -> str:
        """Returns

        Parameters
        ----------
        v : `scalar`
            Value to format. Type can vary depending on which value is being
            formated (boolean, float, int,..).

        Returns
        -------
        formattedValue : `str`
            Value formatted by the currently used color scale.
        """
        if self._color_scale is None:
            return str(v)
        return self._color_scale.format_value(v)

    def paint(
        self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget
    ) -> None:
        """Paint actuator. Overridden method."""
        # if scale isn't set, don't draw
        if self._color_scale is None:
            return

        palette = QGuiApplication.palette()
        if not self.isEnabled():
            palette.setCurrentColorGroup(QPalette.Inactive)

        # basic font to write text
        font = painter.font()
        font.setPixelSize(6.5 * self._scale_factor)
        font.setItalic(True)

        def draw_actuator_id() -> None:
            painter.setFont(font)
            painter.drawText(
                self._center.x() - 10 * self._scale_factor,
                self._center.y() - 10 * self._scale_factor,
                20 * self._scale_factor,
                10 * self._scale_factor,
                int(Qt.AlignBottom) | int(Qt.AlignHCenter),
                str(self.actuator.actuator_id),
            )

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        # paint grayed circle for actuators not providing the selected value
        if self._state == DataItemState.INACTIVE:
            painter.setPen(QPen(Qt.gray, self._scale_factor, Qt.DotLine))
            painter.drawEllipse(
                self._center, 10 * self._scale_factor, 10 * self._scale_factor
            )
            draw_actuator_id()
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
        if self._state == DataItemState.WARNING:
            painter.setBrush(Colors.ERROR)
        else:
            assert self._data is not None
            brush = self._color_scale.get_brush(self._data)
            painter.setBrush(brush)
        # draw actuator, write value
        painter.drawEllipse(
            self._center, 10 * self._scale_factor, 10 * self._scale_factor
        )

        painter.setPen(palette.buttonText().color())

        draw_actuator_id()

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
