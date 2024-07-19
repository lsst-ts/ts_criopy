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


from lsst.ts.salobj import BaseMsgType
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from ..salcomm import MetaSAL


class OverviewPageWidget(QWidget):
    PUBLISH_FIELDS = ["target", "dX", "dY", "dZ", "dRX", "dRY", "dRZ"]

    def __init__(self, laser_tracker: MetaSAL):
        super().__init__()

        layout = QVBoxLayout()
        self.measurements = QTableWidget(1, len(self.PUBLISH_FIELDS))
        self.measurements.setHorizontalHeaderLabels(self.PUBLISH_FIELDS)
        for i in range(self.measurements.columnCount()):
            self.measurements.horizontalHeaderItem(i).setTextAlignment(Qt.AlignHCenter)

        layout.addWidget(self.measurements)

        self.setLayout(layout)

        laser_tracker.offsetsPublish.connect(self.offsets_publish)

    @Slot()
    def offsets_publish(self, data: BaseMsgType) -> None:
        r = self.measurements.rowCount() + 1
        self.measurements.setRowCount(r)
        for c, f in enumerate(self.PUBLISH_FIELDS):
            self.measurements.setItem(r, c, QTableWidgetItem(getattr(data, f)))
