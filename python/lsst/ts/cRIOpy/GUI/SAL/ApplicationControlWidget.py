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
    QButtonGroup,
)
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QColor
from asyncqt import asyncSlot

from lsst.ts.salobj import base
from lsst.ts.idl.enums.MTM1M3 import DetailedState

from .SALComm import warning


class HPWarnings:
    def __init__(self):
        self.faultHigh = self.faultLow = None
        self.warningHigh = self.warningLow = None

        self._faultLow = self._faultLowRaising = None

    def setState(self, state):
        """Change low limits according to sensed state.

        Note
        ----
        As that needs to be called before tool tips are set, do not hook that
        directly to detailedState signal.

        Parameters
        ----------
        state : `int`
            New CSC state.
        """
        if self.faultHigh is None:
            return

        rangeRatio = 0.1
        if state == DetailedState.RAISING or state == DetailedState.RAISINGENGINEERING:
            self.faultLow = self._faultLowRaising
        else:
            self.faultLow = self._faultLow

        errorRange = self.faultHigh - self.faultLow
        self.warningLow = self.faultLow + errorRange * rangeRatio
        self.warningHigh = self.faultHigh - errorRange * rangeRatio

    def getColor(self, v):
        if self.faultLow is None:
            return QColor(128, 128, 128)
        elif v < self.faultLow or v > self.faultHigh:
            return QColor(255, 0, 0)
        elif v < self.warningLow or v > self.warningHigh:
            return QColor(255, 255, 0)
        return QColor(0, 255, 0)

    def minText(self):
        if self.faultLow is None:
            return "Event hardpointActuatorSettings wasn't received"
        return f"Fault: {self.faultLow:.2f} Warning: {self.warningLow:.2f}"

    def maxText(self):
        if self.faultHigh is None:
            return "Event hardpointActuatorSettings wasn't received"
        return f"Warning: {self.warningHigh:.2f} Fault: {self.faultHigh:.2f}"

    def hardpointActuatorSettings(self, data):
        self.faultHigh = data.airPressureFaultHigh
        self._faultLow = data.airPressureFaultLow
        self._faultLowRaising = data.airPressureFaultLowRaising


class ApplicationControlWidget(QWidget):
    """Widget with control buttons for M1M3 operations. Buttons are
    disabled/enabled and reasonable defaults sets on DetailedState changes."""

    TEXT_START = "&Start"
    """Constants for button titles. Titles are used to select command send to
    SAL."""
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
        self._lastEnabled = None
        self._hpWarnings = HPWarnings()

        self.commandButtons = QButtonGroup(self)
        self.commandButtons.buttonClicked.connect(self._buttonClicked)

        commandLayout = QVBoxLayout()

        def _addButton(text):
            button = QPushButton(text)
            button.setEnabled(False)
            self.commandButtons.addButton(button)
            commandLayout.addWidget(button)
            return button

        panicButton = _addButton(self.TEXT_PANIC)
        pal = panicButton.palette()
        pal.setColor(pal.Button, QColor(255, 0, 0))
        panicButton.setPalette(pal)
        panicButton.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        _addButton(self.TEXT_START)
        _addButton(self.TEXT_ENABLE)
        _addButton(self.TEXT_RAISE)
        _addButton(self.TEXT_ENTER_ENGINEERING)
        _addButton(self.TEXT_STANDBY)

        self.supportedNumber = QLCDNumber(6)
        self.supportedNumber.setAutoFillBackground(True)
        self.minPressure = QLCDNumber(6)
        self.minPressure.setAutoFillBackground(True)
        self.maxPressure = QLCDNumber(6)
        self.maxPressure.setAutoFillBackground(True)

        self.minPressure.setToolTip("Limits weren't (yet) received")
        self.maxPressure.setToolTip("Limits weren't (yet) received")

        dataLayout = QFormLayout()
        dataLayout.addRow("Supported", self.supportedNumber)
        dataLayout.addRow("Min pressure", self.minPressure)
        dataLayout.addRow("Max pressure", self.maxPressure)

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
        self.m1m3.hardpointActuatorSettings.connect(self.hardpointActuatorSettings)

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
            if text == self.TEXT_PANIC:
                await self.m1m3.remote.cmd_panic.start()
            elif text == self.TEXT_START:
                await self.m1m3.remote.cmd_start.set_start(
                    configurationOverride="Default", timeout=60
                )
            elif text == self.TEXT_EXIT_CONTROL:
                await self.m1m3.remote.cmd_exitControl.start()
            elif text == self.TEXT_ENABLE:
                await self.m1m3.remote.cmd_enable.start()
            elif text == self.TEXT_DISABLE:
                await self.m1m3.remote.cmd_disable.start()
            elif text == self.TEXT_RAISE:
                await self.m1m3.remote.cmd_raiseM1M3.set_start(
                    bypassReferencePosition=False
                )
            elif text == self.TEXT_ABORT_RAISE:
                await self.m1m3.remote.cmd_abortRaiseM1M3.start()
            elif text == self.TEXT_LOWER:
                await self.m1m3.remote.cmd_lowerM1M3.start()
            elif text == self.TEXT_ENTER_ENGINEERING:
                await self.m1m3.remote.cmd_enterEngineering.start()
            elif text == self.TEXT_EXIT_ENGINEERING:
                await self.m1m3.remote.cmd_exitEngineering.start()
            elif text == self.TEXT_STANDBY:
                await self.m1m3.remote.cmd_standby.start()
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
                f"Error executing {text()}",
                f"Executing button <i>{text()}</i>:<br/>{str(rte)}",
            )
        finally:
            self.restoreEnabled()

    @Slot(map)
    def detailedState(self, data):
        # text mean button is enabled and given text shall be displayed. None
        # for disabled buttons.
        stateMap = {
            DetailedState.STANDBY: [
                self.TEXT_START,
                None,
                None,
                None,
                self.TEXT_EXIT_CONTROL,
            ],
            DetailedState.DISABLED: [
                None,
                self.TEXT_ENABLE,
                None,
                None,
                self.TEXT_STANDBY,
            ],
            DetailedState.FAULT: [self.TEXT_STANDBY, None, None, None, None],
            DetailedState.OFFLINE: [None, None, None, None, None],
            DetailedState.PARKED: [
                None,
                self.TEXT_DISABLE,
                self.TEXT_RAISE,
                self.TEXT_ENTER_ENGINEERING,
                None,
            ],
            DetailedState.PARKEDENGINEERING: [
                None,
                self.TEXT_DISABLE,
                self.TEXT_RAISE,
                self.TEXT_EXIT_ENGINEERING,
                None,
            ],
            DetailedState.RAISING: [None, self.TEXT_ABORT_RAISE, None, None, None],
            DetailedState.RAISINGENGINEERING: [
                None,
                self.TEXT_ABORT_RAISE,
                None,
                None,
                None,
            ],
            DetailedState.ACTIVE: [
                None,
                None,
                self.TEXT_LOWER,
                self.TEXT_ENTER_ENGINEERING,
                None,
            ],
            DetailedState.ACTIVEENGINEERING: [
                None,
                None,
                self.TEXT_LOWER,
                self.TEXT_EXIT_ENGINEERING,
                None,
            ],
            DetailedState.LOWERING: [None, None, None, None, None],
            DetailedState.LOWERINGENGINEERING: [None, None, None, None, None],
            DetailedState.LOWERINGFAULT: [None, None, None, None, None],
            DetailedState.PROFILEHARDPOINTCORRECTIONS: [None, None, None, None, None],
        }

        self._lastEnabled = None

        self.commandButtons.buttons()[0].setEnabled(
            not (data.detailedState == DetailedState.OFFLINE)
        )

        try:
            dbSet = True
            stateData = stateMap[data.detailedState]
            bi = 0
            # we don't care about panic button..that's handled above
            for b in self.commandButtons.buttons()[1:]:
                text = stateData[bi]
                if text is None:
                    b.setEnabled(False)
                    b.setDefault(False)
                else:
                    b.setText(text)
                    b.setEnabled(True)
                    b.setDefault(dbSet)
                    dbSet = False
                bi += 1

        except KeyError:
            print(f"Unhandled detailed state {data.detailedState}")

        self._setHpWarnings(data.detailedState)

    @Slot(map)
    def hardpointActuatorSettings(self, data):
        self._hpWarnings.hardpointActuatorSettings(data)
        state = self.m1m3.remote.evt_detailedState.get()
        if state is not None:
            self._setHpWarnings(state)

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

        min_pal = self.minPressure.palette()
        min_pal.setColor(min_pal.Background, self._hpWarnings.getColor(min_d))
        self.minPressure.display(f"{min_d:.02f}")
        self.minPressure.setPalette(min_pal)

        max_pal = self.minPressure.palette()
        max_pal.setColor(max_pal.Background, self._hpWarnings.getColor(max_d))
        self.maxPressure.display(f"{max_d:.02f}")
        self.maxPressure.setPalette(max_pal)

    def _setHpWarnings(self, state):
        self._hpWarnings.setState(state)
        self.minPressure.setToolTip(self._hpWarnings.minText())
        self.maxPressure.setToolTip(self._hpWarnings.maxText())
