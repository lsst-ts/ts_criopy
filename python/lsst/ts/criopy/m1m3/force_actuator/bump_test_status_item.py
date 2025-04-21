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

from lsst.ts.xml.enums.MTM1M3 import BumpTest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem

__all__ = ["BumpTestStatusItem"]


class BumpTestStatusItem(QStandardItem):
    TEST_PROGRESS = [
        "Unknown",
        "Not tested",
        "Triggered",
        "Testing positive",
        "Positive wait zero",
        "Testing negative",
        "Negative wait zero",
        "Passed",
        "Failed timeout",
        "Failed Positive Overshoot",
        "Failed Positive Undershoot",
        "Failed Negative Overshoot",
        "Failed Negative Undershoot",
        "Failed other FA",
    ]

    STATE_DATA = Qt.UserRole + 10

    def __init__(self, text: str):
        super().__init__(text)

    def set_progress(self, state: int) -> None:
        self.setData(state, self.STATE_DATA)
        self.setText(self.TEST_PROGRESS[state])
        if state < int(BumpTest.PASSED):
            self.setBackground(Qt.GlobalColor.yellow)
        elif state == BumpTest.PASSED:
            self.setBackground(Qt.GlobalColor.green)
        else:
            self.setBackground(Qt.GlobalColor.red)

    def state(self) -> int:
        return self.data(self.STATE_DATA)
