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

from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.enums.MTM1M3 import DetailedStates
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from qasync import asyncSlot

from ..gui import Clipped, Force, Moment, TimeChart, TimeChartView
from ..gui.sal import DetailedStateEnabledButton
from ..salcomm import MetaSAL, command


class ForceBalanceSystemPageWidget(QWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        self.m1m3 = m1m3

        self._balanceData = None
        self._hardpointData = None

        layout = QVBoxLayout()
        data_layout = QGridLayout()
        warning_layout = QHBoxLayout()
        command_layout = QVBoxLayout()
        plotLayout = QHBoxLayout()
        layout.addLayout(command_layout)
        layout.addSpacing(20)
        layout.addLayout(data_layout)
        layout.addSpacing(20)
        layout.addLayout(warning_layout)
        layout.addSpacing(20)
        layout.addLayout(plotLayout)
        self.setLayout(layout)

        self.enable_hardpoint_corrections_button = DetailedStateEnabledButton(
            "Enable Hardpoint Corrections",
            m1m3,
            [DetailedStates.ACTIVEENGINEERING],
        )
        self.enable_hardpoint_corrections_button.clicked.connect(
            self.issueCommandEnableHardpointCorrections
        )
        self.enable_hardpoint_corrections_button.setFixedWidth(256)
        self.disable_hardpoint_corrections_button = DetailedStateEnabledButton(
            "Disable Hardpoint Corrections",
            m1m3,
            [DetailedStates.ACTIVEENGINEERING],
        )
        self.disable_hardpoint_corrections_button.clicked.connect(
            self.issueCommandDisableHardpointCorrections
        )
        self.disable_hardpoint_corrections_button.setFixedWidth(256)

        self.balance_forces_clipped = Clipped("Balance")

        self.balance_chart = TimeChart(
            {
                "Balance Force (N)": [
                    "Force X",
                    "Force Y",
                    "Force Z",
                    "Magnitude",
                ],
                "Moment (N/m)": ["Moment X", "Moment Y", "Moment Z"],
            }
        )
        self.balanceChartView = TimeChartView(self.balance_chart)

        command_layout.addWidget(self.enable_hardpoint_corrections_button)
        command_layout.addWidget(self.disable_hardpoint_corrections_button)

        row = 0

        values = [
            "Fx",
            "Fy",
            "Fz",
            "Mx",
            "My",
            "Mz",
            "Mag",
        ]

        for d in range(len(values)):
            data_layout.addWidget(QLabel(f"<b>{values[d]}</b>"), row, d + 1)

        row += 1

        def createXYZ() -> dict[str, QLabel]:
            return {
                "fx": Force(),
                "fy": Force(),
                "fz": Force(),
                "mx": Moment(),
                "my": Moment(),
                "mz": Moment(),
                "forceMagnitude": Force(),
            }

        def add_data_row(variables: dict[str, QLabel], row: int, col: int = 1) -> None:
            for k, v in variables.items():
                data_layout.addWidget(v, row, col)
                col += 1

        self.totals = createXYZ()

        data_layout.addWidget(QLabel("<b>Total</b>"), row, 0)
        add_data_row(self.totals, row)

        row += 1
        self.corrected = createXYZ()
        data_layout.addWidget(QLabel("<b>Corrected</b>"), row, 0)
        add_data_row(self.corrected, row)

        row += 1
        self.remaing = createXYZ()
        data_layout.addWidget(QLabel("<b>Remaining</b>"), row, 0)
        add_data_row(self.remaing, row)

        row += 1
        data_layout.addWidget(QLabel(" "), row, 0)
        row += 1

        hardpoints = [f"HP{x}" for x in range(1, 7)] + ["Mag"]

        for d in range(len(hardpoints)):
            data_layout.addWidget(QLabel(f"<b>{hardpoints[d]}</b>"), row, d + 1)

        row += 1

        data_layout.addWidget(QLabel("<b>Measured Force</b>"), row, 0)

        self.hardpoints = [Force() for x in range(len(hardpoints))]
        for c in range(len(self.hardpoints)):
            data_layout.addWidget(self.hardpoints[c], row, c + 1)

        warning_layout.addWidget(self.balance_forces_clipped)
        warning_layout.addStretch()

        plotLayout.addWidget(self.balanceChartView)

        self.m1m3.appliedBalanceForces.connect(self.appliedBalanceForces)
        self.m1m3.preclippedBalanceForces.connect(self.preclippedBalanceForces)
        self.m1m3.forceControllerState.connect(self.force_controller_state)
        self.m1m3.hardpointActuatorData.connect(self.hardpointActuatorData)

    def _fillRow(self, variables: dict[str, QLabel], data: BaseMsgType) -> None:
        for k, v in variables.items():
            v.setValue(getattr(data, k))

    @Slot()
    def appliedBalanceForces(self, data: BaseMsgType) -> None:
        self._fillRow(self.corrected, data)

        self.balance_chart.append(
            data.timestamp,
            [data.fx, data.fy, data.fz, data.forceMagnitude],
            axis_index=0,
        )
        self.balance_chart.append(
            data.timestamp, [data.mx, data.my, data.mz], axis_index=1
        )

        self._balanceData = data
        self._setTotalForces()

        self.preclippedBalanceForces(data)

    @Slot()
    def preclippedBalanceForces(self, data: BaseMsgType) -> None:
        self.balance_forces_clipped.setClipped(True)

    @Slot()
    def force_controller_state(self, data: BaseMsgType) -> None:
        self.enable_hardpoint_corrections_button.setDisabled(data.balanceForcesApplied)
        self.disable_hardpoint_corrections_button.setEnabled(data.balanceForcesApplied)

    @Slot()
    def hardpointActuatorData(self, data: BaseMsgType) -> None:
        for hp in range(6):
            self.hardpoints[hp].setValue(data.measuredForce[hp])
        self.hardpoints[6].setValue(sum(data.measuredForce))

        self._fillRow(self.remaing, data)

        self._hardpointData = data
        self._setTotalForces()

    @asyncSlot()
    async def issueCommandEnableHardpointCorrections(self) -> None:
        await command(self, self.m1m3.remote.cmd_enableHardpointCorrections)

    @asyncSlot()
    async def issueCommandDisableHardpointCorrections(self) -> None:
        await command(self, self.m1m3.remote.cmd_disableHardpointCorrections)

    def _fillRowSum(
        self, variables: dict[str, QLabel], d1: typing.Any, d2: typing.Any
    ) -> None:
        for k, v in variables.items():
            v.setValue(getattr(d1, k) + getattr(d2, k))

    def _setTotalForces(self) -> None:
        if self._balanceData is None or self._hardpointData is None:
            return

        self._fillRowSum(self.totals, self._balanceData, self._hardpointData)
