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

from lsst.ts.idl.enums.MTM1M3 import DetailedState
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLCDNumber,
    QProgressBar,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ..gui import ColoredButton, Colors, StatusBox, StatusWidget
from ..gui.sal import ActiveButton, CSCControlWidget, EngineeringButton
from ..salcomm import MetaSAL, command


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
                        "O",
                        "opened",
                        "Booster valves are opened",
                    ),
                    None,
                    StatusWidget(
                        "S",
                        "slewTriggered",
                        "TMA is slewing, booster valve opened",
                    ),
                    StatusWidget(
                        "U",
                        "userTriggered",
                        "User would like to open booster valves",
                    ),
                    StatusWidget(
                        "FE",
                        "followingErrorTriggered",
                        "Force Actuator Following error values suggests booster"
                        " valves shall be opened",
                    ),
                    StatusWidget(
                        "A",
                        "accelerometerTriggered",
                        "Accelerometer values suggest booster valve shall be" " opened",
                    ),
                ],
                self.m1m3.boosterValveStatus,
            )
        )

        self.slew_flag_on = ActiveButton("Slew ON", m1m3)
        self.slew_flag_off = ActiveButton("Slew OFF", m1m3)

        pal = self.slew_flag_on.palette()
        self._default_color = pal.color(pal.Button)

        self.boosterOpen = EngineeringButton("Booster Open", m1m3)
        self.boosterClose = EngineeringButton("Booster Close", m1m3)

        boosterLayout = QHBoxLayout()
        boosterLayout.addWidget(self.boosterOpen)
        boosterLayout.addWidget(self.boosterClose)

        slewLayout.addLayout(boosterLayout)

        slewControlLayout = QHBoxLayout()
        slewControlLayout.addWidget(self.slew_flag_on)
        slewControlLayout.addWidget(self.slew_flag_off)

        slewLayout.addLayout(slewControlLayout)

        self.setLayout(slewLayout)

        self.slew_flag_on.clicked.connect(self.issueCommandSlewFlagOn)
        self.slew_flag_off.clicked.connect(self.issueCommandSlewFlagOff)

        self.boosterOpen.clicked.connect(self.issueCommandBoosterOpen)
        self.boosterClose.clicked.connect(self.issueCommandBoosterClose)

        self.m1m3.forceControllerState.connect(self.force_controller_state)

    @asyncSlot()
    async def issueCommandSlewFlagOn(self) -> None:
        await command(self, self.m1m3.remote.cmd_setSlewFlag)

    @asyncSlot()
    async def issueCommandSlewFlagOff(self) -> None:
        await command(self, self.m1m3.remote.cmd_clearSlewFlag)

    @asyncSlot()
    async def issueCommandBoosterOpen(self) -> None:
        await command(self, self.m1m3.remote.cmd_boosterValveOpen)

    @asyncSlot()
    async def issueCommandBoosterClose(self) -> None:
        await command(self, self.m1m3.remote.cmd_boosterValveClose)

    @Slot()
    def force_controller_state(self, data: typing.Any) -> None:
        pal_on = self.slew_flag_on.palette()
        pal_off = self.slew_flag_off.palette()
        if data.slewFlag:
            pal_on.setColor(pal_on.Button, Colors.WARNING)
            pal_off.setColor(pal_off.Button, self._default_color)
        else:
            pal_on.setColor(pal_on.Button, self._default_color)
            pal_off.setColor(pal_off.Button, Colors.OK)
        self.slew_flag_on.setPalette(pal_on)
        self.slew_flag_off.setPalette(pal_off)


class M1M3CSCControl(CSCControlWidget):
    """Widget to control M1M3 states.

    As M1M3 uses detailed state to record internal M1M3 state, a modification
    of CSCControlWidget is used to control M1M3 state transtions.

    Parameters
    ----------
    m1m3: `MetaSAL`
        M1M3 SAL object.
    """

    TEXT_RAISE = "&Raise M1M3"
    """Texts for additional commands."""
    TEXT_ABORT_RAISE = "&Abort M1M3 Raise"
    TEXT_LOWER = "&Lower M1M3"
    TEXT_ENTER_ENGINEERING = "&Enter Engineering"
    TEXT_EXIT_ENGINEERING = "&Exit Engineering"

    def __init__(self, m1m3: MetaSAL):
        super().__init__(
            m1m3,
            [
                self.TEXT_START,
                self.TEXT_ENABLE,
                self.TEXT_RAISE,
                self.TEXT_ENTER_ENGINEERING,
                self.TEXT_STANDBY,
            ],
            {
                self.TEXT_RAISE: "raiseM1M3",
                self.TEXT_ABORT_RAISE: "abortRaiseM1M3",
                self.TEXT_LOWER: "lowerM1M3",
                self.TEXT_ENTER_ENGINEERING: "enterEngineering",
                self.TEXT_EXIT_ENGINEERING: "exitEngineering",
            },
            "detailedState",
            "detailedState",
        )

    def get_state_buttons_map(self, state: int) -> list[str | None]:
        states_map: dict[int, list[str | None]] = {
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
            DetailedState.RAISING: [
                None,
                self.TEXT_ABORT_RAISE,
                None,
                None,
                None,
            ],
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
            DetailedState.PROFILEHARDPOINTCORRECTIONS: [
                None,
                None,
                None,
                None,
                None,
            ],
        }

        return states_map[state]


class ApplicationControlWidget(QWidget):
    """Widget with control buttons for M1M3 operations.

    Buttons are disabled/enabled and reasonable defaults sets on DetailedState
    changes.
    """

    TEXT_PANIC = "&Panic!"

    def __init__(self, m1m3: MetaSAL):
        super().__init__()

        self.m1m3 = m1m3
        self._hpWarnings = HPWarnings()

        command_layout = QVBoxLayout()

        self._panic_button = ColoredButton(self.TEXT_PANIC)
        self._panic_button.setColor(Qt.red)
        self._panic_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self._panic_button.clicked.connect(self._panic)

        command_layout.addWidget(self._panic_button)
        command_layout.addWidget(M1M3CSCControl(m1m3))

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

        command_layout.addLayout(dataLayout)
        self.slewWidget = SlewWidget(m1m3)
        self.slewWidget.setEnabled(False)
        command_layout.addWidget(self.slewWidget)

        command_layout.addStretch()

        self.weightSupportedPercent = QProgressBar()
        self.weightSupportedPercent.setOrientation(Qt.Vertical)
        self.weightSupportedPercent.setRange(0, 100)
        self.weightSupportedPercent.setTextVisible(True)
        self.weightSupportedPercent.setFormat("%p%")

        layout = QHBoxLayout()
        layout.addLayout(command_layout)
        layout.addWidget(self.weightSupportedPercent)

        self.setLayout(layout)

        # connect SAL signals
        self.m1m3.detailedState.connect(self.detailedState)
        self.m1m3.raisingLoweringInfo.connect(self.raisingLoweringInfo)
        self.m1m3.hardpointMonitorData.connect(self.hardpointMonitorData)
        self.m1m3.hardpointActuatorSettings.connect(self.hardpointActuatorSettings)

    @asyncSlot()
    async def _panic(self, checked: bool = False) -> None:
        await command(self, self.m1m3.remote.cmd_panic)

    @Slot()
    def detailedState(self, data: typing.Any) -> None:
        self._panic_button.setEnabled(not (data.detailedState == DetailedState.OFFLINE))
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
