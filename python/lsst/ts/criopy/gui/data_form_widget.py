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

from lsst.ts.salobj import BaseMsgType
from PySide6.QtCore import Signal, Slot
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QFormLayout, QWidget

from .colors import Colors
from .custom_labels import ColoredButton, DataLabel
from .time_chart import TimeChart

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
        time_chart: TimeChart | None = None,
    ):
        super().__init__()
        self.__time_chart = time_chart

        layout = QFormLayout()
        for text, label in fields:
            if text is None:
                layout.addRow(label)
            else:
                layout.addRow(text, label)
        self.setLayout(layout)

        signal.connect(self._process_signal)

    def _process_signal(self, data: BaseMsgType) -> None:
        for e in dir(data):
            for ch in self.findChildren(QWidget, e):
                ch.new_data(data)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if self.__time_chart is not None:
            child = self.childAt(ev.pos())
            if child is not None:
                self.__time_chart.topicSelected.emit(child)


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
    def _dataChanged(self, data: BaseMsgType) -> None:
        color = Colors.OK
        for f in self._fields:
            if getattr(data, f[1].objectName()) is True:
                color = Colors.ERROR
                break
        self.setColor(color)

    @Slot()
    def _displayDetails(self) -> None:
        self._dataWidget.show()
