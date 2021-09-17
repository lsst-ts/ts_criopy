# This file is part of M1M3 GUI
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

from PySide2.QtCore import Slot
from PySide2.QtWidgets import QWidget, QPushButton

from lsst.ts.idl.enums.MTM1M3 import DetailedState


class StateEnabledButton(QPushButton):
    def __init__(
        self,
        title,
        m1m3,
        enabledStates=[DetailedState.ACTIVE, DetailedState.ACTIVEENGINEERING],
    ):
        super().__init__(title)
        self._enabledStates = enabledStates

        m1m3.detailedState.connect(self.detailedState)

    @Slot(map)
    def detailedState(self, data):
        self.setEnabled(data.detailedState in self._enabledStates)


class EngineeringButton(StateEnabledButton):
    def __init__(self, title, m1m3):
        super().__init__(
            title,
            m1m3,
            [
                DetailedState.PARKEDENGINEERING,
                DetailedState.RAISINGENGINEERING,
                DetailedState.ACTIVEENGINEERING,
                DetailedState.LOWERINGENGINEERING,
            ],
        )


class StateEnabledWidget(QWidget):
    def __init__(
        self,
        m1m3,
        enabledStates=[DetailedState.ACTIVE, DetailedState.ACTIVEENGINEERING],
    ):
        super().__init__()
        self._enabledStates = enabledStates

        m1m3.detailedState.connect(self.detailedState)

    @Slot(map)
    def detailedState(self, data):
        self.setEnabled(data.detailedState in self._enabledStates)
