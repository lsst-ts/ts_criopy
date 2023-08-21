# This file is part of cRIO generic GUI.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https: //www.lsst.org).
# See the COPYRIGHT file at the top - level directory of this distribution
# for details of code ownership.
#
# This program is free software : you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.If not, see < https:  // www.gnu.org/licenses/>.

import typing

from PySide2.QtCore import Signal, Slot
from PySide2.QtGui import QMouseEvent
from PySide2.QtWidgets import QFormLayout, QWidget

from .CustomLabels import ColoredButton, Colors, DataLabel
from .TimeChart import TimeChart

__all__ = ["DataFormWidget", "DataFormButton"]


class DataFormWidget(QWidget):
    """
    Creates labels with data displays. Update fields on signal with new values.

    Parameters
    ----------
    signal : `QSignal`
        Signal with new data. It is assumed DataLabel childs passed in fields
        contain DataLabel with field corresponding to fields in the signal.

    fields : `[(str, DataLabel)]`
        Tuple of text and label. Label shall be child of DataLabel with
        fieldname set.

    timeChart : `TimeChart`, optional
        Time chart receiving "topicSelected" when label is clicked.

    Usage
    -----
       myWidget = DataFormWidget(sal.errors, [(
           "Power",
           WarningLabel(None, "state")
       )])
    """

    def __init__(
        self,
        signal: Signal,
        fields: list[tuple[str | None, DataLabel]],
        timeChart: TimeChart | None = None,
    ):
        super().__init__()
        self._timeChart = timeChart

        layout = QFormLayout()
        for text, label in fields:
            if text is None:
                layout.addRow(label)
            else:
                layout.addRow(text, label)
        self.setLayout(layout)

        signal.connect(self._process_signal)

    def _process_signal(self, data: typing.Any) -> None:
        for e in dir(data):
            ch = self.findChild(QWidget, e)
            if ch is not None:
                ch.setValue(getattr(data, e))

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if self._timeChart is not None:
            child = self.childAt(ev.pos())
            if child is not None:
                self._timeChart.topicSelected.emit(child)


class DataFormButton(ColoredButton):
    """
    Creates button displaying overall status. On click, creates widget showing
    data value. Update fields on signal with new values.

    Parameters
    ----------
    text : `str`
        Button text.
    signal : `Signal`
        Signal with new data. It is assumed DataLabel childs passed in fields
        contain DataLabel with field corresponding to fields in the signal.
    fields : `[(str, DataLabel)]`
        Tuple of text and label. Label shall be child of DataLabel with
        fieldname set.

    Usage
    -----
       myWidget = DataFormWidget(sal.errors, [(
           "Power", WarningLabel(None, "state")
       )])
    """

    def __init__(
        self, text: str, signal: Signal, fields: list[tuple[str | None, DataLabel]]
    ):
        super().__init__(text)

        self._fields = fields

        self._dataWidget = DataFormWidget(signal, self._fields)
        self._dataWidget.setWindowTitle(self.text())

        signal.connect(self._dataChanged)
        self.clicked.connect(self._displayDetails)

    @Slot()
    def _dataChanged(self, data: typing.Any) -> None:
        color = Colors.OK
        for f in self._fields:
            if getattr(data, f[1].objectName()) is True:
                color = Colors.ERROR
                break
        self.setColor(color)

    @Slot()
    def _displayDetails(self) -> None:
        self._dataWidget.show()
