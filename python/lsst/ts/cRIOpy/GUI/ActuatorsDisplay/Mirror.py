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

from PySide2.QtWidgets import QGraphicsScene

from .ForceActuator import ForceActuator


class Mirror(QGraphicsScene):
    """Graphics scene containing plot of the mirror surface with actuators.

    Actuator list is cleared with clear() method (inherited from
    QGraphicsScene). Force Actuators are added with addForceActuator() method.
    Force Actuator data should be updated with updateForceActuator() call.
    """

    def __init__(self):
        super().__init__()

    def setColorScale(self, scale):
        """Set display color scale. Provides getColor method, returning color
        to be used with value.

        Parameters
        ----------
        scale : `class`
            Data scale.
        """
        for a in self.items():
            a.setColorScale(scale)

    def addForceActuator(
        self, id, index, x, y, orientation, data, dataIndex, state, kind
    ):
        """Adds actuator to the list.

        Parameters
        ----------
        id : `int`
            Force Actuator ID. Actuators are matched by ID.
        index : `int`
            Force Actuator index (0-155).
        x : `float`
            Force Actuator X position (in mm).
        y :  `float`
            Force Actuator y position (in mm).
        orientation : `str`
            Secondary actuator orientation. Either NA, +Y, -Y, +X or -X.
        data : `float`
            Force Actuator value.
        dataIndex : `int`
            Force Actuator value index.
        state : `int`
            Force Actuator state. ForceActuator.STATE_INVALID,
            ForceActuator.STATE_VALID or ForceActuator.STATE_WARNING.
        kind : `FASelection`
            Force actuator kind - normal, selected or selected neighbour.
        """
        self.addItem(
            ForceActuator(id, index, x, y, orientation, data, dataIndex, state, kind)
        )

    def getForceActuator(self, id):
        """Returns actuator with given ID.

        Parameters
        ----------
        id : `int`
            Force Actuator ID.

        Returns
        -------
        `ForceActuator`
            Force Actuator with matched ID.

        Raises
        ------
        KeyError
            When actuator with given ID is not found.
        """
        try:
            return next(filter(lambda a: a.id == id, self.items()))
        except StopIteration:
            raise KeyError(f"Cannot find actuator with ID {id}")

    def updateForceActuator(self, id, data, state):
        """Updates actuator value and state.

        Parameters
        ----------
        id : `int`
            Force Actuator ID number.
        data : `float`
            Update actuator value.
        state : `int`
            Updated actuator state. ForceActuator.STATE_INVALID,
            ForceActuator.STATE_VALID, ForceActuator.STATE_WARNING.

        Raises
        ------
        KeyError
            If actuator with the given ID cannot be found.
        """
        self.getForceActuator(id).updateData(data, state)
