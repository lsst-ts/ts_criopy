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
from lsst.ts.xml.enums.MTM1M3 import DetailedStates
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
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
        if state in (DetailedStates.RAISING, DetailedStates.RAISINGENGINEERING):
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

    def hardpointActuatorSettings(self, data: BaseMsgType) -> None:
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
        self._default_color = pal.button().color()

        self.booster_open = EngineeringButton("Booster Open", m1m3)
        self.booster_close = EngineeringButton("Booster Close", m1m3)

        boosterLayout = QHBoxLayout()
        boosterLayout.addWidget(self.booster_open)
        boosterLayout.addWidget(self.booster_close)

        slewLayout.addLayout(boosterLayout)

        slewControlLayout = QHBoxLayout()
        slewControlLayout.addWidget(self.slew_flag_on)
        slewControlLayout.addWidget(self.slew_flag_off)

        slewLayout.addLayout(slewControlLayout)

        self.setLayout(slewLayout)

        self.slew_flag_on.clicked.connect(self.issueCommandSlewFlagOn)
        self.slew_flag_off.clicked.connect(self.issueCommandSlewFlagOff)

        self.booster_open.clicked.connect(self.issueCommandBoosterOpen)
        self.booster_close.clicked.connect(self.issueCommandBoosterClose)

        self.m1m3.boosterValveStatus.connect(self.booster_valve_status)

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
    def booster_valve_status(self, data: BaseMsgType) -> None:
        pal_open = self.booster_open.palette()
        pal_close = self.booster_close.palette()
        if data.userTriggered:
            pal_open.setColor(QPalette.Button, Colors.WARNING)
            pal_close.setColor(QPalette.Button, self._default_color)
            self.booster_open.setEnabled(False)
            self.booster_close.setEnabled(True)
        else:
            pal_open.setColor(QPalette.Button, self._default_color)
            pal_close.setColor(QPalette.Button, Colors.OK)
            self.booster_open.setEnabled(True)
            self.booster_close.setEnabled(False)

        self.booster_open.setPalette(pal_open)
        self.booster_close.setPalette(pal_close)

    @Slot()
    def force_controller_state(self, data: BaseMsgType) -> None:
        pal_on = self.slew_flag_on.palette()
        pal_off = self.slew_flag_off.palette()
        if data.slewFlag:
            pal_on.setColor(QPalette.Button, Colors.WARNING)
            pal_off.setColor(QPalette.Button, self._default_color)
            self.slew_flag_on.setEnabled(False)
            self.slew_flag_off.setEnabled(True)
        else:
            pal_on.setColor(QPalette.Button, self._default_color)
            pal_off.setColor(QPalette.Button, Colors.OK)
            self.slew_flag_on.setEnabled(True)
            self.slew_flag_off.setEnabled(False)

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
    TEXT_EXIT_ENGINEERING = "E&xit Engineering"
    TEXT_PANIC = "&Panic!"
    TEXT_PAUSE_RAISING = "Pause raising"
    TEXT_RESUME_RAISING = "Resume raising"
    TEXT_PAUSE_LOWERING = "Pause lowering"
    TEXT_RESUME_LOWERING = "Resume lowering"

    def __init__(self, m1m3: MetaSAL):
        super().__init__(
            m1m3,
            [
                self.TEXT_START,
                self.TEXT_ENABLE,
                self.TEXT_RAISE,
                self.TEXT_PAUSE_RAISING,
                self.TEXT_ENTER_ENGINEERING,
                self.TEXT_STANDBY,
            ],
            {
                self.TEXT_RAISE: "raiseM1M3",
                self.TEXT_PAUSE_RAISING: "pauseM1M3RaisingLowering",
                self.TEXT_RESUME_RAISING: "resumeM1M3RaisingLowering",
                self.TEXT_ABORT_RAISE: "abortRaiseM1M3",
                self.TEXT_LOWER: "lowerM1M3",
                self.TEXT_PAUSE_LOWERING: "pauseM1M3RaisingLowering",
                self.TEXT_RESUME_LOWERING: "resumeM1M3RaisingLowering",
                self.TEXT_ENTER_ENGINEERING: "enterEngineering",
                self.TEXT_EXIT_ENGINEERING: "exitEngineering",
            },
            "detailedState",
            "detailedState",
        )
        self.m1m3 = m1m3

        self._panic_button = ColoredButton(self.TEXT_PANIC)
        self._panic_button.setColor(Qt.red)
        self._panic_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self._panic_button.setMinimumHeight(50)
        self._panic_button.clicked.connect(self._panic)

        self.insert_widget(self._panic_button, 0)

        self.m1m3.detailedState.connect(self.detailed_state)

    def get_state_buttons_map(self, state: int) -> list[str | None]:
        states_map: dict[int, list[str | None]] = {
            DetailedStates.STANDBY: [
                self.TEXT_START,
                None,
                None,
                None,
                None,
                self.TEXT_EXIT_CONTROL,
            ],
            DetailedStates.DISABLED: [
                None,
                self.TEXT_ENABLE,
                None,
                None,
                None,
                self.TEXT_STANDBY,
            ],
            DetailedStates.FAULT: [self.TEXT_STANDBY, None, None, None, None, None],
            DetailedStates.OFFLINE: [None, None, None, None, None, None],
            DetailedStates.PARKED: [
                None,
                self.TEXT_DISABLE,
                self.TEXT_RAISE,
                None,
                self.TEXT_ENTER_ENGINEERING,
                None,
            ],
            DetailedStates.PARKEDENGINEERING: [
                None,
                self.TEXT_DISABLE,
                self.TEXT_RAISE,
                None,
                self.TEXT_EXIT_ENGINEERING,
                None,
            ],
            DetailedStates.RAISING: [
                None,
                self.TEXT_ABORT_RAISE,
                None,
                self.TEXT_PAUSE_RAISING,
                None,
                None,
            ],
            DetailedStates.RAISINGENGINEERING: [
                None,
                self.TEXT_ABORT_RAISE,
                None,
                self.TEXT_PAUSE_RAISING,
                None,
                None,
            ],
            DetailedStates.ACTIVE: [
                None,
                None,
                self.TEXT_LOWER,
                None,
                self.TEXT_ENTER_ENGINEERING,
                None,
            ],
            DetailedStates.ACTIVEENGINEERING: [
                None,
                None,
                self.TEXT_LOWER,
                None,
                self.TEXT_EXIT_ENGINEERING,
                None,
            ],
            DetailedStates.LOWERING: [
                None,
                None,
                None,
                self.TEXT_PAUSE_LOWERING,
                None,
                None,
            ],
            DetailedStates.LOWERINGENGINEERING: [
                None,
                None,
                None,
                self.TEXT_PAUSE_LOWERING,
                None,
                None,
            ],
            DetailedStates.LOWERINGFAULT: [None, None, None, None, None, None],
            DetailedStates.PROFILEHARDPOINTCORRECTIONS: [
                None,
                None,
                None,
                None,
                None,
                None,
            ],
            DetailedStates.PAUSEDRAISING: [
                None,
                None,
                self.TEXT_RESUME_RAISING,
                None,
                None,
                None,
            ],
            DetailedStates.PAUSEDRAISINGENGINEERING: [
                None,
                None,
                self.TEXT_RESUME_RAISING,
                None,
                None,
                None,
            ],
            DetailedStates.PAUSEDLOWERING: [
                None,
                None,
                self.TEXT_RESUME_LOWERING,
                None,
                None,
                None,
            ],
            DetailedStates.PAUSEDLOWERINGENGINEERING: [
                None,
                None,
                self.TEXT_RESUME_LOWERING,
                None,
                None,
                None,
            ],
        }

        return states_map[state]

    @asyncSlot()
    async def _panic(self, checked: bool = False) -> None:
        await command(self, self.m1m3.remote.cmd_panic)

    @Slot()
    def detailed_state(self, data: BaseMsgType) -> None:
        self._panic_button.setEnabled(
            not (data.detailedState == DetailedStates.OFFLINE)
        )


class ApplicationControlWidget(QWidget):
    """Widget with control buttons for M1M3 operations.

    Buttons are disabled/enabled and reasonable defaults sets on DetailedState
    changes.
    """

    def __init__(self, m1m3: MetaSAL):
        super().__init__()

        self.m1m3 = m1m3
        self._hpWarnings = HPWarnings()

        command_layout = QVBoxLayout()

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

    @Slot()
    def detailedState(self, data: BaseMsgType) -> None:
        self.slewWidget.setEnabled(
            data.detailedState
            not in (
                DetailedStates.OFFLINE,
                DetailedStates.STANDBY,
                DetailedStates.DISABLED,
                DetailedStates.FAULT,
            )
        )

        self._set_hardpoint_warnings(data.detailedState)

    @Slot()
    def hardpointActuatorSettings(self, data: BaseMsgType) -> None:
        self._hpWarnings.hardpointActuatorSettings(data)
        state = self.m1m3.remote.evt_detailedState.get()
        if state is not None:
            self._set_hardpoint_warnings(state)

    @Slot()
    def raisingLoweringInfo(self, data: BaseMsgType) -> None:
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
        pal.setColor(QPalette.Window, col)
        self.supportedNumber.display(f"{data.weightSupportedPercent:.02f}")
        self.supportedNumber.setPalette(pal)

    @Slot()
    def hardpointMonitorData(self, data: BaseMsgType) -> None:
        min_d = min(data.breakawayPressure)
        max_d = max(data.breakawayPressure)

        min_pal = self.minPressure.palette()
        min_pal.setColor(QPalette.Window, self._hpWarnings.get_color(min_d))
        self.minPressure.display(f"{min_d:.02f}")
        self.minPressure.setPalette(min_pal)

        max_pal = self.minPressure.palette()
        max_pal.setColor(QPalette.Window, self._hpWarnings.get_color(max_d))
        self.maxPressure.display(f"{max_d:.02f}")
        self.maxPressure.setPalette(max_pal)

    def _set_hardpoint_warnings(self, state: int) -> None:
        self._hpWarnings.setState(state)
        self.minPressure.setToolTip(self._hpWarnings.min_text())
        self.maxPressure.setToolTip(self._hpWarnings.max_text())
