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
   from lsst.ts.criopy.GUI import (
       ArraySignal,
       ArrayGrid,
       ArrayItem,
       ArrayFields,
       Mm,
   )

   # sal holds SAL remote with signal "sig1", "sig2", "sig3" and "sig4"

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
               sal.sig3,
           ),
           ArrayLabels("Data", "", "", "", "", ""),
           ArrayFields(
               [
                   "data",
                   None,
                   None,
                   None,
                   None,
                   None,
               ],
               "Var Data",
               sal.sig4,
           ),
       ],
   )

   layout = <someLayout>()
   layout.addWidget(grid)
"""

__all__ = [
    "ArrayItem",
    "ArrayFields",
    "ArrayLabels",
    "ArraySignal",
    "ArrayButton",
    "ArrayGrid",
]

import typing

from asyncqt import asyncSlot
from lsst.ts.salobj import base
from PySide2.QtCore import QObject, Qt, Signal, Slot
from PySide2.QtGui import QMouseEvent
from PySide2.QtWidgets import QButtonGroup, QGridLayout, QLabel, QPushButton, QWidget

from ..SALComm import warning
from .CustomLabels import UnitLabel
from .TimeChart import TimeChart


class AbstractColumn(QObject):
    """Common ancestor to items within array.

    Attributes
    ----------
    widget : `QWidget`
        QWidgets/UnitLabes used to display array members together with index in
        data field, holding the value.
    """

    def __init__(
        self,
        field: str,
        label: str | None,
        widget: typing.Callable[[], UnitLabel] | None = UnitLabel,
        signal: Signal | None = None,
        indices: list[int] | None = None,
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
        self._indices = indices

        self.items: list[UnitLabel | None] = []

        if signal:
            signal.connect(self.data)  # type: ignore

    def attach_into(self, parent: "ArrayGrid", row: int) -> int:
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
        NotImplementedError
            Raised when abstract method is used.
        """
        raise NotImplementedError("Abstract attach_into called")

    def get_label(self, name: str, index: int) -> QWidget | None:
        """Returns label with given name and index.

        Parameters
        ----------
        name : `str`
            Row name - string with name of the variable.
        index : `int`
            Value index, 0 based, in the grid.

        Returns
        -------
        widget : `QLabel`
            Label representing value with given name and index.
        """
        if self.objectName() == name:
            return self.items[index]
        return None

    def get_data_index(self, idx: int) -> int:
        if self._indices is not None:
            return self._indices[idx]
        return idx

    @Slot()
    def data(self, data: typing.Any) -> None:
        """Process incoming data.

        Parameters
        ----------
        data : `map(any)`
            Map with data to display. Field named "self.objectName()" (field
            supplied in constructor) is used to extract data to display.
        """
        fd = getattr(data, self.objectName())
        for idx, item in enumerate(self.items):
            if item is not None:
                item.setValue(fd[self.get_data_index(idx)])


class ArrayItem(AbstractColumn):
    """Variable with values in array."""

    def __init__(
        self,
        field: str,
        label: str,
        widget: typing.Callable[[], UnitLabel] = UnitLabel,
        signal: Signal | None = None,
        indices: list[int] | None = None,
    ):
        """Construct QObject holding widgets for array."""
        super().__init__(field, label, widget, signal, indices)

    def attach_into(self, parent: "ArrayGrid", row: int) -> int:
        if self._widget is None:
            return row

        self.items = [self._widget() for i in range(parent.get_data_rows())]

        parent.add_widget(QLabel(self._label), row, 0)

        for c, i in enumerate(self.items):
            parent.add_widget(i, row, c + 1)
            if i is not None:
                i.setObjectName(self.objectName() + f"[{c}]")
                i.setCursor(Qt.PointingHandCursor)
        return row + 1


class ArrayFields(AbstractColumn):
    """Class insrted into ArrayGrid to display an arrya of value, with optional
    widgets at the end.

    Parameters
    ----------
    fields: `[str]`
        Fields to display. Can include None in order to skip a column.
    label: `str`
        Row label text.
    widget: `UnitLabel`
        Type of widget added into row.
    signal:`Signal`
        Signal delivering fields values to be displayed.
    extra_widgets: `[QWidget]`
        Extra widgets added at the end of row.
    """

    def __init__(
        self,
        fields: list[str | None],
        label: str | None,
        widget: typing.Callable[[], UnitLabel] = UnitLabel,
        signal: Signal | None = None,
        extra_widgets: list[QWidget] = [],
    ):
        super().__init__("", label, widget, signal)
        self.fields = fields
        self.extra_widgets = extra_widgets

    def attach_into(self, parent: "ArrayGrid", row: int) -> int:
        if self._widget is None:
            return row

        self.items = [None if f is None else self._widget() for f in self.fields]

        parent.add_widget(QLabel(self._label), row, 0)

        for c, i in enumerate(self.items):
            if i is None:
                continue
            parent.add_widget(i, row, c + 1)
            i.setObjectName(self.fields[c])
            i.setCursor(Qt.PointingHandCursor)

        base_col = len(self.fields) + 1
        for c, w in enumerate(self.extra_widgets):
            parent.add_widget(w, row, c + base_col)

        return row + 1

    @Slot()
    def data(self, data: typing.Any) -> None:
        for i in self.items:
            if i is None:
                continue

            d = getattr(data, i.objectName())
            i.setValue(d)  # type: ignore


class ArrayLabels(AbstractColumn):
    def __init__(self, *labels: str):
        super().__init__("", "")
        self._labels = labels

    def attach_into(self, parent: "ArrayGrid", row: int) -> int:
        parent.rows = list(self._labels)

        for c, l in enumerate(self._labels):
            parent.add_widget(QLabel(l), row, c + 1)

        return row + 1

    @Slot()
    def data(self, data: typing.Any) -> None:
        pass


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

    def attach_into(self, parent: "ArrayGrid", row: int) -> int:
        for i in self.array_items:
            i.attach_into(parent, row)
            row += 1
        return row

    def get_label(self, name: str, index: int) -> QWidget | None:
        for i in self.array_items:
            label = i.get_label(name, index)
            if label:
                return label
        return None

    @Slot()
    def data(self, data: typing.Any) -> None:
        for i in self.array_items:
            field = i.objectName()
            if field == "":
                i.data(data)
            else:
                d = getattr(data, i.objectName())
                for fi, c in enumerate(i.items):
                    if c is not None:
                        c.setValue(d[fi])


class ArrayButton(AbstractColumn):
    """Buttons for actions performed per array member.

    Attributes
    ----------
    action : `func(int)`
    buttonGroup : `QButtonGroup`

    """

    def __init__(
        self, action: typing.Callable[[int], typing.Awaitable[typing.Any]], text: str
    ):
        """ """
        super().__init__("", text)
        self.action = action
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.buttonClicked.connect(self._buttonClicked)

    def attach_into(self, parent: "ArrayGrid", row: int) -> int:
        for i in range(parent.get_data_rows()):
            b = QPushButton(self._label)
            parent.add_widget(b, row, i + 1)
            self.buttonGroup.addButton(b)
        return row + 1

    @asyncSlot()
    async def _buttonClicked(self, bnt: QPushButton) -> None:
        text = bnt.text()
        bnt.setDisabled(True)
        try:
            await self.action(self.buttonGroup.buttons().index(bnt))
        except (base.AckError, base.AckTimeoutError) as ackE:
            warning(
                bnt,
                f"Error executing button {text}",
                "Error executing button" f" <i>{text}</i>:<br/>{ackE.ackcmd.result}",
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
        chart: TimeChart | None = None,
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

        row = 1
        for i in items:
            row = i.attach_into(self, row)

    def add_widget(self, widget: QWidget, row: int, col: int) -> None:
        self.layout().addWidget(widget, *self._rowcol(row, col))

    def _rowcol(self, r: int, c: int) -> tuple[int, int]:
        return (c, r) if self.orientation == Qt.Vertical else (r, c)

    def get_data_rows(self) -> int:
        return len(self.rows)

    def get_label(self, name: str, index: int) -> QWidget | None:
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

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        if self._chart is not None:
            child = self.childAt(ev.pos())
            if child is not None:
                self._chart.topicSelected.emit(child)
