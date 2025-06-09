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

__all__ = ["DataItem", "DataItemState"]

import math
from enum import Enum

from PySide6.QtWidgets import QGraphicsItem

from .gauge_scale import GaugeScale


class DataItemState(Enum):
    INACTIVE = 0
    """Force Actuator value is not relevant for the current display (`int`).
    """
    ACTIVE = 1
    """Force Actuator is active and healthy (`int`).
    """
    WARNING = 2
    """Force Actuator is active, but the value / actuator has some warning
    attached (`int`).
    """


class DataItem(QGraphicsItem):
    def __init__(self, state: DataItemState):
        super().__init__()

        # actuator data
        self._data: float = math.nan
        self._state = state
        self._color_scale: None | GaugeScale = None

    def update_data(self, data: float, state: DataItemState) -> None:
        """Updates actuator data.

        If new data differs from the current data, calls update() to force
        actuator redraw.

        Parameters
        ----------
        data : `float`
             New data associated with the actuator (actual force, calculated
             force, ..).
        state : `state`
             New actuator state value.
        """
        if self._data != data or self._state != state:
            self._data = data
            self._state = state
            self.update()

    def get_value(self) -> str:
        """Returns current value, string formated to scale.

        Returns
        -------
        format_value : `str`
           Current value formatted by the currently used color scale."""
        assert self._data is not None
        return self.format_value(self._data)

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
