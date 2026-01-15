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

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QHeaderView, QTreeView

from lsst.ts.m1m3.utils import ForceActuatorBumpTest


class QueuedTestModel(QStandardItemModel):
    """
    Shows force actuators selected for the bump tests. Those awaits to be
    executed.
    """

    def __init__(self) -> None:
        super().__init__(0, 2)
        self.setHorizontalHeaderLabels(["AccID", "Type"])


class BumpTestQueuedWidget(QTreeView):
    def __init__(self) -> None:
        super().__init__()

        self.setSortingEnabled(True)
        self.setRootIsDecorated(False)
        self.setModel(QueuedTestModel())
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.setMaximumWidth(
            self.header().length() + self.verticalScrollBar().sizeHint().width() + self.frameWidth() * 2
        )

    def append(self, fa_test: ForceActuatorBumpTest) -> None:
        row = [QStandardItem(s) for s in [str(fa_test.actuator.actuator_id), str(fa_test.kind)]]
        row[0].setData(fa_test)
        self.model().appendRow(row)

    def remove(self, fa_test: ForceActuatorBumpTest) -> None:
        m = self.model()
        for r in range(m.rowCount()):
            data = m.itemData(m.index(r, 0))[Qt.UserRole + 1]
            if data.actuator.actuator_id == fa_test.actuator.actuator_id and data.kind == fa_test.kind:
                m.removeRow(r)
                return
