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

from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.enums.MTM1M3 import DetailedStates, EnableDisableForceComponent
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qasync import asyncSlot

from ..gui import ArrayFields, ColoredButton, UnitLabel
from ..gui.sal import Axis, ChartWidget
from ..salcomm import MetaSAL, command
from .force_grid import Forces, ForcesGrid, PreclippedForces, PreclippedLabel


class ForceButton(ColoredButton):
    def __init__(self, enable: bool, name: str, m1m3: MetaSAL):
        super().__init__("Enable" if enable else "Disable")
        self.setObjectName(name)
        self.m1m3 = m1m3

        self.__enable = enable
        self.__engineering_state = False

        self.clicked.connect(self.enable_force)
        self.m1m3.forceControllerState.connect(self.force_controller_state)
        self.m1m3.detailedState.connect(self.detailed_state)

    @asyncSlot()
    async def enable_force(self) -> None:
        await command(
            self,
            self.m1m3.remote.cmd_enableDisableForceComponent,
            forceComponent=int(
                getattr(
                    EnableDisableForceComponent, self.objectName().upper() + "FORCE"
                )
            ),
            enable=self.__enable,
        )

    def set_button_enable(self, applied: bool) -> None:
        self.setDisabled(applied if self.__enable else not (applied))

    @Slot()
    def force_controller_state(self, data: BaseMsgType) -> None:
        applied = getattr(data, self.objectName() + "ForcesApplied")
        if applied:
            self.setColor(Qt.green if self.__enable else None)
        else:
            self.setColor(None if self.__enable else Qt.red)

        if self.__engineering_state:
            self.set_button_enable(applied)

    @Slot()
    def detailed_state(self, data: BaseMsgType) -> None:
        self.__engineering_state = (
            data.detailedState == DetailedStates.ACTIVEENGINEERING
        )
        if self.__engineering_state:
            force_controller_state = self.m1m3.remote.evt_forceControllerState.get()
            if force_controller_state is not None:
                self.set_button_enable(
                    getattr(force_controller_state, self.objectName() + "ForcesApplied")
                )
            else:
                self.setEnabled(True)
        else:
            self.setDisabled(True)

    @classmethod
    def create(cls, name: str, m1m3: MetaSAL) -> list["ForceButton"]:
        return [ForceButton(True, name, m1m3), ForceButton(False, name, m1m3)]


class ActuatorOverviewPageWidget(QWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        self.m1m3 = m1m3

        layout = QVBoxLayout()
        layout.addWidget(
            ForcesGrid(
                [
                    PreclippedForces("<i>Pre-clipped</i>", m1m3.preclippedForces),
                    Forces("Applied", m1m3.appliedForces),
                    Forces("Measured", m1m3.forceActuatorData),
                    Forces("Hardpoints", m1m3.hardpointActuatorData),
                    PreclippedForces(
                        "<i>Pre-clipped Acceleration</i>",
                        m1m3.preclippedAccelerationForces,
                    ),
                    Forces(
                        "Applied Acceleration",
                        m1m3.appliedAccelerationForces,
                        ForceButton.create("acceleration", m1m3),
                    ),
                    ArrayFields(
                        [None, None, "fz", "mx", "my"],
                        "<i>Pre-clipped Active Optics</i>",
                        PreclippedLabel,
                        m1m3.preclippedActiveOpticForces,
                    ),
                    ArrayFields(
                        [None, None, "fz", "mx", "my", None, None],
                        "Applied Active Optics",
                        partial(UnitLabel, ".02f"),
                        m1m3.appliedActiveOpticForces,
                        ForceButton.create("activeOptic", m1m3),
                    ),
                    PreclippedForces(
                        "<i>Pre-clipped Azimuth</i>", m1m3.preclippedAzimuthForces
                    ),
                    Forces(
                        "Applied Azimuth",
                        m1m3.appliedAzimuthForces,
                        ForceButton.create("azimuth", m1m3),
                    ),
                    PreclippedForces(
                        "<i>Pre-clipped Balance</i>", m1m3.preclippedBalanceForces
                    ),
                    Forces(
                        "Applied Balance",
                        m1m3.appliedBalanceForces,
                        ForceButton.create("balance", m1m3),
                    ),
                    PreclippedForces(
                        "<i>Pre-clipped Elevation</i>", m1m3.preclippedElevationForces
                    ),
                    Forces("Applied Elevation", m1m3.appliedElevationForces),
                    PreclippedForces("Pre-clipped Offset", m1m3.preclippedOffsetForces),
                    Forces(
                        "Applied Offset",
                        m1m3.appliedOffsetForces,
                        ForceButton.create("offset", m1m3),
                    ),
                    PreclippedForces("Pre-clipped Static", m1m3.preclippedStaticForces),
                    Forces(
                        "Applied Static",
                        m1m3.appliedStaticForces,
                        ForceButton.create("static", m1m3),
                    ),
                    PreclippedForces(
                        "<i>Pre-clipped Thermal</i>", m1m3.preclippedThermalForces
                    ),
                    Forces(
                        "Applied Thermal",
                        m1m3.appliedThermalForces,
                        ForceButton.create("thermal", m1m3),
                    ),
                    PreclippedForces(
                        "<i>Pre-clipped Velocity</i>", m1m3.preclippedVelocityForces
                    ),
                    Forces(
                        "Applied Velocity",
                        m1m3.appliedVelocityForces,
                        ForceButton.create("velocity", m1m3),
                    ),
                ],
                Qt.Horizontal,
            )
        )

        plotLayout = QVBoxLayout()

        layout.addLayout(plotLayout)

        chartForces = ChartWidget(
            Axis("Force (N)", self.m1m3.appliedForces).addValue(
                "Total Mag", "forceMagnitude"
            ),
            max_items=50 * 5,
        )
        chartPercentage = ChartWidget(
            Axis("Percentage", self.m1m3.raisingLoweringInfo).addValue(
                "Weight Support Percentage", "weightSupportedPercent"
            ),
            max_items=50 * 5,
        )

        plotLayout = QHBoxLayout()

        plotLayout.addWidget(chartForces)
        plotLayout.addWidget(chartPercentage)

        layout.addLayout(plotLayout)

        self.setLayout(layout)
