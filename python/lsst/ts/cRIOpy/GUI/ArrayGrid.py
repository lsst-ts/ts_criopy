# This file is part of cRIO UIs.
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
"""Module displaying grid of UnitLabels.

Creates widget utilizing QGridLayout to display multi-indexed variables.
Provides functions to add variables into TimeChart. In default, Vertical
orientation, columns represents data items, while rows are used to display
array items. For example for hardpoints, columns are forces, encoder values and
rows are hardpoint numbers.

Usage
-----
.. code-block:: python
   from lsst.ts.cRIOpy.GUI import (
       ArraySignal,
       ArrayGrid,
       ArrayItem,
       ArrayFields,
       Mm,
   )

   # sal holds SALComm remote with signal "sig1", "sig2" and "sig3"

   grid = ArrayGrid(
       "<b>Some data</b>",
       [f"<b>{x}</b>" for b in range(1, 7)],
       [
           ArrayItem("myField", "Label 1", Mm, sal.sig1),
           ArraySignal(
               sal.sig2,
               [
                   ArrayItem("fieldA", "A"),
                   ArrayItem("fieldB", "B"),
                   ArrayItem("fieldC", "C"),
                   ArrayFields(["fX", None, "fZ"], "My forces")
               ]
           ),
           ArrayFields(
               [
                   None,
                   None,
                   "fZ",
                   None,
                   None,
                   "mZ"
               ],
               "Forces",
               sal.sig3
           ),
       ],
   )

   layout = <someLayout>()
   layout.addWidget(grid)
"""

__all__ = ["ArrayItem", "ArrayFields", "ArraySignal", "ArrayButton", "ArrayGrid"]

from PySide2.QtCore import QObject, Slot, Signal, Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QLabel, QButtonGroup, QPushButton

from asyncqt import asyncSlot

from lsst.ts.salobj import base

from . import UnitLabel, TimeChart
from .SAL.SALComm import warning


# forward declaration for MyPy
class ArrayGrid:
    pass


class AbstractColumn(QObject):
    """Common ancestor to items within array.

    Attributes
    ----------
    items : `[UnitLabel]`
        QWidgets/UnitLabes used to display array members.

    """

    def __init__(
        self,
        field: str,
        label: str,
        widget: UnitLabel = UnitLabel,
        signal: Signal = None,
    ):
        """
        Creates member of grid representing an array.

        Parameters
        ----------
        field : `str`
            Field within data holding the values.
        label : `str`
            Label displayed on top of the row.
        widget : `UnitLabel`, optional
            Type of widget to be used in the grid to display the array. If
            signal is provided, widget setValue method is used to set the
            value.
        signal : `Signal`, optional
            Connect to this signal to receive data updates.
        """
        super().__init__()
        self.setObjectName(field)
        self._label = label
        self._widget = widget

        self.items = None

        if signal:
            signal.connect(self.data)

    def attach_into(self, parent: ArrayGrid, row: int) -> int:
        """
        Creates widgets in ArrayGrid.

        Parameters
        ----------
        parent : `ArrayGrid`
            Grid array where items will be attached.
        row : `int`
            Current row index.

        Returns
        -------
        row : `int`
            New row index after current member was added.

        Raises
        ------
        RuntimeError
            Raised when abstract method is used.
        """
        raise RuntimeError("Abstract attach_into called")

    def get_label(self, name: str, index: int) -> QWidget:
        """Returns label with given name and index.

        Parameters
        ----------
        name : `str`
            Row name - string with name of the variable.
        index : `int`
            Value index.

        Returns
        -------
        widget : `QLabel`
            Label representing value with given name and index.
        """
        if self.objectName() == name:
            return self.items[index]
        return None

    @Slot(map)
    def data(self, data: map):
        """Process incoming data.

        Parameters
        ----------
        data : `map(any)`
            Map with data to display. Field named "self.objectName()" (field
            supplied in constructor) is used to extract data to display.
        """
        fd = getattr(data, self.objectName())
        for idx, item in enumerate(self.items):
            item.setValue(fd[idx])


class ArrayItem(AbstractColumn):
    """Variable with values in array."""

    def __init__(
        self,
        field: str,
        label: str,
        widget: UnitLabel = UnitLabel,
        signal: Signal = None,
    ):
        """Construct QObject holding widgets for array."""
        super().__init__(field, label, widget, signal)

    def attach_into(self, parent: ArrayGrid, row: int) -> int:
        self.items = [self._widget() for i in range(parent.get_data_rows())]

        parent.add_widget(QLabel(self._label), row, 0)

        for c, i in enumerate(self.items):
            parent.add_widget(i, row, c + 1)
            i.setObjectName(self.objectName() + f"[{c}]")
            i.setCursor(Qt.PointingHandCursor)
        return row + 1


class ArrayFields(AbstractColumn):
    def __init__(
        self,
        fields: [str],
        label: str,
        widget: UnitLabel = UnitLabel,
        signal: Signal = None,
    ):
        super().__init__("", label, widget, signal)
        self.fields = fields

    def attach_into(self, parent: ArrayGrid, row: int) -> int:
        self.items = [None if f is None else self._widget() for f in self.fields]

        parent.add_widget(QLabel(self._label), row, 0)

        for c, i in enumerate(self.items):
            if i is None:
                continue
            parent.add_widget(i, row, c + 1)
            i.setObjectName(self.fields[c])
            i.setCursor(Qt.PointingHandCursor)
        return row + 1

    @Slot(map)
    def data(self, data):
        for i in self.items:
            if i is None:
                continue

            d = getattr(data, i.objectName())
            i.setValue(d)


class ArraySignal(AbstractColumn):
    def __init__(self, signal: Signal, items: list[AbstractColumn]):
        """Construct member holding multiple array items. Shall be used to
        group together ArrayItems receiving data from a single signal/SAL
        topic.

        Parameters
        ----------
        signal : `Signal`
            Signal fired when new data are available.
        items : `[ArrayItem]`
            Items to display. Those shall not have the signal connected.
        """
        super().__init__("", "", None, signal)
        self.array_items = items

    def attach_into(self, parent: ArrayGrid, row: int) -> int:
        for i in self.array_items:
            i.attach_into(parent, row)
            row += 1
        return row

    def get_label(self, name: str, index: int) -> QWidget:
        for i in self.array_items:
            label = i.get_label(name, index)
            if label:
                return label
        return None

    @Slot(map)
    def data(self, data):
        for i in self.array_items:
            d = getattr(data, i.objectName())
            for fi, c in enumerate(i.items):
                c.setValue(d[fi])


class ArrayButton(AbstractColumn):
    """Buttons for actions performed per array member.

    Attributes
    ----------
    action : `func(int)`
    buttonGroup : `QButtonGroup`

    """

    def __init__(self, action, text: str):
        """ """
        super().__init__("", text)
        self.action = action
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.buttonClicked.connect(self._buttonClicked)

    def attach_into(self, parent: ArrayGrid, row: int) -> int:
        for i in range(parent.get_data_rows()):
            b = QPushButton(self._label)
            parent.add_widget(b, row, i + 1)
            self.buttonGroup.addButton(b)
        return row + 1

    @asyncSlot()
    async def _buttonClicked(self, bnt):
        text = bnt.text()
        bnt.setDisabled(True)
        try:
            await self.action(self.buttonGroup.buttons().index(bnt))
        except (base.AckError, base.AckTimeoutError) as ackE:
            warning(
                bnt,
                f"Error executing button {text}",
                f"Error executing button <i>{text}</i>:<br/>{ackE.ackcmd.result}",
            )
        except RuntimeError as rte:
            warning(
                bnt,
                f"Error executing {text}",
                f"Executing button <i>{text}</i>:<br/>{str(rte)}",
            )
        finally:
            bnt.setEnabled(True)


class ArrayGrid(QWidget):
    """Construct grid of Array-like items.

    Shall be used to display arrays associated with some physical hardware.

    Attributes
    ----------
    rows : `[str]`
        Labels for array items. Length of the array is number of rows, which
        equals to number of items/variables.

    orientation : `Qt.Orientation`
        Grid orientation. Vertical displays in columns indices and in rows
        values. Horizontal swaps rows and columns.
    """

    def __init__(
        self,
        title: str,
        rows: list[str],
        items: list[AbstractColumn],
        orientation: Qt.Orientation = Qt.Vertical,
        chart: TimeChart = None,
    ):
        """Construct grid item holding ArrayItems.

        Parameters
        ----------
        title : `str`
            Title label. Displayed in top left cell.
        rows : `[str]`
            Labels for rows.
        items : `[AbstractColumn]`
            Items to be displayed in grid.
        orientation : `Qt.Orientation`, optional
            Either Qt.Vertical or Qt.Horizontal. Qt.Vertical, the default,
            displays in columns indices (e.g. for hardpoints, 1, 2, 3..), and
            in rows values (Force,..). Qt.Horizontal swaps rows for columns and
            vice versa.
        chart : `TimeChart`, optional
            Timechart to display values from clicked label.
        """
        super().__init__()
        self.rows = rows
        self._items = items
        self.orientation = orientation
        self._chart = chart

        self.setLayout(QGridLayout())

        self.add_widget(QLabel(title), 0, 0)

        for c, r in enumerate(self.rows):
            self.add_widget(QLabel(r), 0, c + 1)

        r = 1
        self.labels_rows = {}
        for i in items:
            r = i.attach_into(self, r)

    def add_widget(self, widget, row, col):
        self.layout().addWidget(widget, *self._rowcol(row, col))

    def _rowcol(self, r, c):
        return (c, r) if self.orientation == Qt.Vertical else (r, c)

    def get_data_rows(self) -> int:
        return len(self.rows)

    def get_label(self, name: str, index: int) -> QWidget:
        """Returns label with given name and index.

        Parameters
        ----------
        name : `str`
            Row name - string with name of the variable.
        index : `int`
            Value index.

        Returns
        -------
        widget : `QLabel`
            Label representing value with given name and index.
        """
        for i in self._items:
            label = i.get_label(name, index)
            if label is not None:
                return label
        return None

    def mousePressEvent(self, ev):
        if self._chart is not None:
            child = self.childAt(ev.pos())
            if child is not None:
                self._chart.topicSelected.emit(child)
