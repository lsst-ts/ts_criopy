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
    """Push button enabled by state.

    Parameters
    ----------
    title : `str`
        Button title. Passed to QPushButton.
    m1m3 : `SALComm`
        SALComm. Its detailed state is connected to a handler enabling/disabling the button.
    enabledStates : `[DetailedState.*]`
        States in which button shall be enabled. It will be disabled in all other states.
    """

    def __init__(
        self,
        title,
        m1m3,
        enabledStates=[DetailedState.ACTIVE, DetailedState.ACTIVEENGINEERING],
    ):
        super().__init__(title)
        self.__correctState = False
        self.__askedEnabled = False
        self.setEnabled()
        self._enabledStates = enabledStates

        m1m3.detailedState.connect(self.detailedState)

    def setEnabled(self, enabled=True):
        self.__askedEnabled = enabled
        self.__updateEnabled()

    def setDisabled(self, disabled=True):
        self.__askedEnabled = not (disabled)
        self.__updateEnabled()

    @Slot(map)
    def detailedState(self, data):
        self.__correctState = data.detailedState in self._enabledStates
        self.__updateEnabled()

    def __updateEnabled(self):
        super().setEnabled(self.__correctState and self.__askedEnabled)


class EngineeringButton(StateEnabledButton):
    """Push button enabled only in mirror engineering states.

    Parameters
    ----------
    title : `str`
        Button title. Passed to QPushButton.
    m1m3 : `SALComm`
        SALComm. When detailed state is in one of the engineering states,
        button is enabled. It is disabled otherwise.
    """

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
    """Widget linked to mirror detailed state, enabled only when mirror is in specified state(s).

    Parameters
    ----------
    m1m3 : `SALComm`
        SALComm. When detailed state is in one of the enabledStates, widget is
        enabled. It is disabled otehrwise.
    enabledStates : `[DetailedState]`
        States in which the widget is enabled.
    """

    def __init__(
        self,
        m1m3,
        enabledStates=[DetailedState.ACTIVE, DetailedState.ACTIVEENGINEERING],
    ):
        super().__init__()
        self.setEnabled(False)
        self._enabledStates = enabledStates

        m1m3.detailedState.connect(self.detailedState)

    @Slot(map)
    def detailedState(self, data):
        self.setEnabled(data.detailedState in self._enabledStates)
