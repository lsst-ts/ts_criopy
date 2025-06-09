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


from math import sqrt

from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.tables.m1m3 import CENTER_HOLE_R, M1_R, M3_R, FATable, FCUTable
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPen
from PySide6.QtWidgets import QGraphicsScene

from .data_item import DataItemState
from .fcu_item import FCUItem
from .force_actuator_item import ForceActuatorItem
from .gauge_scale import GaugeScale


class Mirror(QGraphicsScene):
    """Graphics scene containing plot of the mirror surface with actuators.

    Actuator list is cleared with clear() method (inherited from
    QGraphicsScene). Force Actuators are added with add_force_actuator()
    method. Force Actuator data should be updated with update_force_actuator()
    call.

    Attributes
    ----------

    fa : [ForceActuatorItem]
        Mirror support system force actuators.
    fcu : [FCUItem]
        Mirror thermal system FCU (Fan Coil Units).

    Parameters
    ----------
    support : bool, optional
        Populate mirror view with support actuators.
    thermal : bool, optional
        Populate mirror view with thermal actuators.
    """

    def __init__(self, support: bool = False, thermal: bool = False) -> None:
        super().__init__()

        pen = QPen(Qt.black, 15, Qt.DashLine)

        # Plots mirror boundaries
        M2MM = 1000
        R_HOLE = CENTER_HOLE_R * M2MM
        R_M3 = M3_R * M2MM
        R_M1 = M1_R * M2MM
        self.addEllipse(-R_HOLE, -R_HOLE, R_HOLE * 2, R_HOLE * 2, pen)
        self.addEllipse(-R_M3, -R_M3, R_M3 * 2, R_M3 * 2, pen)
        self.addEllipse(-R_M1, -R_M1, R_M1 * 2, R_M1 * 2, pen)

        # Plots axes
        def vector(
            x: float,
            y: float,
            dx: float,
            dy: float,
            pen: QPen,
            text: str,
            tx: float,
            ty: float,
        ) -> None:
            self.addLine(x, y, x + dx, y + dy, pen)

            norm = sqrt(dx**2 + dy**2)
            udx = dx / norm
            udy = dy / norm

            wf = sqrt(3) * 0.5

            ax = udx * wf - udy * 0.5
            ay = udx * 0.5 + udy * wf
            bx = udx * wf + udy * 0.5
            by = -udx * 0.5 + udy * wf

            x += dx
            y += dy

            self.addLine(x, y, x - 100 * ax, y - 100 * ay, pen)
            self.addLine(x, y, x - 100 * bx, y - 100.0 * by, pen)

            font = QFont("Helvetica", 100)

            ti = self.addSimpleText(text, font)
            ti.setPos(x + tx, y + ty)

        pen = QPen(Qt.black, 10, Qt.SolidLine, Qt.RoundCap)

        xo = -R_M1
        yo = -R_M1 + 1000

        vector(xo, yo, 0, -1000, pen, "+Y", 100, -50)
        vector(xo, yo, 1000, 0, pen, "+X", 100, -100)
        self.addLine(xo - 100, yo - 100, xo + 100, yo + 100, pen)
        self.addLine(xo - 100, yo + 100, xo + 100, yo - 100, pen)

        self.fa: list[ForceActuatorItem] = []
        self.fcu: list[FCUItem] = []

        if support:
            for fa in FATable:
                self.add_fa(ForceActuatorItem(fa))

        if thermal:
            for fcu in FCUTable:
                self.add_fcu(FCUItem(fcu, DataItemState.INACTIVE))

    def add_fa(self, fa: ForceActuatorItem) -> None:
        self.fa.append(fa)
        fa.setZValue(9)
        self.addItem(fa)

    def add_fcu(self, fcu: FCUItem) -> None:
        self.fcu.append(fcu)
        fcu.setZValue(10)
        self.addItem(fcu)

    def set_color_scale(self, scale: GaugeScale) -> None:
        """Set display color scale. Provides get_brush method, returning brush
        to be used with value.

        Parameters
        ----------
        scale : `GaugeScale`
            Data scale.
        """
        for fa in self.fa:
            fa.set_color_scale(scale)

        for fcu in self.fcu:
            fcu.set_color_scale(scale)

    def update_force_actuator(
        self, index: int, data: BaseMsgType, state: DataItemState
    ) -> None:
        """Updates actuator value and state.

        Parameters
        ----------
        actuator_id : int
            Force Actuator ID number.
        data : BaseMsgType
            Update actuator value.
        state : DataItemState
            Updated actuator state. ForceActuatorItem.STATE_INVALID,
            ForceActuatorItem.STATE_VALID, ForceActuatorItem.STATE_WARNING.

        Raises
        ------
        KeyError
            If actuator with the given ID cannot be found.
        """
        self.fa[index].update_data(data, state)
