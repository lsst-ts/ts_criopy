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

from PySide2.QtCore import Signal
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QVBoxLayout, QWidget

from . import ColoredButton

__all__ = ["FieldButton", "TopicStatusLabel"]


class FieldButton(ColoredButton):
    """Display single field in topic.

    Parameters
    ----------
    field : `str`
        Field name. Used to retrieve value from new signal data.
    inactive : `(str, QColor)`
        Button text and color when value is false. If color is None, use
        default color.
    active : `(str, QColor)`
        Button text and color when value is true. If color is None, use default
        color.
    """

    def __init__(
        self, field: str, inactive: tuple[str, QColor], active: tuple[str, QColor]
    ):
        super().__init__("---")
        self.field = field
        self.attributes = {False: inactive, True: active}

    def setValue(self, value: bool) -> None:
        self.setTextColor(*self.attributes[value])


class TopicStatusLabel(ColoredButton):
    """
    Button tied to data containing some boolean fields. Passed an array of
    FieldButton. The entries are used to construct a window appearing after
    button is clicked.

    Button text and color is set to match text and color of the first true
    field among fields. If all fields values are false, button text is set to
    "---" and color is set to match default color.

    Parameters
    ----------
    signal : `Signal`
        Signal triggered when new data arrives.
    title : `str`
        Sub-window title.
    fields : `[FieldButton]`
        Fields in signal to display in sub-window.
    """

    def __init__(self, signal: Signal, title: str, fields: list[FieldButton]):
        super().__init__("---")
        self._title = title
        self._window = None
        self.fields = fields

        self.clicked.connect(self._clicked)
        signal.connect(self.data)  # type: ignore

    def _clicked(self):
        if self._window is None:
            self._window = QWidget()
            self._window.setWindowTitle(self._title)
            layout = QVBoxLayout()
            for f in self.fields:
                layout.addWidget(f)
            self._window.setLayout(layout)
        self._window.show()

    def data(self, data):
        updated = False
        for f in self.fields:
            v = getattr(data, f.field)
            f.setValue(v)
            if v is True and updated is False:
                self.setTextColor(*(f.attributes[True]))
                updated = True
        if updated is False:
            self.setTextColor("---", None)
