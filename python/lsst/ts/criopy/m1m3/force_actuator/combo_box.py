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

from PySide2.QtWidgets import QComboBox

from ...m1m3_fa_table import FATABLE

__all__ = ["ComboBox"]


class ComboBox(QComboBox):
    """Allows user to select force actuator. Either its ID can be typed, or it
    can be selected from a listbox. See QComboBox for signals etc."""

    def __init__(self) -> None:
        super().__init__()
        self.setEditable(True)
        self.lineEdit().setInputMask("999")
        for row in FATABLE:
            self.addItem(str(row.actuator_id))
