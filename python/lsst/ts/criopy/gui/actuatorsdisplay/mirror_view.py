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


from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.tables.m1m3 import FATable, actuator_id_to_index
from PySide6.QtCore import QEvent, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QGraphicsView

from .force_actuator_item import FASelection, ForceActuatorData, ForceActuatorItem
from .gauge_scale import GaugeScale
from .mirror import Mirror


class MirrorView(QGraphicsView):
    """View on mirror populated by actuators."""

    selectionChanged = Signal(ForceActuatorItem)
    """Signal raised when another actuator is selected by a mouse click.

    Parameters
    ----------
    support : bool, optional
        Populate mirror view with support actuators.
    thermal : bool, optional
        Populate mirror view with thermal actuators.
    """

    def __init__(self, support: bool, thermal: bool) -> None:
        self._mirror = Mirror(support, thermal)
        super().__init__(self._mirror)
        self._selected_actuator: ForceActuatorItem | None = None

    def get_force_actuator(self, actuator_id: int) -> ForceActuatorItem:
        """Returns ForceActuatorItem object with given ID.

        Parameters
        ----------
        actuator_id : `int`
            ID of the force actuator to retrieve.

        Returns
        -------
        actuator : `ForceActuatorItem`
            Force actuator object with give ID.

        Raises
        ------
        KeyError
            If actuator with given ID doesn't exists.
        """
        return self._mirror.fa[actuator_id_to_index(actuator_id)]

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.EnabledChange:
            for i in self._mirror.items():
                i.setEnabled(self.isEnabled())

    def _setNeighbour(self, index: int, activate: bool) -> None:
        for fids in FATable[index].far_neighbors:
            fa = self.get_force_actuator(fids)
            if activate:
                if fids in FATable[index].near_neighbors:
                    fa.setKind(FASelection.NEAR_NEIGHBOR)
                else:
                    fa.setKind(FASelection.FAR_NEIGHBOR)
            else:
                fa.setKind(FASelection.NORMAL)

    def selected(self) -> ForceActuatorItem | None:
        return self._selected_actuator

    def set_selected_id(self, selected_id: int) -> None:
        self.set_selected(self.get_force_actuator(selected_id))

    def clear_selected(self) -> None:
        if self._selected_actuator is not None:
            self._setNeighbour(self._selected_actuator.actuator.index, False)
            self._selected_actuator.setKind(FASelection.NORMAL)
            self._selected_actuator = None

    def set_selected(self, selected_actuator: ForceActuatorItem) -> None:
        self.clear_selected()

        selected_actuator.setKind(FASelection.SELECTED)
        self._setNeighbour(selected_actuator.actuator.index, True)
        self.selectionChanged.emit(selected_actuator)
        self._selected_actuator = selected_actuator

    def set_color_scale(self, scale: GaugeScale) -> None:
        """Sets scale used for color scaling.

        Parameters
        ----------
        scale : `class`
            New scale.
        """
        self._mirror.set_color_scale(scale)

    def clear(self) -> None:
        """Removes all actuators from the view."""
        self.clear_selected()
        self._mirror.clear()

    def update_scale(self) -> None:
        """Sets prefered scale."""
        s = min(self.width() / 8600, self.height() / 8600)
        self.scale(s, s)

    def update_force_actuator(
        self, fa: ForceActuatorData, data: BaseMsgType, state: int
    ) -> None:
        """Update actuator value and state.

        Parameters
        ----------
        fa : ForceActuatorData
            Force Actuator record.
        data : BaseMsgType
            Update actuator value.
        state : int
            Updated actuator state. ForceActuatorItem.STATE_INVALID,
            ForceActuatorItem.STATE_VALID, ForceActuatorItem.STATE_WARNING.

        Raises
        ------
        KeyError
            If actuator with the given ID cannot be found.
        """
        self._mirror.fa[fa.index].update_data(data, state)
        if self._selected_actuator is None:
            return
        if self._selected_actuator.actuator.actuator_id == fa.actuator_id:
            self.selectionChanged.emit(
                self._selected_actuator if self._selected_actuator.active else None
            )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        item = self.itemAt(event.pos())
        if isinstance(item, ForceActuatorItem):
            self.set_selected(item)
