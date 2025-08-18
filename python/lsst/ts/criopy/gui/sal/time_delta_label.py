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

from astropy.time import Time, TimeDelta
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

    time_delta : int, optional
        If not None and the calculated timeout (in seconds) is greater than
        this value, full date-time string will be displayed instead of time
        delta. Defaults to None.
    """

    def __init__(
        self,
        signal: Signal | None = None,
        field: str | None = None,
        timeout: int = 50,
        time_delta: float | None = None,
    ) -> None:
        super().__init__(signal, field)
        self.event_time: Time | None = None
        self.timeout = timeout
        if time_delta is None:
            self.time_delta = None
        else:
            self.time_delta = TimeDelta(float(time_delta), format="sec")
        self.timer = None

    def update(self) -> None:
        if self.event_time is None:
            self.setText("---")
        else:
            delta = Time.now() - self.event_time
            if self.time_delta is not None and abs(delta) > self.time_delta:
                self.setText(f"{Time(self.event_time, scale='utc').iso}")
            else:
                self.setText(f"{delta.sec:.2f}")

    @Slot()
    def setValue(self, time: float) -> None:
        if self.event_time is None:
            self.timer = self.startTimer(self.timeout)
        self.event_time = Time(time, format="unix_tai")

    def set_unknown(self) -> None:
        self.event_time = None
        if self.timer is not None:
            self.killTimer(self.timer)
            self.timer = None
        self.update()

    def timerEvent(self, event: QTimerEvent) -> None:
        self.update()
