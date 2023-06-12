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
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ..GUI import Clipped, Force, Moment, TimeChart, TimeChartView
from ..GUI.SAL import DetailedStateEnabledButton
from ..SALComm import MetaSAL, command


class ForceBalanceSystemPageWidget(QWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        self.m1m3 = m1m3

        self._balanceData = None
        self._hardpointData = None

        layout = QVBoxLayout()
        dataLayout = QGridLayout()
        warningLayout = QHBoxLayout()
        commandLayout = QVBoxLayout()
        plotLayout = QHBoxLayout()
        layout.addLayout(commandLayout)
        layout.addSpacing(20)
        layout.addLayout(dataLayout)
        layout.addSpacing(20)
        layout.addLayout(warningLayout)
        layout.addSpacing(20)
        layout.addLayout(plotLayout)
        self.setLayout(layout)

        self.enableHardpointCorrectionsButton = DetailedStateEnabledButton(
            "Enable Hardpoint Corrections",
            m1m3,
            [DetailedState.ACTIVE, DetailedState.ACTIVEENGINEERING],
        )
        self.enableHardpointCorrectionsButton.clicked.connect(
            self.issueCommandEnableHardpointCorrections
        )
        self.enableHardpointCorrectionsButton.setFixedWidth(256)
        self.disableHardpointCorrectionsButton = DetailedStateEnabledButton(
            "Disable Hardpoint Corrections",
            m1m3,
            [DetailedState.ACTIVE, DetailedState.ACTIVEENGINEERING],
        )
        self.disableHardpointCorrectionsButton.clicked.connect(
            self.issueCommandDisableHardpointCorrections
        )
        self.disableHardpointCorrectionsButton.setFixedWidth(256)

        self.balanceForcesClipped = Clipped("Balance")

        self.balanceChart = TimeChart(
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
        self.balanceChartView = TimeChartView(self.balanceChart)

        commandLayout.addWidget(self.enableHardpointCorrectionsButton)
        commandLayout.addWidget(self.disableHardpointCorrectionsButton)

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
            dataLayout.addWidget(QLabel(f"<b>{values[d]}</b>"), row, d + 1)

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

        def addDataRow(variables: dict[str, QLabel], row: int, col: int = 1) -> None:
            for k, v in variables.items():
                dataLayout.addWidget(v, row, col)
                col += 1

        self.totals = createXYZ()

        dataLayout.addWidget(QLabel("<b>Total</b>"), row, 0)
        addDataRow(self.totals, row)

        row += 1
        self.corrected = createXYZ()
        dataLayout.addWidget(QLabel("<b>Corrected</b>"), row, 0)
        addDataRow(self.corrected, row)

        row += 1
        self.remaing = createXYZ()
        dataLayout.addWidget(QLabel("<b>Remaining</b>"), row, 0)
        addDataRow(self.remaing, row)

        row += 1
        dataLayout.addWidget(QLabel(" "), row, 0)
        row += 1

        hardpoints = [f"HP{x}" for x in range(1, 7)] + ["Mag"]

        for d in range(len(hardpoints)):
            dataLayout.addWidget(QLabel(f"<b>{hardpoints[d]}</b>"), row, d + 1)

        row += 1

        dataLayout.addWidget(QLabel("<b>Measured Force</b>"), row, 0)

        self.hardpoints = [Force() for x in range(len(hardpoints))]
        for c in range(len(self.hardpoints)):
            dataLayout.addWidget(self.hardpoints[c], row, c + 1)

        warningLayout.addWidget(self.balanceForcesClipped)
        warningLayout.addStretch()

        plotLayout.addWidget(self.balanceChartView)

        self.m1m3.appliedBalanceForces.connect(self.appliedBalanceForces)
        self.m1m3.preclippedBalanceForces.connect(self.preclippedBalanceForces)
        self.m1m3.forceActuatorState.connect(self.forceActuatorState)
        self.m1m3.hardpointActuatorData.connect(self.hardpointActuatorData)

    def _fillRow(self, variables: dict[str, QLabel], data: typing.Any) -> None:
        for k, v in variables.items():
            v.setValue(getattr(data, k))

    @Slot()
    def appliedBalanceForces(self, data: typing.Any) -> None:
        self._fillRow(self.corrected, data)

        self.balanceChart.append(
            data.timestamp,
            [data.fx, data.fy, data.fz, data.forceMagnitude],
            axis_index=0,
        )
        self.balanceChart.append(
            data.timestamp, [data.mx, data.my, data.mz], axis_index=1
        )

        self._balanceData = data
        self._setTotalForces()

        self.preclippedBalanceForces(data)

    @Slot()
    def preclippedBalanceForces(self, data: typing.Any) -> None:
        try:
            self.balanceForcesClipped.setClipped(
                (
                    self.m1m3.remote.evt_balanceForcesApplied.get().timestamp
                    == self.m1m3.remote.evt_preclippedBalanceForces.get().timestamp
                )
            )
        except AttributeError:
            self.balanceForcesClipped.setClipped(False)

    @Slot()
    def forceActuatorState(self, data: typing.Any) -> None:
        self.enableHardpointCorrectionsButton.setDisabled(data.balanceForcesApplied)
        self.disableHardpointCorrectionsButton.setEnabled(data.balanceForcesApplied)

    @Slot()
    def hardpointActuatorData(self, data: typing.Any) -> None:
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
