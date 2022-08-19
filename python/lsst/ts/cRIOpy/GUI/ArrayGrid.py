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

Tst..
"""

__all__ = ["ArrayItem", "ArraySignal", "ArrayButton", "ArrayGrid"]

import typing

from PySide2.QtCore import QObject, Slot, Signal, Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QLabel, QButtonGroup, QPushButton

from asyncqt import asyncSlot

from lsst.ts.salobj import base

from . import UnitLabel
from .SAL.SALComm import warning


class ArrayItem(QObject):
    """Item in array attribute.

    Attributes
    ----------
    signal : `Signal`
    field : `str`
    size : `int`
    unit : `UnitLabel`
    """

    def __init__(
        self, field: str, name: str, signal: Signal = None, unit: UnitLabel = UnitLabel
    ):
        """Construct QObject holding widgets for array.

        Parameters
        ----------
        field : `str`
        name : `str`
        signal : `Signal`
        unit : `UnitLabel`
        """
        super().__init__()
        self._field = field
        self._name = name
        self._unit = unit

        if signal is not None:
            signal.connect(self._data)

    def get_name(self, idx=None) -> str:
        return self._name

    def get_widgets(self, size, idx=None) -> typing.List[UnitLabel]:
        """
        Parameters
        ----------
        size : `int`
        idx : `int`, optional
            Defaults to None.
        """
        self.items = [self._unit() for i in range(size)]
        return self.items

    @Slot(map)
    def _data(self, data):
        fd = getattr(data, self._field)
        for idx, item in enumerate(self.items):
            item.setValue(fd[idx])


class ArraySignal(QObject):
    def __init__(self, signal: Signal, items: typing.List[ArrayItem]):
        self.array_items = items
        self.items = {}
        signal.connect(self._data)

    def get_name(self, idx: int = None) -> str:
        return self.array_items[idx].get_name()

    def get_widgets(self, size: int, idx: int) -> typing.List[UnitLabel]:
        self.items[idx] = self.array_items[idx].get_widgets(size)
        return self.items[idx]

    @Slot(map)
    def _data(self, data):
        for idx, i in enumerate(self.array_items):
            d = getattr(data, i._field)
            for fi, c in enumerate(i.items):
                c.setValue(d[fi])


class ArrayButton(QObject):
    def __init__(self, action, text: str):
        self.action = action
        self.text = text
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.buttonClicked.connect(self._buttonClicked)

    def get_name(self, idx=None) -> str:
        return ""

    def get_widgets(self, size, idx=None) -> typing.List[QPushButton]:
        for i in range(size):
            self.buttonGroup.addButton(QPushButton(self.text))
        return self.buttonGroup.buttons()

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
    """Construct grid of ArrayItems.

    Attributes
    ----------
    title : `str`
    labels : `[str]`
        Labels for array items. Length of the

    items : `[ArrayItem]`

    orientation : `Qt.Orientation`
    """

    def __init__(
        self,
        title,
        labels,
        items: typing.List[ArrayItem],
        orientation: Qt.Orientation = Qt.Vertical,
    ):
        """Construct grid item holding ArrayItems.

        Parameters
        ----------
        labels : `[str]`
        *items : `[ArrayItem]`
        orientation : `Qt.Orientation`
        """
        super().__init__()
        self._items = items

        dataLayout = QGridLayout()
        self.setLayout(dataLayout)

        dataLayout.addWidget(QLabel(title), 0, 0)

        def rowcol(r, c):
            return (c, r) if orientation == Qt.Vertical else (r, c)

        for idx, l in enumerate(labels):
            dataLayout.addWidget(QLabel(l), *rowcol(0, idx + 1))
        row = 1
        for c in items:
            if type(c) == ArraySignal:
                for idx, i in enumerate(c.array_items):
                    dataLayout.addWidget(QLabel(c.get_name(idx)), *rowcol(row, 0))
                    for j, i in enumerate(c.get_widgets(len(labels), idx)):
                        dataLayout.addWidget(i, *rowcol(row, j + 1))
                    row += 1
            else:
                dataLayout.addWidget(QLabel(c.get_name()), *rowcol(row, 0))
                for j, i in enumerate(c.get_widgets(len(labels))):
                    dataLayout.addWidget(i, *rowcol(row, j + 1))
                row += 1
