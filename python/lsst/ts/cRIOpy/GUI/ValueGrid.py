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

from .CustomLabels import StatusLabel, WarningLabel

from PySide2.QtWidgets import QGroupBox, QGridLayout, QLabel
from PySide2.QtCore import Slot


class ValueGrid(QGroupBox):
    """Displays Status Labels. Feed in hash with names and labels, event to
    connect to and number of columns.

    Parameters
    ----------
    valueLabel : `class`
        Type of values.
    states : `map(str, str)`
        Keys are event items, values are labels for those items.
    event : `Signal`
        Event emitted when new data arrives.
    cols : `int`
        Number of columns.
    """

    def __init__(self, valueLabel, states, event, cols):
        super().__init__()
        self.states = {}

        layout = QGridLayout()

        lw = len(states)
        rows = lw / cols
        i = 0
        for s in states.items():
            r = i % rows
            c = int(i / rows) * 2
            i += 1

            layout.addWidget(QLabel(s[1]), r, c)

            label = valueLabel()
            layout.addWidget(label, r, c + 1)

            self.states[s[0]] = label

        self.setLayout(layout)

        event.connect(self.data)

    @Slot(map)
    def data(self, data):
        for s in self.states.items():
            s[1].setValue(getattr(data, s[0]))


class StatusGrid(ValueGrid):
    def __init__(self, states, event, cols):
        super().__init__(StatusLabel, states, event, cols)


class WarningGrid(ValueGrid):
    def __init__(self, states, event, cols):
        super().__init__(WarningLabel, states, event, cols)
