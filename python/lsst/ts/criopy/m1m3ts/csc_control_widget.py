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


from lsst.ts.salobj import BaseMsgType
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QPushButton
from qasync import asyncSlot

from ..gui.sal import CSCControlWidget
from ..salcomm import MetaSAL, command


class EnterExitEngineeringButton(QPushButton):
    ENTER_ENGINEERING = "Enter Engineering"
    EXIT_ENGINEERING = "Exit Engineering"

    def __init__(self, m1m3ts: MetaSAL):
        super().__init__(self.ENTER_ENGINEERING)
        self.m1m3ts = m1m3ts

        self.m1m3ts.engineeringMode.connect(self.engineering_mode)
        self.clicked.connect(self._clicked)

    @asyncSlot()
    async def _clicked(self) -> None:
        await command(
            self,
            self.m1m3ts.remote.cmd_setEngineeringMode,
            enableEngineeringMode=self.text() == self.ENTER_ENGINEERING,
        )

    @Slot()
    def engineering_mode(self, data: BaseMsgType) -> None:
        self.setText(
            self.EXIT_ENGINEERING if data.engineeringMode else self.ENTER_ENGINEERING
        )


class M1M3TSCSCControlWidget(CSCControlWidget):
    def __init__(self, m1m3ts: MetaSAL):
        super().__init__(m1m3ts)

        self.insert_widget(EnterExitEngineeringButton(m1m3ts), 1)
