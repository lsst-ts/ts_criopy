# This file is part of M1M3 SS GUI.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org). See the COPYRIGHT file at the top - level directory
# of this distribution for details of code ownership.
#
# This program is free software : you can redistribute it and / or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.If not, see <https://www.gnu.org/licenses/>.

from lsst.ts.m1m3.utils import BumpTestKind
from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.tables.m1m3 import ForceActuatorData
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QTreeView

from ...salcomm import MetaSAL
from ...time_cache import TimeCache
from .bump_test_status_item import BumpTestStatusItem


class BumpTestModel(QStandardItemModel):
    APPLIED_DATA = Qt.UserRole + 1
    MEASURED_DATA = Qt.UserRole + 2

    def __init__(self, m1m3: MetaSAL):
        super().__init__(0, 4)
        self.setHorizontalHeaderLabels(["AccID", "Index", "Kind", "Progress"])

        m1m3.appliedForces.connect(self.applied_forces)
        m1m3.forceActuatorData.connect(self.force_actuator_data)

    def append(
        self, fa: ForceActuatorData, kind: BumpTestKind
    ) -> tuple[TimeCache, TimeCache]:
        time_field = [("timestamp", "f8")]
        if kind == BumpTestKind.AXIS_X:
            axis_index = fa.x_index
        elif kind == BumpTestKind.AXIS_Y:
            axis_index = fa.y_index
        elif kind == BumpTestKind.AXIS_Z:
            axis_index = fa.z_index

        row = [
            QStandardItem(s) for s in [str(fa.actuator_id), str(axis_index), str(kind)]
        ] + [BumpTestStatusItem("--")]
        row[0].setData(fa)

        row[2].setData(kind)

        row[3].setBackground(Qt.GlobalColor.gray)

        row[3].setData(
            TimeCache(1000, time_field + [(f"Applied {str(kind)}", "f4")]),
            self.APPLIED_DATA,
        )
        row[3].setData(
            TimeCache(1000, time_field + [(f"Measured {str(kind)}", "f4")]),
            self.MEASURED_DATA,
        )

        self.appendRow(row)

        return (row[3].data(self.APPLIED_DATA), row[3].data(self.MEASURED_DATA))

    def find_tests(self, actuator_id: int, primary: bool) -> int | None:
        items = self.findItems(str(actuator_id), column=0)
        for i in items:
            row = i.index().row()
            kind = self.item(row, 2).data()
            if primary and kind in [
                BumpTestKind.CYLINDER_PRIMARY,
                BumpTestKind.AXIS_Z,
            ]:
                return row
            elif not (primary) and kind in [
                BumpTestKind.CYLINDER_SECONDARY,
                BumpTestKind.AXIS_X,
                BumpTestKind.AXIS_Y,
            ]:
                return row

        return None

    def caches(
        self, actuator_id: int, primary: bool
    ) -> tuple[TimeCache, TimeCache] | None:
        row = self.find_tests(actuator_id, primary)
        if row is not None:
            return (
                self.item(row, 3).data(self.APPLIED_DATA),
                self.item(row, 3).data(self.MEASURED_DATA),
            )
        return None

    def remove(self, actuator_id: int, primary: bool) -> None:
        row = self.find_tests(actuator_id, primary)
        if row is not None:
            self.removeRows(row, 1)

    @Slot()
    def applied_forces(self, data: BaseMsgType) -> None:
        for r in range(self.rowCount()):
            new = [data.timestamp * 1000.0]
            fa = self.item(r, 0).data()
            kind = self.item(r, 2).data()
            if kind == BumpTestKind.AXIS_X:
                new.append(data.xForces[fa.x_index])
            elif kind == BumpTestKind.AXIS_Y:
                new.append(data.yForces[fa.y_index])
            else:
                new.append(data.zForces[fa.z_index])

            self.item(r, 3).data(self.APPLIED_DATA).append(tuple(new))

    @Slot()
    def force_actuator_data(self, data: BaseMsgType) -> None:
        for r in range(self.rowCount()):
            new = [data.timestamp * 1000.0]
            fa = self.item(r, 0).data()
            kind = self.item(r, 2).data()
            if kind == BumpTestKind.AXIS_X:
                new.append(data.xForce[fa.x_index])
            elif kind == BumpTestKind.AXIS_Y:
                new.append(data.yForce[fa.y_index])
            else:
                new.append(data.zForce[fa.z_index])

            self.item(r, 3).data(self.MEASURED_DATA).append(tuple(new))


class BumpTestProgressWidget(QTreeView):
    """Holds all tests currenlly in progress."""

    def __init__(self, m1m3: MetaSAL):
        super().__init__()

        self.m1m3 = m1m3

        self.setModel(BumpTestModel(self.m1m3))
        self.setSortingEnabled(True)
        for col in range(self.model().columnCount()):
            self.resizeColumnToContents(col)

        self.setMinimumWidth(200)
        self.setMaximumWidth(420)

    def add(
        self, fa: ForceActuatorData, kind: BumpTestKind
    ) -> tuple[TimeCache, TimeCache]:
        return self.model().append(fa, kind)

    def clear(self) -> None:
        """Remove all actuators progress boxes."""
        self.setModel(BumpTestModel(self.m1m3))

    def progress(self, fa: ForceActuatorData, primary: bool, state: int) -> None:
        row = self.model().find_tests(fa.actuator_id, primary)
        if row is not None:
            self.model().item(row, 3).set_progress(state)
