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

import typing

from lsst.ts.idl.enums.MTM1M3 import DetailedState
from PySide2.QtCore import Signal, Slot
from PySide2.QtWidgets import QPushButton, QWidget

from ...salcomm import MetaSAL

__all__ = [
    "SignalButton",
    "DetailedStateEnabledButton",
    "EngineeringButton",
    "StateEnabledWidget",
]


class SignalButton(QPushButton):
    """Push button enabled by signal.value in given state.

    Parameters
    ----------
    title : `str`
        Button title. Passed to QPushButton.
    signal : `PySide2.QtCore.Signal`
        Signal
    variable : `str`
        Name of variable governing enable/disable switching. Part of signal.
    enabledValues : `[]`
        When variable value is in this list, button is enabled. It is disabled
        otherwise.
    """

    def __init__(
        self,
        title: str,
        signal: Signal,
        variable: str,
        enabledValues: list[str],
    ):
        super().__init__(title)
        self.__correctState = False
        self.__askedEnabled = False
        self._variable = variable
        self._enabledValues = enabledValues

        self.setEnabled()

        signal.connect(self.__update)  # type: ignore

    def setEnabled(self, enabled: bool = True) -> None:
        self.__askedEnabled = enabled
        self.__updateEnabled()

    def setDisabled(self, disabled: bool = True) -> None:
        self.__askedEnabled = not (disabled)
        self.__updateEnabled()

    @Slot()
    def __update(self, data: dict) -> None:
        self.__correctState = getattr(data, self._variable) in self._enabledValues
        self.__updateEnabled()

    def __updateEnabled(self) -> None:
        super().setEnabled(self.__correctState and self.__askedEnabled)


class DetailedStateEnabledButton(SignalButton):
    """Push button enabled by detailed state.

    Parameters
    ----------
    title : `str`
        Button title. Passed to QPushButton.
    m1m3 : `MetaSAL`
        SAL. Its detailed state is connected to a handler
        enabling/disabling the button.
    enabledStates : `[DetailedState.*]`
        States in which button shall be enabled. It will be disabled in all
        other states.
    """

    def __init__(
        self,
        title: str,
        m1m3: MetaSAL,
        enabledStates: list[DetailedState] = [
            DetailedState.ACTIVE,
            DetailedState.ACTIVEENGINEERING,
        ],
    ):
        super().__init__(title, m1m3.detailedState, "detailedState", enabledStates)


class EngineeringButton(DetailedStateEnabledButton):
    """Push button enabled only in mirror engineering states.

    Parameters
    ----------
    title : `str`
        Button title. Passed to QPushButton.
    m1m3 : `MetaSAL`
        SAL. When detailed state is in one of the engineering states,
        button is enabled. It is disabled otherwise.
    """

    def __init__(self, title: str, m1m3: MetaSAL):
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
    """Widget linked to mirror detailed state, enabled only when mirror is in
    specified state(s).

    Parameters
    ----------
    m1m3 : `MetaSAL`
        SAL. When detailed state is in one of the enabledStates, widget is
        enabled. It is disabled otehrwise.
    enabledStates : `[DetailedState]`
        States in which the widget is enabled.
    """

    def __init__(
        self,
        m1m3: MetaSAL,
        enabledStates: list[DetailedState] = [
            DetailedState.ACTIVE,
            DetailedState.ACTIVEENGINEERING,
        ],
    ) -> None:
        super().__init__()
        self.setEnabled(False)
        self._enabledStates = enabledStates

        m1m3.detailedState.connect(self.detailedState)

    @Slot()
    def detailedState(self, data: typing.Any) -> None:
        self.setEnabled(data.detailedState in self._enabledStates)
