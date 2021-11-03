# This file is part of M1M3 TS GUI.
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

# You should have received a copy of the GNU General Public License along with
# this program.If not, see <https://www.gnu.org/licenses/>.

__all__ = ["summaryStateString", "ThermalStatesDock"]

from ..GUI import DockWindow, SALCommand

from lsst.ts.salobj import State

from PySide2.QtCore import Slot
from PySide2.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout, QFormLayout

from asyncqt import asyncSlot


def summaryStateString(summaryState):
    """Returns HTML string sumarizing device state.

    Parameters
    ----------
    summaryState : `int`
        Current device summary state.

    Returns
    -------
    string : `str`
        HTML text (including color) of device state.
    """
    _map = {
        State.OFFLINE: "<font color='red'>Offline</font>",
        State.STANDBY: "Standby",
        State.DISABLED: "Disabled",
        State.ENABLED: "<font color='green'>Enabled</font>",
        State.FAULT: "<font color='red'>Fault</font>",
    }
    try:
        return _map[summaryState]
    except KeyError:
        return f"<font color='red'>Unknow : {summaryState}</font>"


class ThermalStatesDock(DockWindow):
    """DockWidget to display and manipulate M1M3 TS states.

    Paramaters
    ----------
    m1m3ts : `SALComm`
        SALComm object, connection to M1M3 TS.
    """

    def __init__(self, m1m3ts):
        super().__init__("Status")
        self.m1m3ts = m1m3ts
        self.setMaximumWidth(100)

        layout = QVBoxLayout()

        self._controlButtons = []

        def _addButton(text, onClick, default=False):
            button = QPushButton(text)
            button.clicked.connect(onClick)
            button.setEnabled(False)
            button.setAutoDefault(default)
            layout.addWidget(button)
            self._controlButtons.append(button)
            return button

        _addButton("Start", self.start, True)
        _addButton("Enable", self.enable)
        self.engineeringButton = _addButton(
            "Enable Engineering", self.setEngineeringMode
        )
        _addButton("Disable", self.disable)
        _addButton("Standby", self.standby)
        _addButton("Exit Control", self.exitControl)

        formLayout = QFormLayout()
        self.stateLabel = QLabel("---")
        formLayout.addRow("State", self.stateLabel)

        layout.addLayout(formLayout)

        widget = QWidget()
        widget.setLayout(layout)

        m1m3ts.summaryState.connect(self.summaryState)
        m1m3ts.engineeringMode.connect(self.engineeringMode)

        self.setWidget(widget)

    def setButtonsToState(self, state):
        """Sets button for given state. Changes button enabled/disabled to
        actions allowed at the given state.

        Parameters
        ----------
        state : `int`
            Current CSC state."""
        _bm = {
            State.OFFLINE: [False, False, False, False, False, False],
            State.STANDBY: [True, False, False, False, False, True],
            State.DISABLED: [False, True, False, False, True, False],
            State.ENABLED: [False, False, True, True, False, False],
            State.FAULT: [False, False, False, False, True, False],
        }
        try:
            bs = _bm[state]
            for bi in range(len(self._controlButtons)):
                self._controlButtons[bi].setEnabled(bs[bi])
        except KeyError as ke:
            print(f"Undefined buttonstate: {state} - {str(ke)}")

    @SALCommand
    def _start(self, **kwargs):
        return self.m1m3ts.remote.cmd_start

    @asyncSlot()
    async def start(self):
        await self._start(settingsToApply="Default")

    @SALCommand
    def _enable(self, **kwargs):
        return self.m1m3ts.remote.cmd_enable

    @asyncSlot()
    async def enable(self):
        await self._enable()

    @SALCommand
    def _setEngineeringMode(self, **kwargs):
        return self.m1m3ts.remote.cmd_setEngineeringMode

    @asyncSlot()
    async def setEngineeringMode(self):
        await self._setEngineeringMode(enableEngineeringMode=self._)

    @SALCommand
    def _disable(self, **kwargs):
        return self.m1m3ts.remote.cmd_disable

    @asyncSlot()
    async def disable(self):
        await self._disable()

    @SALCommand
    def _standby(self, **kwargs):
        return self.m1m3ts.remote.cmd_standby

    @asyncSlot()
    async def standby(self):
        await self._standby()

    @SALCommand
    def _exitControl(self, **kwargs):
        return self.m1m3ts.remote.cmd_exitControl

    @asyncSlot()
    async def exitControl(self):
        await self._exitControl()

    @Slot(map)
    def summaryState(self, data):
        self.stateLabel.setText(summaryStateString(data.summaryState))
        self.setButtonsToState(data.summaryState)
