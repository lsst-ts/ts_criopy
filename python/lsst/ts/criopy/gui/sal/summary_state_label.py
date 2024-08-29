# This file is part of cRIO GUI.
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

from lsst.ts.salobj import State
from PySide6.QtCore import Qt, Signal

from ..custom_labels import DataLabel

__all__ = ["SummaryStateLabel"]


class SummaryStateLabel(DataLabel):
    """Display state label."""

    def __init__(self, signal: Signal = None, field: str | None = None):
        super().__init__(signal, field)
        self.setAlignment(Qt.AlignCenter)

    def setValue(self, value: State) -> None:
        states = {
            State.DISABLED: "Disabled",
            State.ENABLED: "Enabled",
            State.FAULT: "Fault",
            State.OFFLINE: "Offline",
            State.STANDBY: "Standby",
        }
        try:
            self.setText(states[value])
        except KeyError:
            self.setText(f"Unknown ({value})")
