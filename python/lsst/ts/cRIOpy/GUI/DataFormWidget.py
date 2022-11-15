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

from PySide2.QtCore import Slot, Signal
from PySide2.QtGui import QPalette
from PySide2.QtWidgets import QFormLayout, QWidget, QPushButton

from . import TimeChart, DataLabel, Colors

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

    timeChart : `TimeChart`
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
        fields: list[tuple[str, DataLabel]],
        timeChart: TimeChart = None,
    ):
        super().__init__()
        self._timeChart = timeChart

        layout = QFormLayout()
        for (text, label) in fields:
            if text is None:
                layout.addRow(label)
            else:
                layout.addRow(text, label)
        self.setLayout(layout)

        signal.connect(self._process_signal)

    def _process_signal(self, data):
        for e in dir(data):
            ch = self.findChild(QWidget, e)
            if ch is not None:
                ch.setValue(getattr(data, e))

    def mousePressEvent(self, ev):
        if self._timeChart is not None:
            child = self.childAt(ev.pos())
            if child is not None:
                self._timeChart.topicSelected.emit(child)


class DataFormButton(QPushButton):
    """
    Creates button displaying overall status. On click, creates widget showing
    data value. Update fields on signal with new values.

    Parameters
    ----------
    signal : `QSignal`
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

    def __init__(self, title, signal, fields):
        super().__init__(title)

        self._fields = fields

        self._dataWidget = DataFormWidget(signal, self._fields)
        self._dataWidget.setWindowTitle(self.text())

        signal.connect(self._dataChanged)
        self.clicked.connect(self._displayDetails)

    @Slot(map)
    def _dataChanged(self, data):
        pal = self.palette()
        pal.setColor(QPalette.Button, Colors.OK)
        for f in self._fields:
            if getattr(data, f[1].objectName()) is True:
                pal.setColor(QPalette.Button, Colors.ERROR)
                break
        self.setPalette(pal)

    @Slot()
    def _displayDetails(self):
        self._dataWidget.show()
