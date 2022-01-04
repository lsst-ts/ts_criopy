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

from PySide2.QtWidgets import (
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QProgressBar,
    QLCDNumber,
    QFormLayout,
    QSizePolicy,
)
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QColor

from .SALComm import warning

from asyncqt import asyncSlot

from lsst.ts.salobj import base
from lsst.ts.idl.enums.MTM1M3 import DetailedState


class ApplicationControlWidget(QWidget):
    """Widget with control buttons for M1M3 operations. Buttons are disabled/enabled and reasonable defaults sets on DetailedState changes."""

    TEXT_START = "&Start"
    """Constants for button titles. Titles are used to select command send to SAL."""
    TEXT_ENABLE = "&Enable"
    TEXT_DISABLE = "&Disable"
    TEXT_STANDBY = "&Standby"
    TEXT_RAISE = "&Raise M1M3"
    TEXT_ABORT_RAISE = "&Abort M1M3 Raise"
    TEXT_LOWER = "&Lower M1M3"
    TEXT_ENTER_ENGINEERING = "&Enter Engineering"
    TEXT_EXIT_ENGINEERING = "&Exit Engineering"
    TEXT_EXIT_CONTROL = "&Exit Control"
    TEXT_PANIC = "&Panic!"

    def __init__(self, m1m3):
        super().__init__()

        self.m1m3 = m1m3
        self.lastEnabled = None

        def _addButton(text, onClick, default=False):
            button = QPushButton(text)
            button.clicked.connect(onClick)
            button.setEnabled(False)
            button.setAutoDefault(default)
            return button

        self.panicButton = _addButton(self.TEXT_PANIC, self.panic, True)
        pal = self.panicButton.palette()
        pal.setColor(pal.Button, QColor(255, 0, 0))
        self.panicButton.setPalette(pal)
        self.panicButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.startButton = _addButton(self.TEXT_START, self.start, True)
        self.enableButton = _addButton(self.TEXT_ENABLE, self.enable, True)
        self.raiseButton = _addButton(self.TEXT_RAISE, self.raiseControl, True)
        self.engineeringButton = _addButton(
            self.TEXT_ENTER_ENGINEERING, self.engineering
        )
        self.exitButton = _addButton(self.TEXT_STANDBY, self.exit)

        self.supportedNumber = QLCDNumber(6)
        self.supportedNumber.setAutoFillBackground(True)
        self.minPressure = QLCDNumber(6)
        self.minPressure.setAutoFillBackground(True)
        self.maxPressure = QLCDNumber(6)
        self.maxPressure.setAutoFillBackground(True)

        dataLayout = QFormLayout()
        dataLayout.addRow("Supported", self.supportedNumber)
        dataLayout.addRow("Min pressure", self.minPressure)
        dataLayout.addRow("Max pressure", self.maxPressure)

        commandLayout = QVBoxLayout()
        commandLayout.addWidget(self.panicButton, 1)
        commandLayout.addWidget(self.startButton)
        commandLayout.addWidget(self.enableButton)
        commandLayout.addWidget(self.raiseButton)
        commandLayout.addWidget(self.engineeringButton)
        commandLayout.addWidget(self.exitButton)
        commandLayout.addLayout(dataLayout)
        commandLayout.addStretch()

        self.supportPercentage = QProgressBar()
        self.supportPercentage.setOrientation(Qt.Vertical)
        self.supportPercentage.setRange(0, 100)
        self.supportPercentage.setTextVisible(True)
        self.supportPercentage.setFormat("%p%")

        layout = QHBoxLayout()
        layout.addLayout(commandLayout)
        layout.addWidget(self.supportPercentage)

        self.setLayout(layout)

        # connect SAL signals
        self.m1m3.detailedState.connect(self.detailedState)
        self.m1m3.forceActuatorState.connect(self.forceActuatorState)
        self.m1m3.hardpointMonitorData.connect(self.hardpointMonitorData)

    def disableAllButtons(self):
        if self.lastEnabled is None:
            self.lastEnabled = [
                self.startButton.isEnabled(),
                self.enableButton.isEnabled(),
                self.raiseButton.isEnabled(),
                self.engineeringButton.isEnabled(),
                self.exitButton.isEnabled(),
            ]
        self.startButton.setEnabled(False)
        self.enableButton.setEnabled(False)
        self.raiseButton.setEnabled(False)
        self.engineeringButton.setEnabled(False)
        self.exitButton.setEnabled(False)

    def restoreEnabled(self):
        if self.lastEnabled is None:
            return
        self.startButton.setEnabled(self.lastEnabled[0])
        self.enableButton.setEnabled(self.lastEnabled[1])
        self.raiseButton.setEnabled(self.lastEnabled[2])
        self.engineeringButton.setEnabled(self.lastEnabled[3])
        self.exitButton.setEnabled(self.lastEnabled[4])
        self.lastEnabled = None

    async def command(self, button):
        self.disableAllButtons()
        try:
            if button.text() == self.TEXT_PANIC:
                await self.m1m3.remote.cmd_panic.start()
            elif button.text() == self.TEXT_START:
                await self.m1m3.remote.cmd_start.set_start(
                    settingsToApply="Default", timeout=60
                )
            elif button.text() == self.TEXT_EXIT_CONTROL:
                await self.m1m3.remote.cmd_exitControl.start()
            elif button.text() == self.TEXT_ENABLE:
                await self.m1m3.remote.cmd_enable.start()
            elif button.text() == self.TEXT_DISABLE:
                await self.m1m3.remote.cmd_disable.start()
            elif button.text() == self.TEXT_RAISE:
                await self.m1m3.remote.cmd_raiseM1M3.set_start(
                    bypassReferencePosition=False
                )
            elif button.text() == self.TEXT_ABORT_RAISE:
                await self.m1m3.remote.cmd_abortRaiseM1M3.start()
            elif button.text() == self.TEXT_LOWER:
                await self.m1m3.remote.cmd_lowerM1M3.start()
            elif button.text() == self.TEXT_ENTER_ENGINEERING:
                await self.m1m3.remote.cmd_enterEngineering.start()
            elif button.text() == self.TEXT_EXIT_ENGINEERING:
                await self.m1m3.remote.cmd_exitEngineering.start()
            elif button.text() == self.TEXT_STANDBY:
                await self.m1m3.remote.cmd_standby.start()
        except base.AckError as ackE:
            warning(
                self,
                f"Error executing button {button.text()}",
                f"Error executing button <i>{button.text()}</i>:<br/>{ackE.ackcmd.result}",
            )
        except RuntimeError as rte:
            warning(
                self,
                f"Error executing {button.text()}",
                f"Executing button <i>{button.text()}</i>:<br/>{str(rte)}",
            )
        finally:
            self.restoreEnabled()

    @asyncSlot()
    async def panic(self):
        await self.command(self.panicButton)

    @asyncSlot()
    async def start(self):
        await self.command(self.startButton)

    @asyncSlot()
    async def enable(self):
        await self.command(self.enableButton)

    @asyncSlot()
    async def raiseControl(self):
        await self.command(self.raiseButton)

    @asyncSlot()
    async def engineering(self):
        await self.command(self.engineeringButton)

    @asyncSlot()
    async def exit(self):
        await self.command(self.exitButton)

    def _setTextEnable(self, button, text):
        button.setText(text)
        button.setEnabled(True)

    @Slot(map)
    def detailedState(self, data):
        self.lastEnabled = None
        if data.detailedState == DetailedState.DISABLED:
            self.panicButton.setEnabled(True)
            self.raiseButton.setEnabled(False)
            self.engineeringButton.setEnabled(False)
            self._setTextEnable(self.enableButton, self.TEXT_ENABLE)
            self._setTextEnable(self.exitButton, self.TEXT_STANDBY)
            self.enableButton.setDefault(True)
        elif data.detailedState == DetailedState.FAULT:
            self.panicButton.setEnabled(True)
            self._setTextEnable(self.startButton, self.TEXT_STANDBY)
            self.startButton.setDefault(True)
        elif data.detailedState == DetailedState.OFFLINE:
            self.startButton.setEnabled(False)
        elif data.detailedState == DetailedState.STANDBY:
            self.panicButton.setEnabled(False)
            self._setTextEnable(self.startButton, self.TEXT_START)
            self._setTextEnable(self.exitButton, self.TEXT_EXIT_CONTROL)
            self.startButton.setDefault(True)
        elif data.detailedState == DetailedState.PARKED:
            self.panicButton.setEnabled(True)
            self._setTextEnable(self.enableButton, self.TEXT_DISABLE)
            self._setTextEnable(self.raiseButton, self.TEXT_RAISE)
            self._setTextEnable(self.engineeringButton, self.TEXT_ENTER_ENGINEERING)
            self.exitButton.setEnabled(False)
            self.raiseButton.setDefault(True)
        elif data.detailedState == DetailedState.RAISING:
            self.panicButton.setEnabled(True)
            self._setTextEnable(self.raiseButton, self.TEXT_ABORT_RAISE)
            self.engineeringButton.setEnabled(False)
            self.raiseButton.setDefault(True)
        elif data.detailedState == DetailedState.ACTIVE:
            self.panicButton.setEnabled(True)
            self._setTextEnable(self.raiseButton, self.TEXT_LOWER)
            self._setTextEnable(self.engineeringButton, self.TEXT_ENTER_ENGINEERING)
            self.engineeringButton.setEnabled(True)
        elif data.detailedState == DetailedState.LOWERING:
            self.panicButton.setEnabled(True)
            pass
        elif data.detailedState == DetailedState.PARKEDENGINEERING:
            self.panicButton.setEnabled(True)
            self.enableButton.setEnabled(False)
            self._setTextEnable(self.raiseButton, self.TEXT_RAISE)
            self._setTextEnable(self.engineeringButton, self.TEXT_EXIT_ENGINEERING)
        elif data.detailedState == DetailedState.RAISINGENGINEERING:
            self.panicButton.setEnabled(True)
            self._setTextEnable(self.raiseButton, self.TEXT_ABORT_RAISE)
            self.engineeringButton.setEnabled(False)
        elif data.detailedState == DetailedState.ACTIVEENGINEERING:
            self.panicButton.setEnabled(True)
            self._setTextEnable(self.raiseButton, self.TEXT_LOWER)
            self.engineeringButton.setEnabled(True)
            self._setTextEnable(self.engineeringButton, self.TEXT_EXIT_ENGINEERING)
        elif data.detailedState == DetailedState.LOWERINGENGINEERING:
            self.panicButton.setEnabled(True)
            pass
        elif data.detailedState == DetailedState.LOWERINGFAULT:
            self.panicButton.setEnabled(False)
            self._setTextEnable(self.exitButton, self.TEXT_STANDBY)
        elif data.detailedState == DetailedState.PROFILEHARDPOINTCORRECTIONS:
            pass
        else:
            print(f"Unhandled detailed state {data.detailedState}")

    @Slot(map)
    def forceActuatorState(self, data):
        self.supportPercentage.setValue(data.supportPercentage)
        pal = self.supportedNumber.palette()
        if data.supportPercentage == 0:
            col = QColor(255, 0, 0)
        elif data.supportPercentage < 90:
            col = QColor(0, 0, 255)
        elif data.supportPercentage < 100:
            col = QColor(255, 255, 0)
        else:
            col = QColor(0, 255, 0)
        pal.setColor(pal.Background, col)
        self.supportedNumber.display(f"{data.supportPercentage:.02f}")
        self.supportedNumber.setPalette(pal)

    @Slot(map)
    def hardpointMonitorData(self, data):
        min_d = min(data.breakawayPressure)
        max_d = max(data.breakawayPressure)

        def _getColor(v):
            if v < 110 or v > 127:
                return QColor(255, 0, 0)
            elif v < 115 or v > 125:
                return QColor(255, 255, 0)
            return QColor(0, 255, 0)

        min_pal = self.minPressure.palette()
        min_pal.setColor(min_pal.Background, _getColor(min_d))
        self.minPressure.display(f"{min_d:.02f}")
        self.minPressure.setPalette(min_pal)

        max_pal = self.minPressure.palette()
        max_pal.setColor(max_pal.Background, _getColor(max_d))
        self.maxPressure.display(f"{max_d:.02f}")
        self.maxPressure.setPalette(max_pal)
