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

from .CustomLabels import DockWindow
from .SALComm import SALCommand

from lsst.ts.salobj import State

from PySide2.QtCore import Slot
from PySide2.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout, QFormLayout

from asyncqt import asyncSlot


def summaryStateString(summaryState):
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
    """Widget to display and manipulate M1M3 TS states."""

    def __init__(self, m1m3ts):
        super().__init__("Status")
        self.m1m3ts = m1m3ts
        self.setMaximumWidth(100)

        layout = QVBoxLayout()

        formLayout = QFormLayout()
        self.stateLabel = QLabel("---")
        formLayout.addRow("State", self.stateLabel)

        layout.addLayout(formLayout)

        def _addButton(text, onClick, default=False):
            button = QPushButton(text)
            button.clicked.connect(onClick)
            # button.setEnabled(False)
            button.setAutoDefault(default)
            layout.addWidget(button)
            return button

        _addButton("Start", self.start, True)
        _addButton("Standby", self.standby)
        _addButton("Exit Control", self.exitControl)

        widget = QWidget()
        widget.setLayout(layout)

        m1m3ts.summaryState.connect(self.summaryState)

        self.setWidget(widget)

    @SALCommand
    def _start(self, **kwargs):
        return self.m1m3ts.remote.cmd_start

    @asyncSlot()
    async def start(self):
        await self._start(settingsToApply="Default")

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
