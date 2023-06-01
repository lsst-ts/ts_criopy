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

from asyncqt import asyncSlot
from lsst.ts.idl.enums.MTM1M3 import DetailedState
from lsst.ts.salobj import base
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QButtonGroup,
    QFormLayout,
    QHBoxLayout,
    QLCDNumber,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from lsst.ts import salobj

from ..GUI import Colors, StatusBox, StatusWidget
from ..GUI.SAL import EngineeringButton, SALCommand
from ..GUI.SAL.SALComm import warning


class ApplicationControlWidget(QWidget):
    """Widget with control buttons for M1M3 operations. Buttons are
    disabled/enabled and reasonable defaults sets on DetailedState changes."""

    TEXT_START = "&Start"
    """Constants for button titles. Titles are used to select command send to
    SAL."""
    TEXT_ENABLE = "&Enable"
    TEXT_DISABLE = "&Disable"
    TEXT_STANDBY = "&Standby"
    TEXT_EXIT_CONTROL = "&Exit Control"

    def __init__(self, laser_tracker):
        super().__init__()

        self.laser_tracker = laser_tracker

        self._lastEnabled = None

        self.commandButtons = QButtonGroup(self)
        self.commandButtons.buttonClicked.connect(self._buttonClicked)

        commandLayout = QVBoxLayout()

        def _addButton(text):
            button = QPushButton(text)
            button.setEnabled(False)
            self.commandButtons.addButton(button)
            commandLayout.addWidget(button)
            return button

        _addButton(self.TEXT_START)
        _addButton(self.TEXT_ENABLE)
        _addButton(self.TEXT_STANDBY)

        self.laser_tracker.summaryState.connect(self.summary_state)

        self.setLayout(commandLayout)

    def disableAllButtons(self):
        if self._lastEnabled is None:
            self._lastEnabled = []
            for b in self.commandButtons.buttons():
                self._lastEnabled.append(b.isEnabled())
                b.setEnabled(False)

    def restoreEnabled(self):
        if self._lastEnabled is None:
            return
        bi = 0
        for b in self.commandButtons.buttons():
            b.setEnabled(self._lastEnabled[bi])
            bi += 1

        self._lastEnabled = None

    @asyncSlot()
    async def _buttonClicked(self, bnt):
        text = bnt.text()
        self.disableAllButtons()
        try:
            if text == self.TEXT_START:
                await self.laser_tracker.remote.cmd_start.start()
            elif text == self.TEXT_EXIT_CONTROL:
                await self.laser_tracker.remote.cmd_exitControl.start()
            elif text == self.TEXT_ENABLE:
                await self.laser_tracker.remote.cmd_enable.start()
            elif text == self.TEXT_DISABLE:
                await self.laser_tracker.remote.cmd_disable.start()
            elif text == self.TEXT_STANDBY:
                await self.laser_tracker.remote.cmd_standby.start()
            else:
                raise RuntimeError(f"unassigned command for button {text}")
        except (base.AckError, base.AckTimeoutError) as ackE:
            warning(
                self,
                f"Error executing button {text}",
                f"Error executing button <i>{text}</i>:<br/>{ackE.ackcmd.result}",
            )
        except RuntimeError as rte:
            warning(
                self,
                f"Error executing {text}",
                f"Executing button <i>{text}</i>:<br/>{str(rte)}",
            )
        finally:
            self.restoreEnabled()

    @Slot(map)
    def summary_state(self, data):
        # text mean button is enabled and given text shall be displayed. None
        # for disabled buttons.
        stateMap = {
            salobj.State.STANDBY: [
                self.TEXT_START,
                None,
                self.TEXT_EXIT_CONTROL,
            ],
            salobj.State.DISABLED: [
                None,
                self.TEXT_ENABLE,
                self.TEXT_STANDBY,
            ],
            salobj.State.ENABLED: [
                None,
                self.TEXT_DISABLE,
                None,
            ],
            salobj.State.FAULT: [None, None, self.TEXT_STANDBY],
            salobj.State.OFFLINE: [None, None, None],
        }

        self._lastEnabled = None

        try:
            dbSet = True
            stateData = stateMap[data.summaryState]
            for bi, b in enumerate(self.commandButtons.buttons()):
                text = stateData[bi]
                if text is None:
                    b.setEnabled(False)
                    b.setDefault(False)
                else:
                    b.setText(text)
                    b.setEnabled(True)
                    b.setDefault(dbSet)
                    dbSet = False

        except KeyError:
            print(f"Unhandled summary state {data.summaryState}")
