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

import typing

from PySide2.QtCore import Slot
from PySide2.QtGui import QStandardItem, QStandardItemModel
from PySide2.QtWidgets import QTreeView, QVBoxLayout, QWidget

from ..SALComm import MetaSAL


class EventWindow(QWidget):
    """
    Class representing widget with event data.

    Parameters
    ----------
    comm : `MetaSAL`
        SAL/DDS communication object.
    topic : `str`
        Topic (without evt_ prefix) for which data will be displayed.
    """

    def __init__(self, comm: MetaSAL, topic: str):
        super().__init__()
        self.setWindowTitle(f"{comm.remote.salinfo.name}/{topic}")

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

    @Slot()
    def newData(self, data: typing.Any) -> None:
        usedMembers = filter(
            lambda member: not (member.startswith("_") and member == "priority"),
            data.__dict__,
        )

        if self._data is None:
            for member in usedMembers:
                self.model.appendRow(
                    [
                        QStandardItem(str(member)),
                        QStandardItem(str(getattr(data, member))),
                    ]
                )
            self._data = data
            return

        for member in usedMembers:
            items = self.model.findItems(str(member))
            self.model.item(items[0].index().row(), 1).setText(
                str(getattr(data, member))
            )

        self._data = data
