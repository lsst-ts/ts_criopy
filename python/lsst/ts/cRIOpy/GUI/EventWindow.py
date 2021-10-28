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
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget, QVBoxLayout, QTreeView
from PySide2.QtGui import QStandardItemModel, QStandardItem


class EventWindow(QWidget):
    def __init__(self, comm, topic):
        super().__init__()

        self._data = None

        layout = QVBoxLayout()
        self.tree = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Name", "Data"])
        self.tree.setModel(self.model)

        layout.addWidget(self.tree)

        self.setLayout(layout)

        getattr(comm, topic).connect(self.newData)

        data = getattr(comm.remote, "evt_" + topic).get()
        if data:
            self.newData(data)

    @Slot(map)
    def newData(self, data):
        if self._data is None:
            for a in data.__dict__:
                if a.startswith("_") or a == "priority":
                    continue
                self.model.appendRow(
                    [QStandardItem(str(a)), QStandardItem(str(getattr(data, a)))]
                )
            self._data = data
            return

        for a in data.__dict__:
            if a.startswith("_") or a == "priority":
                continue
            items = self.model.findItems(str(a))
            self.model.item(items[0].index().row(), 1).setText(str(getattr(data, a)))

        self._data = data
