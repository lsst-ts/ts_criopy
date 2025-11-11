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

import numpy as np

from lsst.ts.xml.tables.m1m3 import ThermocoupleData

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QGuiApplication, QPainter, QPen, QPalette
from PySide6.QtWidgets import QStyleOptionGraphicsItem, QWidget

from ...gui import Colors
from .data_item import DataItem, DataItemState
from .gauge_scale import GaugeScale


class ScannerItem(DataItem):
    """Represent ScannerItem. This is an arteficial concept, linking
    thermocouples in the same location. Overwrites function to draw the
    QGraphicsItem. Hold values of all (up to 4, if cross-calibration
    thermocouples are at the cell) thermocouples at the same location.

    Attributes
    ----------
    tcs : `[ThermocoupleData]`
        List of thermocouples sharing the location. The list is sorted from
        topmost to bottommost thermocouples.

    Parameters
    ----------
    tcs : `[ThermocoupleData]`
        List of thermocuples sharing the location.
    state : `DataItemState`, optional
        Sensor state. Optional, defaults to DataItemState.INACTIVE.
    """

    def __init__(
        self, name: str, tcs: list[ThermocoupleData], state: DataItemState = DataItemState.INACTIVE
    ) -> None:
        super().__init__(state)
        self.tcs = tcs
        self.tcs.sort(key=lambda tc: (-tc.z_position, tc.name))
        self.name = name
        self._center = QPointF(tcs[0].x_position * 1000.0, -tcs[0].y_position * 1000.0)
        self._values: list[float] = [np.nan] * len(self.tcs)
        self._scale_factor = 25

    @property
    def data(self) -> list[float]:
        """Values associated with the scanner ([`float`]).

        Returns
        -------
        data : `[float]`
            Thermocouple temperatures.
        """
        return self._values

    @data.setter
    def data(self, data: list[float]) -> None:
        self._values = data
        self._data = np.mean(data)
        self.update()

    def set_tc(self, tc_name: str, value: float, state: DataItemState) -> None:
        """Set thermocouple current value.

        Parameters
        ----------
        tc_name : `str`
            Thermocouple name.
        value : `float`
            Thermocouple temperature in degrees C.
        state : `DataItemState`
            Thermocouple state.

        Raises
        ------
        RuntimeError
            If thermocuple with give name is not found.
        """
        for i, tc in enumerate(self.tcs):
            if tc.name == tc_name:
                self._values[i] = value
                self._data = np.mean(self._values)
                self._state = state
                return
        raise RuntimeError(f"Cannot find thermocouple {tc_name} in scanner {self.name}!")

    def set_color_scale(self, scale: GaugeScale) -> None:
        """Set actuator data display scale. This is used for setting display
        color and formatting values.

        Parameters
        ----------
        scale : `object`
            Scaling object. Should provide format_value() and get_brush()
            methods.
        """
        self._color_scale = scale
        self.update()

    def get_value(self) -> str:
        """Returns current value, string formated to scale.

        Returns
        -------
        format_value : `str`
           Current value formatted by the currently used color scale.
        """
        return self.format_value(self._data)

    def get_range(self, s_min: float, s_max: float) -> tuple[float, float]:
        for v in self._values:
            s_min = min(v, s_min)
            s_max = max(v, s_max)
        return s_min, s_max

    def get_indexed_value(self, index: int) -> str:
        """Returns formated value with given index.

        Parameters
        ----------
        index : `int`
            Thermocouple index.

        Returns
        -------
        format : `str`
            Formated returned thermocouple value.
        """
        return self.format_value(self._values[index])

    def format_value(self, v: float) -> str:
        """Returns formated value.

        Parameters
        ----------
        v : `float`
            Value to format. Type can vary depending on which value is being
            formated (boolean, float, int,..).

        Returns
        -------
        formatted_value : `str`
            Value formatted by the currently used color scale.
        """
        if self._color_scale is None:
            return f"{v:.03f}"
        return self._color_scale.format_value(v)

    def boundingRect(self) -> QRectF:
        h = len(self.tcs) + 1.2
        return QRectF(
            self._center.x() - 12 * self._scale_factor,
            self._center.y() - 2.5 * h * self._scale_factor,
            24 * self._scale_factor,
            5 * h * self._scale_factor,
        )

    def get_index(self, tc_name: str) -> int | None:
        """Returns index of thermocouple withj given name.

        Parameters
        ----------
        tc_name : `str`
            Thermocouple name.

        Returns
        -------
        index : `int | None`
            Thermocouple index. None if thermcouple with the given name is not
            present.
        """
        for i, tc in enumerate(self.tcs):
            if tc.name == tc_name:
                return i
        return None

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget) -> None:
        """Paint actuator. Overridden method of the QGraphicsItem class."""
        palette = QGuiApplication.palette()
        if not self.isEnabled():
            palette.setCurrentColorGroup(QPalette.Inactive)

        # basic font to write text
        font = painter.font()
        font.setPixelSize(4 * self._scale_factor)
        font.setItalic(True)

        br = self.boundingRect()
        rect = br.adjusted(self._scale_factor, 0.4 * self._scale_factor, -1 * self._scale_factor, 0)
        rect.setHeight(4.7 * self._scale_factor)

        def draw_scanner_id() -> None:
            painter.setFont(font)
            painter.drawText(rect, int(Qt.AlignBottom) | int(Qt.AlignHCenter), self.name)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        # paint grayed circle for scanners not providing the selected value
        if self._state == DataItemState.INACTIVE:
            painter.setPen(QPen(Qt.gray, self._scale_factor, Qt.DotLine))
            painter.drawRect(br)
            draw_scanner_id()
            return
        lineStyle = Qt.SolidLine if self.isEnabled() else Qt.DotLine
        # draw scanner with warning in red color
        if self._state == DataItemState.WARNING:
            color = Colors.ERROR
        elif self._color_scale is None:
            color = Colors.WARNING
        else:
            color = self._color_scale.get_brush(self._data)
        painter.setPen(QPen(color, self._scale_factor, lineStyle))
        painter.setBrush(Qt.white)
        # draw scanner, write value
        painter.drawRect(br)

        painter.setPen(palette.buttonText().color())

        draw_scanner_id()

        font.setItalic(False)
        font.setBold(False)
        painter.setFont(font)
        for i, tc in enumerate(self.tcs):
            rect.translate(0, 5 * self._scale_factor)
            vstr = f"{tc.location()} {self.get_indexed_value(i)}"
            if len(vstr) > 6:
                font.setPixelSize(3.5 * self._scale_factor)
            elif len(vstr) > 3:
                font.setPixelSize(4.5 * self._scale_factor)
            if self._color_scale is None:
                painter.setBrush(Colors.WARNING)
            else:
                painter.setBrush(self._color_scale.get_brush(self._values[i]))
            painter.drawRect(rect)
            painter.setPen(Qt.black)
            painter.drawText(rect, int(Qt.AlignTop) | int(Qt.AlignHCenter), vstr)
