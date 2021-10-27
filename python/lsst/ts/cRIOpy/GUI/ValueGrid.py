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

from .CustomLabels import (
    StatusLabel,
    WarningLabel,
    OnOffLabel,
    PowerOnOffLabel,
    InterlockOffLabel,
)

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
    extraLabels : `array((str, QLabel))`
        Extra labels added to beginning.
    """

    def __init__(self, valueLabel, states, event, cols, extraLabels=[]):
        super().__init__()
        self.states = {}

        layout = QGridLayout()

        lw = len(states)
        rows = lw / cols
        i = 0
        for (l, w) in extraLabels:
            r = i % rows
            c = int(i / rows) * 2
            i += 1
            layout.addWidget(QLabel(l), r, c)
            layout.addWidget(w, r, c + 1)

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


class OnOffGrid(ValueGrid):
    def __init__(self, states, event, cols):
        super().__init__(OnOffLabel, states, event, cols)


class PowerOnOffGrid(ValueGrid):
    def __init__(self, states, event, cols):
        super().__init__(PowerOnOffLabel, states, event, cols)


class InterlockOffGrid(ValueGrid):
    def __init__(self, states, event, cols, showAnyWarning=True):
        if showAnyWarning:
            self.anyWarningLabel = WarningLabel()
            super().__init__(
                InterlockOffLabel,
                states,
                event,
                cols,
                [("Any Warning", self.anyWarningLabel)],
            )
        else:
            self.anyWarningLabel = None
            super().__init__(InterlockOffLabel, states, event, cols)

    @Slot(map)
    def data(self, data):
        super().data(data)
        if self.anyWarningLabel:
            anyWarning = False
            for s in self.states.items():
                anyWarning |= getattr(data, s[0])
            self.anyWarningLabel.setValue(anyWarning)
