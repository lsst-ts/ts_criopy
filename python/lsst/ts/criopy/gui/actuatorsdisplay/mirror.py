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

import typing

from PySide2.QtWidgets import QGraphicsScene

from ...m1m3_fa_table import ForceActuatorData
from .force_actuator_item import FASelection, ForceActuatorItem
from .gauge_scale import GaugeScale


class Mirror(QGraphicsScene):
    """Graphics scene containing plot of the mirror surface with actuators.

    Actuator list is cleared with clear() method (inherited from
    QGraphicsScene). Force Actuators are added with addForceActuator() method.
    Force Actuator data should be updated with updateForceActuator() call.
    """

    def __init__(self) -> None:
        super().__init__()

    def set_color_scale(self, scale: GaugeScale) -> None:
        """Set display color scale. Provides getColor method, returning color
        to be used with value.

        Parameters
        ----------
        scale : `GaugeScale`
            Data scale.
        """
        for a in self.items():
            a.set_color_scale(scale)

    def addForceActuator(
        self,
        actuator: ForceActuatorData,
        data: typing.Any,
        data_index: int | None,
        state: int,
        kind: FASelection,
    ) -> None:
        """Adds actuator to the list.

        Parameters
        ----------
        actuator : `ForceActuatorData`
            Row from m1m3_fa_table.
        data : `float`
            Force Actuator value.
        data_index : `int`
            Force Actuator value index.
        state : `int`
            Force Actuator state. ForceActuatorItem.STATE_INVALID,
            ForceActuatorItem.STATE_VALID or ForceActuatorItem.STATE_WARNING.
        kind : `FASelection`
            Force actuator kind - normal, selected or selected neighbour.
        """
        self.addItem(ForceActuatorItem(actuator, data, data_index, state, kind))

    def getForceActuator(self, actuator_id: int) -> ForceActuatorItem:
        """Returns actuator with given ID.

        Parameters
        ----------
        actuator_id : `int`
            Force Actuator ID.

        Returns
        -------
        `ForceActuatorItem`
            Force Actuator with matched ID.

        Raises
        ------
        KeyError
            When actuator with given ID is not found.
        """
        for item in self.items():
            if (
                isinstance(item, ForceActuatorItem)
                and item.actuator.actuator_id == actuator_id
            ):
                return item
        raise KeyError(f"Cannot find actuator with ID {actuator_id}")

    def updateForceActuator(
        self, actuator_id: int, data: typing.Any, state: int
    ) -> None:
        """Updates actuator value and state.

        Parameters
        ----------
        actuator_id : `int`
            Force Actuator ID number.
        data : `Any`
            Update actuator value.
        state : `int`
            Updated actuator state. ForceActuatorItem.STATE_INVALID,
            ForceActuatorItem.STATE_VALID, ForceActuatorItem.STATE_WARNING.

        Raises
        ------
        KeyError
            If actuator with the given ID cannot be found.
        """
        self.getForceActuator(actuator_id).updateData(data, state)
