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

from PySide2.QtWidgets import QLabel
from lsst.ts.salobj import current_tai

__all__ = ["TimeDeltaLabel"]


class TimeDeltaLabel(QLabel):
    """
    Displays time since some specified time in past. Updates display to show
    time from that past event.
    """

    def __init__(self):
        super().__init__()
        self.eventTime = None
        self.timer = None

    def update(self):
        if self.eventTime is None:
            self.setText("UNKNOWN")
        else:
            self.setText(f"{current_tai() - self.eventTime:.2f}")

    def setTime(self, time):
        if self.eventTime is None:
            self.timer = self.startTimer(50)
        self.eventTime = time

    def setUnknown(self):
        self.eventTime = None
        if self.timer is not None:
            self.killTimer(self.timer)
            self.timer = None
        self.update()

    def timerEvent(self, event):
        self.update()
