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

from .SALComm import SALCommand
from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QSpinBox,
    QPushButton,
)
from PySide2.QtCore import Slot
from asyncqt import asyncSlot
from .CustomLabels import Force, Moment, Mm, UnitLabel, WarningLabel
import copy

from lsst.ts.idl.enums.MTM1M3 import DetailedState, HardpointActuatorMotionStates


class HardpointsWidget(QWidget):
    """Displays hardpoint data - encoders and calculated position, hardpoint
    state, and M1M3 displacement."""

    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3

        self.layout = QVBoxLayout()

        dataLayout = QGridLayout()

        self.layout.addLayout(dataLayout)
        self.setLayout(self.layout)

        dataLayout.addWidget(QLabel("<b>Hardpoint</b>"), 0, 0)
        for hp in range(1, 7):
            dataLayout.addWidget(QLabel(f"<b>{hp}</b>"), 0, hp)

        self.variables = {
            "stepsQueued": ("Steps queued", UnitLabel()),
            "stepsCommanded": ("Steps commanded", UnitLabel()),
            "encoder": ("Encoder", UnitLabel()),
            "measuredForce": ("Measured force", Force(".03f")),
            "displacement": ("Displacement", Mm()),
        }

        row = 1

        def addRow(textValue, row):
            ret = []
            dataLayout.addWidget(QLabel(textValue[0]), row, 0)
            for hp in range(6):
                label = copy.copy(textValue[1])
                dataLayout.addWidget(label, row, 1 + hp)
                ret.append(label)
            return ret

        for k, v in self.variables.items():
            setattr(self, k, addRow(v, row))
            row += 1

        dataLayout.addWidget(QLabel("Encoder offsets"), row, 0)
        self.hpOffsets = []
        for hp in range(6):
            sb = QSpinBox()
            sb.setRange(-(1 << 16), 1 << 16)
            sb.setSingleStep(100)
            dataLayout.addWidget(sb, row, 1 + hp)
            self.hpOffsets.append(sb)
        row += 1

        self.moveHPButton = QPushButton("Move")
        self.moveHPButton.clicked.connect(self._moveHP)
        dataLayout.addWidget(self.moveHPButton, row, 1, 1, 3)

        reset = QPushButton("Reset")
        reset.clicked.connect(self._reset)
        dataLayout.addWidget(reset, row, 4, 1, 3)

        row += 1

        self.monitorData = {
            "breakawayLVDT": ("Breakaway LVDT", UnitLabel(".02f")),
            "displacementLVDT": ("Displacement LVDT", UnitLabel(".02f")),
            "breakawayPressure": ("Breakaway Pressure", UnitLabel(".02f")),
            "pressureSensor1": ("Pressure Sensor 1", UnitLabel(".04f")),
            "pressureSensor2": ("Pressure Sensor 2", UnitLabel(".04f")),
            "pressureSensor3": ("Pressure Sensor 3", UnitLabel(".04f")),
        }

        for k, v in self.monitorData.items():
            setattr(self, k, addRow(v, row))
            row += 1

        self.warnings = {
            "majorFault": ("Major fault", WarningLabel()),
            "minorFault": ("Minor fault", WarningLabel()),
            "faultOverride": ("Fault override", WarningLabel()),
            "mainCalibrationError": ("Main calibration error", WarningLabel()),
            "backupCalibrationError": ("Backup calibration error", WarningLabel()),
            "limitSwitch1Operated": ("Limit switch 1", WarningLabel()),
            "limitSwitch2Operated": ("Limit switch 2", WarningLabel()),
        }

        for k, v in self.warnings.items():
            setattr(self, k, addRow(v, row))
            row += 1

        dataLayout.addWidget(QLabel("Motion state"), row, 0)
        self.hpStates = []
        for hp in range(6):
            self.hpStates.append(QLabel())
            dataLayout.addWidget(self.hpStates[hp], row, hp + 1)
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

        dataLayout.addWidget(QLabel(), row, 0)
        row += 1

        def addDataRow(variables, row, col=0):
            for k, v in variables.items():
                dataLayout.addWidget(QLabel(f"<b>{v[0]}</b>"), row, col)
                setattr(self, k, v[1])
                dataLayout.addWidget(v[1], row + 1, col)
                col += 1

        addDataRow(self.forces, row)
        row += 2
        dataLayout.addWidget(QLabel(), row, 0)
        row += 1
        self.positions = {
            "xPosition": ("Position X", Mm()),
            "yPosition": ("Position Y", Mm()),
            "zPosition": ("Position Z", Mm()),
            "xRotation": ("Rotation X", Mm()),
            "yRotation": ("Rotation Y", Mm()),
            "zRotation": ("Rotation Z", Mm()),
        }
        addDataRow(self.positions, row, 1)

        self.layout.addStretch()

        self.m1m3.detailedState.connect(self.detailedState)
        self.m1m3.hardpointActuatorData.connect(self.hardpointActuatorData)
        self.m1m3.hardpointActuatorState.connect(self.hardpointActuatorState)
        self.m1m3.hardpointMonitorData.connect(self.hardpointMonitorData)
        self.m1m3.hardpointActuatorWarning.connect(self.hardpointActuatorWarning)

    @SALCommand
    def _moveIt(self, **kvargs):
        return self.m1m3.remote.cmd_moveHardpointActuators

    @asyncSlot()
    async def _moveHP(self):
        steps = list(map(lambda x: x.value(), self.hpOffsets))
        await self._moveIt(steps=steps)

    @Slot()
    def _reset(self):
        for hp in range(6):
            self.hpOffsets[hp].setValue(0)

    def _fillRow(self, hpData, rowLabels):
        for hp in range(6):
            rowLabels[hp].setValue(hpData[hp])

    @Slot(map)
    def detailedState(self, data):
        self.moveHPButton.setEnabled(
            data.detailedState
            in (
                DetailedState.PARKEDENGINEERING,
                DetailedState.RAISINGENGINEERING,
                DetailedState.ACTIVEENGINEERING,
                DetailedState.LOWERINGENGINEERING,
            )
        )

    @Slot(map)
    def hardpointActuatorData(self, data):
        for k, v in self.variables.items():
            self._fillRow(getattr(data, k), getattr(self, k))

        for k, v in self.forces.items():
            getattr(self, k).setValue(getattr(data, k))

        for k, v in self.positions.items():
            getattr(self, k).setValue(getattr(data, k))

    @Slot(map)
    def hardpointActuatorState(self, data):
        states = {
            HardpointActuatorMotionStates.STANDBY: "Standby",
            HardpointActuatorMotionStates.CHASING: "Chasing",
            HardpointActuatorMotionStates.STEPPING: "Stepping",
            HardpointActuatorMotionStates.QUICKPOSITIONING: "Quick positioning",
            HardpointActuatorMotionStates.FINEPOSITIONING: "Fine positioning",
        }

        def getHpState(state):
            try:
                return states[state]
            except KeyError:
                return f"Invalid {state}"

        for hp in range(6):
            self.hpStates[hp].setText(getHpState(data.motionState[hp]))

    @Slot(map)
    def hardpointMonitorData(self, data):
        for k, v in self.monitorData.items():
            self._fillRow(getattr(data, k), getattr(self, k))

    @Slot(map)
    def hardpointActuatorWarning(self, data):
        for k, v in self.warnings.items():
            self._fillRow(getattr(data, k), getattr(self, k))
