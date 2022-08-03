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

from PySide2.QtCore import Signal, QEvent
from PySide2.QtWidgets import QGraphicsView
from . import Mirror, ForceActuator, FASelection
from ...M1M3FATable import (
    FATABLE,
    FATABLE_NEAR_NEIGHBOR_INDEX,
    FATABLE_FAR_NEIGHBOR_INDEX,
)


class MirrorView(QGraphicsView):
    """View on mirror populated by actuators."""

    selectionChanged = Signal(ForceActuator)
    """Signal raised when another actuator is selected by a mouse click.

    Parameters
    ----------
    Force Actuator
        Selected actuator.
    """

    def __init__(self):
        self._mirror = Mirror()
        super().__init__(self._mirror)
        self._selectedId = None

    def getForceActuator(self, id):
        """Returns ForceActuator object with given ID.

        Parameters
        ----------
        id : `int`
            ID of the force actuator to retrieve.

        Returns
        -------
        actuator : `ForceActuator`
            Force actuator object with give ID, or None if not found.
        """
        try:
            return self._mirror.getForceActuator(id)
        except KeyError:
            return None

    def changeEvent(self, event):
        if event.type() == QEvent.EnabledChange:
            for i in self._mirror.items():
                i.setEnabled(self.isEnabled())

    @property
    def selected(self):
        """Selected actuator or None if no actuator selected
        (ForceActuator)."""
        return self.getForceActuator(self._selectedId)

    def _setNeighbour(self, index, activate):
        for fids in FATABLE[self.selected.index][FATABLE_FAR_NEIGHBOR_INDEX]:
            if activate:
                if fids in FATABLE[self.selected.index][FATABLE_NEAR_NEIGHBOR_INDEX]:
                    self.getForceActuator(fids).setKind(FASelection.NEAR_NEIGHBOR)
                else:
                    self.getForceActuator(fids).setKind(FASelection.FAR_NEIGHBOR)
            else:
                self.getForceActuator(fids).setKind(FASelection.NORMAL)

    @selected.setter
    def selected(self, s):
        if self.selected is not None:
            self._setNeighbour(self.selected.index, False)
            self.selected.setKind(FASelection.NORMAL)
        if s is None:
            self._selectedId = None
            return None
        self._selectedId = s.id
        s.setKind(FASelection.SELECTED)
        self._setNeighbour(self.selected.index, True)
        self.selectionChanged.emit(s)

    def setColorScale(self, scale):
        """Sets scale used for color scaling.

        Parameters
        ----------
        scale : `class`
            New scale.
        """
        self._mirror.setColorScale(scale)

    def clear(self):
        """Removes all actuators from the view."""
        self._mirror.clear()

    def scaleHints(self):
        """Returns preferred scaling. Overloaded method."""
        s = min(self.width() / 8600, self.height() / 8600)
        return (s, s)

    def addForceActuator(self, id, index, x, y, orientation, data, dataIndex, state):
        """Adds actuator.

        Parameters
        ----------
        id : `int`
            Force Actuator ID. Actuators are matched by ID.
        index : `int`
            Actuator index (0-155).
        x : `float`
            Force Actuator X position (in mm).
        y :  `float`
            Force Actuator y position (in mm).
        orientation : `str`
            Secondary orientation. Either NA, +Y, -Y, +X or -X.
        data : `float`
            Force Actuator value.
        dataIndex : `int`
            Force Actuator value index.
        state : `int`
            Force Actuator state. ForceActuator.STATE_INVALID,
            ForceActuator.STATE_VALID or ForceActuator.STATE_WARNING.
        """
        self._mirror.addForceActuator(
            id,
            index,
            x,
            y,
            orientation,
            data,
            dataIndex,
            state,
            FASelection.SELECTED if id == self._selectedId else FASelection.NORMAL,
        )

    def updateForceActuator(self, id, data, state):
        """Update actuator value and state.

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
        self._mirror.updateForceActuator(id, data, state)
        if self._selectedId == id:
            self.selectionChanged.emit(self.selected if self.selected.active else None)

    def mousePressEvent(self, event):
        self.selected = self.itemAt(event.pos())
