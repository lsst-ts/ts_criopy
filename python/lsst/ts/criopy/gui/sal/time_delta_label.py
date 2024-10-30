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

from lsst.ts.utils import current_tai
from PySide6.QtCore import QTimerEvent, Signal, Slot

from ..custom_labels import DataLabel

__all__ = ["TimeDeltaLabel"]


class TimeDeltaLabel(DataLabel):
    """
    Displays time since some specified time in past. Updates display to show
    time from that past event.

    Parameters
    ----------
    signal : `Signal`, optional
        Signal to which the data shall be connected. If specified, widget will
        connect to this signal wit the update. Defaults to None, no signal
        connected.

    field : `str`, optional
        SAL field that contains time float. Usually private_sndStamp or
        timestamp. Defaults to None, not field selected.

    timeout : `int`, optional
        Timeout value in ms. After this time expires, the label will turn red.
        Defaults to 50 ms.
    """

    def __init__(
        self, signal: Signal | None = None, field: str | None = None, timeout: int = 50
    ) -> None:
        super().__init__(signal, field)
        self.event_time: float | None = None
        self.timeout = timeout
        self.timer = None

    def update(self) -> None:
        if self.event_time is None:
            self.setText("---")
        else:
            self.setText(f"{current_tai() - self.event_time:.2f}")

    @Slot()
    def setValue(self, time: float) -> None:
        if self.event_time is None:
            self.timer = self.startTimer(self.timeout)
        self.event_time = time

    def set_unknown(self) -> None:
        self.event_time = None
        if self.timer is not None:
            self.killTimer(self.timer)
            self.timer = None
        self.update()

    def timerEvent(self, event: QTimerEvent) -> None:
        self.update()
