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

from PySide2.QtWidgets import QGroupBox, QHBoxLayout, QFormLayout, QWidget
from PySide2.QtCore import Slot


class ValueGrid(QGroupBox):
    """Displays Status Labels. Feed in hash with names and labels, event to
    connect to and number of columns.

    Parameters
    ----------
    valueLabel : `DataLabel or UnitLabel`
        Type of values. A class which provides setValue method to change its
        value.
    items : `map(str, str)`
        Keys are event items, values are labels for those items.
    event : `Signal`
        Event emitted when new data arrives.
    cols : `int`
        Number of columns.
    extraLabels : `array((str, QLabel))`, optional
        Extra labels added to beginning. Those are responsible for signal
        processing.
    """

    def __init__(self, valueLabel, items, event, cols, extraLabels=None):
        super().__init__()

        layout = QHBoxLayout()
        columns = []

        for c in range(cols):
            fl = QFormLayout()
            columns.append(fl)
            layout.addLayout(fl)

        if extraLabels is None:
            extraLabels = []

        lw = len(items) + len(extraLabels)
        rows = lw / cols
        i = 0
        for label, w in extraLabels:
            c = int(i / rows)
            i += 1
            columns[c].addRow(label, w)

        for n, label in items.items():
            c = int(i / rows)
            i += 1

            dataLabel = valueLabel()
            dataLabel.setObjectName(n)

            columns[c].addRow(label, dataLabel)

        self.setLayout(layout)

        event.connect(self._dataChanged)

    @Slot(map)
    def _dataChanged(self, data):
        for e in dir(data):
            ch = self.findChild(QWidget, e)
            if ch is not None:
                ch.setValue(getattr(data, e))


class StatusGrid(ValueGrid):
    """A variation of ValueGrid, assuming all labels are StatusLabel."""

    def __init__(self, items, event, cols):
        super().__init__(StatusLabel, items, event, cols)


class WarningGrid(ValueGrid):
    """A variation of ValueGrid, assuming all labels are WarningLabel."""

    def __init__(self, items, event, cols):
        super().__init__(WarningLabel, items, event, cols)


class OnOffGrid(ValueGrid):
    """A variation of ValueGrid, assuming all labels are OnOffLabel."""

    def __init__(self, items, event, cols):
        super().__init__(OnOffLabel, items, event, cols)


class PowerOnOffGrid(ValueGrid):
    """A variation of ValueGrid, assuming all labels are PowerOnOffLabel."""

    def __init__(self, items, event, cols):
        super().__init__(PowerOnOffLabel, items, event, cols)


class InterlockOffGrid(ValueGrid):
    """A variation of ValueGrid, assuming all labels are InterlockOffLabel.
    Adds anyWarning to display if any interlock is locked.
    """

    def __init__(self, items, event, cols, showAnyWarning=True):
        if showAnyWarning:
            self.anyWarningLabel = WarningLabel()
            super().__init__(
                InterlockOffLabel,
                items,
                event,
                cols,
                [("Any Warning", self.anyWarningLabel)],
            )
        else:
            self.anyWarningLabel = None
            super().__init__(InterlockOffLabel, items, event, cols)

    @Slot(map)
    def _dataChanged(self, data):
        super()._dataChanged(data)
        if self.anyWarningLabel:
            anyWarning = False
            for e in dir(data):
                ch = self.findChild(QWidget, e)
                if ch is not None:
                    anyWarning |= getattr(data, e)

            self.anyWarningLabel.setValue(anyWarning)
