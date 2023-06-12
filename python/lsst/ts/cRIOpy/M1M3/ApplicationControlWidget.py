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

import typing

from asyncqt import asyncSlot
from lsst.ts.idl.enums.MTM1M3 import DetailedState
from lsst.ts.salobj import base
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QAbstractButton,
    QButtonGroup,
    QFormLayout,
    QHBoxLayout,
    QLCDNumber,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..GUI import Colors, StatusBox, StatusWidget
from ..GUI.SAL import EngineeringButton, SALCommand
from ..GUI.SAL.SALComm import MetaSAL, warning


class HPWarnings:
    def __init__(self) -> None:
        self.faultHigh = self.faultLow = None
        self.warningHigh = self.warningLow = None

        self._faultLow = self._faultLowRaising = None

    def setState(self, state: int) -> None:
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

    def get_color(self, v: float) -> QColor:
        if self.faultLow is None:
            return QColor(128, 128, 128)
        elif v < self.faultLow or v > self.faultHigh:
            return QColor(255, 0, 0)
        elif v < self.warningLow or v > self.warningHigh:
            return QColor(255, 255, 0)
        return QColor(0, 255, 0)

    def min_text(self) -> str:
        if self.faultLow is None:
            return "Event hardpointActuatorSettings wasn't received"
        return f"Fault: {self.faultLow:.2f} Warning: {self.warningLow:.2f}"

    def max_text(self) -> str:
        if self.faultHigh is None:
            return "Event hardpointActuatorSettings wasn't received"
        return f"Warning: {self.warningHigh:.2f} Fault: {self.faultHigh:.2f}"

    def hardpointActuatorSettings(self, data: typing.Any) -> None:
        self.faultHigh = data.airPressureFaultHigh
        self._faultLow = data.airPressureFaultLow
        self._faultLowRaising = data.airPressureFaultLowRaising


class SlewWidget(QWidget):
    """Class to display and interact with slew flag status."""

    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        self.m1m3 = m1m3
        slewLayout = QVBoxLayout()
        slewLayout.addWidget(
            StatusBox(
                [
                    StatusWidget(
                        "S", "slewFlag", "SlewFlag - if booster valves are opened"
                    ),
                    StatusWidget(
                        "U", "userTriggered", "User would like to open booster valves"
                    ),
                    StatusWidget(
                        "FE",
                        "followingErrorTriggered",
                        "Force Actuator Following error values suggests booster valves shall be opened",
                    ),
                    StatusWidget(
                        "A",
                        "accelerometerTriggered",
                        "Accelerometer values suggest booster valve shall be opened",
                    ),
                ],
                self.m1m3.boosterValveStatus,
            )
        )
        self.slewFlagOn = EngineeringButton("Slew ON", m1m3)
        self.slewFlagOff = EngineeringButton("Slew OFF", m1m3)
        pal = self.slewFlagOn.palette()
        self._defaultColor = pal.color(pal.Button)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.slewFlagOn)
        buttonLayout.addWidget(self.slewFlagOff)

        slewLayout.addLayout(buttonLayout)

        self.setLayout(slewLayout)

        self.slewFlagOn.clicked.connect(self.issueCommandSlewFlagOn)
        self.slewFlagOff.clicked.connect(self.issueCommandSlewFlagOff)
        self.m1m3.boosterValveStatus.connect(self.boosterValveStatus)

    @asyncSlot()
    async def issueCommandSlewFlagOn(self) -> None:
        await SALCommand(self, self.m1m3.remote.cmd_boosterValveOpen)

    @asyncSlot()
    async def issueCommandSlewFlagOff(self) -> None:
        await SALCommand(self, self.m1m3.remote.cmd_boosterValveClose)

    @Slot()
    def boosterValveStatus(self, data: typing.Any) -> None:
        palOn = self.slewFlagOn.palette()
        palOff = self.slewFlagOff.palette()
        if data.slewFlag:
            palOn.setColor(palOn.Button, Colors.WARNING)
            palOff.setColor(palOff.Button, self._defaultColor)
        else:
            palOn.setColor(palOn.Button, self._defaultColor)
            palOff.setColor(palOff.Button, Colors.OK)
        self.slewFlagOn.setPalette(palOn)
        self.slewFlagOff.setPalette(palOff)


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

    def __init__(self, m1m3: MetaSAL):
        super().__init__()

        self.m1m3 = m1m3
        self._lastEnabled: list[bool] | None = None
        self._hpWarnings = HPWarnings()

        self.commandButtons = QButtonGroup(self)
        self.commandButtons.buttonClicked.connect(self._buttonClicked)

        commandLayout = QVBoxLayout()

        def _addButton(text: str) -> QPushButton:
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
        self.slewWidget = SlewWidget(m1m3)
        self.slewWidget.setEnabled(False)
        commandLayout.addWidget(self.slewWidget)

        commandLayout.addStretch()

        self.weightSupportedPercent = QProgressBar()
        self.weightSupportedPercent.setOrientation(Qt.Vertical)
        self.weightSupportedPercent.setRange(0, 100)
        self.weightSupportedPercent.setTextVisible(True)
        self.weightSupportedPercent.setFormat("%p%")

        layout = QHBoxLayout()
        layout.addLayout(commandLayout)
        layout.addWidget(self.weightSupportedPercent)

        self.setLayout(layout)

        # connect SAL signals
        self.m1m3.detailedState.connect(self.detailedState)
        self.m1m3.raisingLoweringInfo.connect(self.raisingLoweringInfo)
        self.m1m3.hardpointMonitorData.connect(self.hardpointMonitorData)
        self.m1m3.hardpointActuatorSettings.connect(self.hardpointActuatorSettings)

    def disableAllButtons(self) -> None:
        if self._lastEnabled is None:
            self._lastEnabled = []
            for b in self.commandButtons.buttons():
                self._lastEnabled.append(b.isEnabled())
                b.setEnabled(False)

    def restoreEnabled(self) -> None:
        if self._lastEnabled is None:
            return
        bi = 0
        for b in self.commandButtons.buttons():
            b.setEnabled(self._lastEnabled[bi])
            bi += 1

        self._lastEnabled = None

    @asyncSlot()
    async def _buttonClicked(self, bnt: QAbstractButton) -> None:
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
                f"Error executing {text}",
                f"Executing button <i>{text}</i>:<br/>{str(rte)}",
            )
        finally:
            self.restoreEnabled()

    @Slot()
    def detailedState(self, data: typing.Any) -> None:
        # text mean button is enabled and given text shall be displayed. None
        # for disabled buttons.
        stateMap: dict[int, typing.Any] = {
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
        self.slewWidget.setEnabled(
            not (
                data.detailedState
                in (
                    DetailedState.OFFLINE,
                    DetailedState.STANDBY,
                    DetailedState.DISABLED,
                    DetailedState.FAULT,
                )
            )
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

        self._set_hardpoint_warnings(data.detailedState)

    @Slot()
    def hardpointActuatorSettings(self, data: typing.Any) -> None:
        self._hpWarnings.hardpointActuatorSettings(data)
        state = self.m1m3.remote.evt_detailedState.get()
        if state is not None:
            self._set_hardpoint_warnings(state)

    @Slot()
    def raisingLoweringInfo(self, data: typing.Any) -> None:
        self.weightSupportedPercent.setValue(data.weightSupportedPercent)
        pal = self.supportedNumber.palette()
        if data.weightSupportedPercent == 0:
            col = QColor(255, 0, 0)
        elif data.weightSupportedPercent < 90:
            col = QColor(0, 0, 255)
        elif data.weightSupportedPercent < 100:
            col = QColor(255, 255, 0)
        else:
            col = QColor(0, 255, 0)
        pal.setColor(pal.Background, col)
        self.supportedNumber.display(f"{data.weightSupportedPercent:.02f}")
        self.supportedNumber.setPalette(pal)

    @Slot()
    def hardpointMonitorData(self, data: typing.Any) -> None:
        min_d = min(data.breakawayPressure)
        max_d = max(data.breakawayPressure)

        min_pal = self.minPressure.palette()
        min_pal.setColor(min_pal.Background, self._hpWarnings.get_color(min_d))
        self.minPressure.display(f"{min_d:.02f}")
        self.minPressure.setPalette(min_pal)

        max_pal = self.minPressure.palette()
        max_pal.setColor(max_pal.Background, self._hpWarnings.get_color(max_d))
        self.maxPressure.display(f"{max_d:.02f}")
        self.maxPressure.setPalette(max_pal)

    def _set_hardpoint_warnings(self, state: int) -> None:
        self._hpWarnings.setState(state)
        self.minPressure.setToolTip(self._hpWarnings.min_text())
        self.maxPressure.setToolTip(self._hpWarnings.max_text())
