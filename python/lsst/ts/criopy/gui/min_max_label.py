# This file is part of M1M3 SS GUI.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from lsst.ts.salobj import BaseMsgType
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLabel


class MinLabel(type(QLabel)):  # type: ignore
    def __new__(cls, classname, bases, dictionary):  # type: ignore

        dictionary["_current_data"] = None

        @Slot()
        def new_data(self, data: BaseMsgType) -> None:  # type: ignore
            if self._current_data is None:
                self._current_data = data
            else:
                if getattr(data, self._field) < getattr(
                    self._current_data, self._field
                ):
                    self._current_data = data
                else:
                    return

            self.setValue(getattr(self._current_data, self._field))

        newclass = super(MinLabel, cls).__new__(cls, classname, bases, dictionary)
        setattr(newclass, new_data.__name__, new_data)

        return newclass
