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

from PySide2.QtCore import QSize, Signal, Slot
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QHBoxLayout, QWidget

from . import Colors
from .CustomLabels import ColoredButton

__all__ = ["StatusWidget", "StatusBox"]

"""
Widget with rectangles representing various state variables. Values of the
variables are color coded.
"""


class StatusWidget(ColoredButton):
    """
    Widget for a single boolean state.

    Parameters
    ----------
    text : `str`
        Widget text. Displayed in widget.
    object_name : `str`
        Value of the objectName property.
    tooltip : `str`
        Tooltip to be displayed on mouse hover.
    color_true : `QColor`
        Widget color if true value is set.
    color_false : `QColor`
        Widget color if false value is set.
    """

    def __init__(
        self,
        text: str,
        object_name: str,
        tooltip: str,
        color_true: QColor = Colors.OK,
        color_false: QColor = Colors.DISABLED,
    ):
        super().__init__(text)
        self.setObjectName(object_name)
        self.setToolTip(tooltip)
        self._color_true = color_true
        self._color_false = color_false

    def sizeHint(self):
        size = super().sizeHint()
        return QSize(20, size.height())

    def setValue(self, value: bool):
        """Sets new value.

        Parameters
        ----------
        value : `bool`
            New status value.
        """
        self.setColor(self._color_true if value else self._color_false)


class StatusBox(QWidget):
    """
    Widget to display a set of boolean values. Values are color coded.

    Parameters
    ----------
    items : `[StatusWidget]`
        StatusWidget to fill inside the box.
    signale : Signal
        Signal send when new data are available.
    """

    def __init__(self, items, signal: Signal):
        super().__init__()
        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(hbox)

        self._boxes = []
        for i in items:
            hbox.addWidget(i)

        signal.connect(self._data)

    @Slot(map)
    def _data(self, data):
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i).widget()
            if item is not None:
                v = getattr(data, item.objectName())
                item.setValue(v)
