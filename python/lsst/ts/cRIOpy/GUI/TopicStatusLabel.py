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
from PySide2.QtWidgets import QWidget, QVBoxLayout

from . import ColoredButton

__all__ = ["FieldButton", "TopicStatusLabel"]


class FieldButton(ColoredButton):
    """Display single field in topic.

    Parameters
    ----------
    field : `str`
    inactive : `(str, QColor)`
    active : `(str, QColor)`
    """

    def __init__(self, field: str, inactive: (str, str), active: (str, str)):
        super().__init__("---")
        self.field = field
        self.attributes = {False: inactive, True: active}

    def setValue(self, value: bool) -> None:
        self.setTextColor(*self.attributes[value])


class TopicStatusLabel(ColoredButton):
    def __init__(self, signal: Signal, fields: [FieldButton]):
        super().__init__("---")
        self.fields = fields
        self.window = None

        self.clicked.connect(self._clicked)
        signal.connect(self.data)

    def _clicked(self):
        if self.window is None:
            self.window = QWidget()
            # self.setWindowTitle(
            layout = QVBoxLayout()
            for f in self.fields:
                layout.addWidget(f)
            self.window.setLayout(layout)
        self.window.show()

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
