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

from functools import partial

import astropy.units as u
from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.enums.MTM1M3 import DetailedStates, HardpointActuatorMotionState
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QDoubleSpinBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ..gui import (
    Arcsec,
    ArrayGrid,
    ArrayItem,
    ArraySignal,
    Colors,
    Force,
    FormatLabel,
    Mm,
    Moment,
    OnOffLabel,
)
from ..gui.sal import DetailedStateEnabledButton
from ..salcomm import MetaSAL, command


class OffsetUnit:
    """Helper class.

    Holds data for offset types presented.
    """

    def __init__(self, text: str, scale: float, decimals: int, unit: str):
        self.text = text
        self.scale = scale
        self.decimals = decimals
        self.unit = unit


class OffsetsTypeButton(QPushButton):
    """Button to change units of offset movement. Knows how to convert value
    from selected units into steps.

    Attributes
    ----------
    unitChanged : Signal(float, float, str, int)
        Signal emmited after unit changes. Parameters passed is old and new
        scale, unit name and number of decimal values to shown.
    """

    unitChanged = Signal(float, float, str, int)

    def __init__(self) -> None:
        super().__init__()

        # member array is unit name, scale factor, numbe of decimals, unit
        # abbrevation
        self._units = [
            OffsetUnit("&Motor steps", 1, 0, "motor"),
            OffsetUnit("&Encoder steps", 1, 0, "encoder"),
            OffsetUnit("&Displacement (um)", 1, 1, "um"),
            OffsetUnit("&Displacement (mm)", 1, 4, "mm"),
        ]
        self.setToolTip("Click to change move units")
        self.set_scales(0.0607, 0.2442)

        self._selectedIndex = 0
        self.setSelectedIndex(0)
        self.clicked.connect(self._clicked)

    def setSelectedIndex(self, index: int) -> None:
        """Sets new selected index.

        Parameters
        ----------
        index : int
            New index to set.
        """
        oldScale = self.getScale()

        self._selectedIndex = index
        self.setText(self._units[index].text)

        self.unitChanged.emit(
            oldScale, self.getScale(), self.getUnit(), self.getDecimals()
        )

    def getScale(self) -> float:
        """Returns scale used.

        Returns
        -------
        scale : float
            Scale factor for the current unit.
        """
        return self._units[self._selectedIndex].scale

    def getDecimals(self) -> int:
        """Returns number of decimals suggested for display. 0 for integer
        values."""
        return self._units[self._selectedIndex].decimals

    def getUnit(self) -> u:
        return self._units[self._selectedIndex].unit

    def set_scales(
        self, micrometersPerStep: float, micrometersPerEncoder: float
    ) -> None:
        self._units[1].scale = micrometersPerEncoder / micrometersPerStep
        self._units[2].scale = 1.0 / micrometersPerStep
        self._units[3].scale = u.mm.to(u.um) / micrometersPerStep

    @Slot()
    def _clicked(self, checked: bool) -> None:
        newIndex = self._selectedIndex + 1
        if newIndex >= len(self._units):
            newIndex = 0
        self.setSelectedIndex(newIndex)

    def get_steps(self, value: int) -> float:
        return int(value * self.getScale())


class HardpointsWidget(QWidget):
    """Displays hardpoint data - encoders and calculated position, hardpoint
    state, and M1M3 displacement."""

    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        self.m1m3 = m1m3

        layout = QVBoxLayout()

        self.grid = ArrayGrid(
            "<b>Hardpoint</b>",
            [f"<b>{x}</b>" for x in range(1, 7)],
            [
                ArraySignal(
                    self.m1m3.hardpointActuatorData,
                    [
                        ArrayItem("stepsQueued", "Steps queued"),
                        ArrayItem(
                            "stepsCommanded",
                            "Steps commanded",
                        ),
                        ArrayItem("encoder", "Encoder"),
                        ArrayItem(
                            "measuredForce",
                            "Measured force",
                            partial(Force, fmt=".03f"),
                        ),
                        ArrayItem(
                            "displacement",
                            "Displacement",
                            Mm,
                        ),
                    ],
                ),
                ArraySignal(
                    self.m1m3.hardpointMonitorData,
                    [
                        ArrayItem(
                            "breakawayLVDT",
                            "Breakaway LVDT",
                            partial(FormatLabel, ".02f"),
                        ),
                        ArrayItem(
                            "breakawayPressure",
                            "Breakaway Pressure",
                            partial(FormatLabel, ".02f"),
                        ),
                        ArrayItem(
                            "pressureSensor1",
                            "Pressure Sensor 1",
                            partial(FormatLabel, ".04f"),
                        ),
                        ArrayItem(
                            "pressureSensor2",
                            "Pressure Sensor 2",
                            partial(FormatLabel, ".04f"),
                        ),
                        ArrayItem(
                            "pressureSensor3",
                            "Pressure Sensor 3",
                            partial(FormatLabel, ".04f"),
                        ),
                    ],
                ),
                ArraySignal(
                    self.m1m3.hardpointActuatorWarning,
                    [
                        ArrayItem(
                            "majorFault",
                            "Major fault",
                            OnOffLabel,
                        ),
                        ArrayItem(
                            "minorFault",
                            "Minor fault",
                            OnOffLabel,
                        ),
                        ArrayItem(
                            "faultOverride",
                            "Fault override",
                            OnOffLabel,
                        ),
                        ArrayItem(
                            "mainCalibrationError",
                            "Main calibration error",
                            OnOffLabel,
                        ),
                        ArrayItem(
                            "backupCalibrationError",
                            "Backup calibration error",
                            OnOffLabel,
                        ),
                        ArrayItem(
                            "limitSwitch1Operated",
                            "Limit switch 1",
                            OnOffLabel,
                        ),
                        ArrayItem(
                            "limitSwitch2Operated",
                            "Limit switch 2",
                            OnOffLabel,
                        ),
                        ArrayItem(
                            "lowProximityWarning",
                            "Low proximity warning",
                            OnOffLabel,
                        ),
                        ArrayItem(
                            "highProximityWarning",
                            "High proximity warning",
                            OnOffLabel,
                        ),
                    ],
                ),
                ArraySignal(
                    self.m1m3.hardpointActuatorSettings,
                    [
                        ArrayItem(
                            "lowProximityEncoder",
                            "Low Proximity",
                        ),
                        ArrayItem(
                            "highProximityEncoder",
                            "High Proximity",
                        ),
                    ],
                ),
            ],
            Qt.Horizontal,
        )

        layout.addWidget(self.grid)

        self.dataLayout = QGridLayout()

        layout.addLayout(self.dataLayout)
        self.setLayout(layout)

        self.dataLayout.addWidget(QLabel("<b>Hardpoint</b>"), 0, 0)
        for hp in range(1, 7):
            self.dataLayout.addWidget(QLabel(f"<b>{hp}</b>"), 0, hp)

        row = 1

        self.lastEditedSteps = [0] * 6

        self.offsetType = OffsetsTypeButton()
        self.offsetType.unitChanged.connect(self._HPUnitChanged)

        self.dataLayout.addWidget(self.offsetType, row, 0)
        self._hpMoveRow = row
        self._HPUnitChanged(1, 1, " motor", 0)
        row += 1

        enabledStates = [
            DetailedStates.PARKEDENGINEERING,
            DetailedStates.RAISINGENGINEERING,
            DetailedStates.ACTIVEENGINEERING,
            DetailedStates.LOWERINGENGINEERING,
        ]

        self._lastOffsetFocused: int | None = None

        copyHPButton = QPushButton("Copy")
        copyHPButton.setToolTip("Use last edited (focused) value for all HP offsets")
        copyHPButton.clicked.connect(self._copyHP)
        self.dataLayout.addWidget(copyHPButton, row, 0)

        moveHPButton = DetailedStateEnabledButton("Move", m1m3, enabledStates)
        moveHPButton.clicked.connect(self._moveHP)
        self.dataLayout.addWidget(moveHPButton, row, 1, 1, 2)

        stopHPButton = DetailedStateEnabledButton("Stop", m1m3, enabledStates)
        stopHPButton.clicked.connect(self._stopHP)
        self.dataLayout.addWidget(stopHPButton, row, 3, 1, 2)

        reset = QPushButton("Reset")
        reset.clicked.connect(self._reset)
        self.dataLayout.addWidget(reset, row, 5, 1, 2)

        row += 1

        self.dataLayout.addWidget(QLabel("Motion state"), row, 0)
        self.hpStates = []
        for hp in range(6):
            self.hpStates.append(QLabel())
            self.dataLayout.addWidget(self.hpStates[hp], row, hp + 1)
        row += 1

        enableHPChaseButton = DetailedStateEnabledButton(
            "Enable Hardpoint Chase", m1m3, enabledStates
        )
        enableHPChaseButton.clicked.connect(self._enableHPChase)
        self.dataLayout.addWidget(enableHPChaseButton, row, 1, 1, 3)

        disableHPChaseButton = DetailedStateEnabledButton(
            "Disable Hardpoint Chase", m1m3, enabledStates
        )
        disableHPChaseButton.clicked.connect(self._disableHPChase)
        self.dataLayout.addWidget(disableHPChaseButton, row, 4, 1, 3)
        row += 1

        self.forces = {
            "forceMagnitude": ("Total force", Force()),
            "fx": ("Force X", Force()),
            "fy": ("Force Y", Force()),
            "fz": ("Force Z", Force()),
            "mx": ("Moment X", Moment()),
            "my": ("Moment Y", Moment()),
            "mz": ("Moment Z", Moment()),
        }

        self.dataLayout.addWidget(QLabel(), row, 0)
        row += 1

        def addDataRow(
            variables: dict[str, tuple[str, FormatLabel]], row: int, col: int = 0
        ) -> None:
            for k, v in variables.items():
                self.dataLayout.addWidget(QLabel(f"<b>{v[0]}</b>"), row, col)
                setattr(self, k, v[1])
                self.dataLayout.addWidget(v[1], row + 1, col)
                col += 1

        addDataRow(self.forces, row)
        row += 2
        self.dataLayout.addWidget(QLabel(), row, 0)
        row += 1
        self.positions = {
            "xPosition": ("Position X", Mm()),
            "yPosition": ("Position Y", Mm()),
            "zPosition": ("Position Z", Mm()),
            "xRotation": ("Rotation X", Arcsec()),
            "yRotation": ("Rotation Y", Arcsec()),
            "zRotation": ("Rotation Z", Arcsec()),
        }
        addDataRow(self.positions, row, 1)

        layout.addStretch()

        QApplication.instance().focusChanged.connect(self.focusChanged)

        self.m1m3.hardpointActuatorSettings.connect(self.hardpointActuatorSettings)

        self.m1m3.hardpointActuatorData.connect(self.hardpointActuatorData)
        self.m1m3.hardpointActuatorState.connect(self.hardpointActuatorState)

    @Slot()
    def focusChanged(self, old: QWidget, new: QWidget) -> None:
        for hp in range(len(self.hpOffsets)):
            if self.hpOffsets[hp] == old:
                self.lastEditedSteps[hp] = self.offsetType.getScale() * old.value()
                self._lastOffsetFocused = hp
                return

    @Slot()
    def _HPUnitChanged(
        self, oldScale: float, newScale: float, units: str, decimals: int
    ) -> None:
        self.hpOffsets = []
        for hp in range(6):
            if decimals == 0:
                sb = QSpinBox()
                maxSteps = 70000 * 4.03 / self.offsetType.get_steps(1)
                sb.setRange(-maxSteps, maxSteps)
                sb.setSingleStep(100)
            else:
                sb = QDoubleSpinBox()
                maxRange = 15 * (10 ** (4 - decimals))
                sb.setRange(-maxRange, maxRange)
                sb.setDecimals(decimals)
                sb.setSingleStep(1)

            sb.setSuffix(" " + units)
            self.dataLayout.addWidget(sb, self._hpMoveRow, 1 + hp)
            if self.lastEditedSteps is not None:
                sb.setValue(self.lastEditedSteps[hp] / self.offsetType.getScale())

            self.hpOffsets.append(sb)

    @Slot()
    def _copyHP(self) -> None:
        if self._lastOffsetFocused is not None:
            v = self.hpOffsets[self._lastOffsetFocused].value()
            for offset in self.hpOffsets:
                offset.setValue(v)
            self.lastEditedSteps = [self.offsetType.getScale() * v] * 6

    @asyncSlot()
    async def _moveHP(self) -> None:
        steps = [self.offsetType.get_steps(x.value()) for x in self.hpOffsets]
        await command(self, self.m1m3.remote.cmd_moveHardpointActuators, steps=steps)

    @asyncSlot()
    async def _stopHP(self) -> None:
        await command(self, self.m1m3.remote.cmd_stopHardpointMotion)

    @Slot()
    def _reset(self) -> None:
        for hp in range(6):
            self.hpOffsets[hp].setValue(0)

    def _fillRow(self, hpData: list[float], rowLabels: list[FormatLabel]) -> None:
        for hp in range(6):
            rowLabels[hp].setValue(hpData[hp])

    @asyncSlot()
    async def _enableHPChase(self) -> None:
        await command(self, self.m1m3.remote.cmd_enableHardpointChase)

    @asyncSlot()
    async def _disableHPChase(self) -> None:
        await command(self, self.m1m3.remote.cmd_disableHardpointChase)

    @Slot()
    def hardpointActuatorSettings(self, data: BaseMsgType) -> None:
        self.offsetType.set_scales(data.micrometersPerStep, data.micrometersPerEncoder)

    @Slot()
    def hardpointActuatorData(self, data: BaseMsgType) -> None:
        hs = self.m1m3.remote.evt_hardpointActuatorSettings.get()
        if hs is not None:
            for idx, f in enumerate(data.measuredForce):
                color = Colors.OK
                if (
                    f < hs.hardpointMeasuredForceWarningLow
                    or f > hs.hardpointMeasuredForceWarningHigh
                ):
                    color = Colors.WARNING
                if (
                    f < hs.hardpointMeasuredForceFaultLow
                    or f > hs.hardpointMeasuredForceFaultHigh
                ):
                    color = Colors.ERROR

                label = self.grid.get_label("measuredForce", idx)
                assert label is not None
                label.setTextColor(color)

            for idx, e in enumerate(data.encoder):
                color = self.palette().windowText().color()
                if e < hs.lowProximityEncoder[idx] or e > hs.highProximityEncoder[idx]:
                    color = Colors.WARNING

                label = self.grid.get_label("encoder", idx)
                assert label is not None
                label.setTextColor(color)

        for k, v in self.forces.items():
            getattr(self, k).setValue(getattr(data, k))

        for k, v in self.positions.items():
            getattr(self, k).setValue(getattr(data, k))

    @Slot()
    def hardpointActuatorState(self, data: BaseMsgType) -> None:
        states = {
            HardpointActuatorMotionState.STANDBY: "Standby",
            HardpointActuatorMotionState.CHASING: "Chasing",
            HardpointActuatorMotionState.STEPPING: "Stepping",
            HardpointActuatorMotionState.QUICKPOSITIONING: "Quick positioning",
            HardpointActuatorMotionState.FINEPOSITIONING: "Fine positioning",
            HardpointActuatorMotionState.WAITINGTENSION: "Wait for support",
        }

        def getHpState(state: HardpointActuatorMotionState) -> str:
            try:
                return states[state]
            except KeyError:
                return f"Invalid {state}"

        for hp in range(6):
            self.hpStates[hp].setText(getHpState(data.motionState[hp]))
