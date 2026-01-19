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

from math import isnan

from astropy.time import Time
from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QHeaderView, QTreeView

from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.enums.MTM1M3 import BumpTestType

from .bump_test_status_item import BumpTestStatusItem


class SndTimestampItem(QStandardItem):
    def __init__(self, time: Time):
        super().__init__(time.strftime("%H:%M:%S.%f"))


class ElapsedTimeItem(QStandardItem):
    def __init__(self, elapsed: float):
        super().__init__(f"{elapsed:.2f}")
        if isnan(elapsed):
            self.setBackground(Qt.red)


class BumpTestStatistics(QStandardItemModel):
    def __init__(self, parent: QObject) -> None:
        super().__init__(0, 8, parent)

        self.setHorizontalHeaderLabels(
            ["Time", "AccID", "Type", "Stage", "Settle Time", "Minimum", "Maximum", "Average", "Error RMS"]
        )

    def add_statistic_event(self, data: BaseMsgType) -> None:
        def test_type_str(test_type: int) -> str:
            test_map = {
                BumpTestType.PRIMARY: "P",
                BumpTestType.SECONDARY: "S",
                BumpTestType.Z: "Z",
                BumpTestType.Y: "Y",
                BumpTestType.X: "X",
            }
            return test_map[test_type]

        self.appendRow(
            [
                SndTimestampItem(Time(data.private_sndStamp, format="unix_tai")),
                QStandardItem(str(data.actuatorId)),
                QStandardItem(test_type_str(data.testType)),
                QStandardItem(BumpTestStatusItem.get_text(data.stage)),
                ElapsedTimeItem(data.settleTime),
                QStandardItem(f"{data.minimum:.2f} N"),
                QStandardItem(f"{data.maximum:.2f} N"),
                QStandardItem(f"{data.average:.2f} N"),
                QStandardItem(f"{data.errorRMS:.2f} N"),
            ]
        )


class BumpTestStatisticsView(QTreeView):
    def __init__(self) -> None:
        super().__init__()
        self.setSortingEnabled(True)
        self.setRootIsDecorated(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
