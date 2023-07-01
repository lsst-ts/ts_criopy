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
from functools import partial

from asyncqt import asyncSlot
from lsst.ts.idl.enums.MTM1M3 import DetailedState, EnableDisableForceComponent
from PySide2.QtCore import Qt, Signal, Slot
from PySide2.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QWidget

from ..gui import ArrayFields, ArrayGrid, ColoredButton, UnitLabel
from ..gui.sal import Axis, ChartWidget
from ..salcomm import MetaSAL, command


class ForceButton(ColoredButton):
    def __init__(self, enable: bool, name: str, m1m3: MetaSAL):
        super().__init__("Enable" if enable else "Disable")
        self.setObjectName(name)
        self.m1m3 = m1m3

        self.__enable = enable
        self.__engineering_state = False

        self.clicked.connect(self.enable_force)
        self.m1m3.forceActuatorState.connect(self.force_actuator_state)
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
    def force_actuator_state(self, data: typing.Any) -> None:
        applied = getattr(data, self.objectName() + "ForcesApplied")
        if applied:
            self.setColor(Qt.green if self.__enable else None)
        else:
            self.setColor(None if self.__enable else Qt.red)

        if self.__engineering_state:
            self.set_button_enable(applied)

    @Slot()
    def detailed_state(self, data: typing.Any) -> None:
        self.__engineering_state = data.detailedState == DetailedState.ACTIVEENGINEERING
        if self.__engineering_state:
            force_state = self.m1m3.remote.evt_forceActuatorState.get()
            if force_state is not None:
                self.set_button_enable(
                    getattr(force_state, self.objectName() + "ForcesApplied")
                )
            else:
                self.setEnabled(True)
        else:
            self.setDisabled(True)


class Forces(ArrayFields):
    def __init__(
        self,
        label: str,
        signal: Signal,
        force_component: tuple[str, MetaSAL] | None = None,
    ):
        extra_widgets: list[QWidget] = []
        if force_component is not None:
            extra_widgets = [
                ForceButton(True, *force_component),
                ForceButton(False, *force_component),
            ]

        super().__init__(
            ["fx", "fy", "fz", "mx", "my", "mz", "forceMagnitude"],
            label,
            partial(UnitLabel, ".02f"),
            signal,
            extra_widgets=extra_widgets,
        )


class PreclippedLabel(UnitLabel):
    def __init__(self, fmt: str = ".02f"):
        super().__init__(".02f")

    def setValue(self, value: float) -> None:
        self.setText(f"<i>{(value * self.scale):{self.fmt}}{self.unit_name}</i>")


class PreclippedForces(ArrayFields):
    def __init__(self, label: str, signal: Signal):
        super().__init__(
            ["fx", "fy", "fz", "mx", "my", "mz", "forceMagnitude"],
            f"<i>{label}</i>",
            PreclippedLabel,
            signal,
        )


class ActuatorOverviewPageWidget(QWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        self.m1m3 = m1m3

        layout = QVBoxLayout()
        dataLayout = QGridLayout()
        dataLayout.addWidget(
            ArrayGrid(
                "<b>Forces</b>",
                [
                    "<b>Force X</b> (N)",
                    "<b>Force Y</b> (N)",
                    "<b>Force Z</b> (N)",
                    "<b>Moment X</b> (Nm)",
                    "<b>Moment Y</b> (Nm)",
                    "<b>Moment Z</b> (Nm)",
                    "<b>Magnitude</b> (N)",
                ],
                [
                    PreclippedForces("Pre-clipped", m1m3.preclippedForces),
                    Forces("Applied", m1m3.appliedForces),
                    Forces("Measured", m1m3.forceActuatorData),
                    Forces("Hardpoints", m1m3.hardpointActuatorData),
                    PreclippedForces(
                        "Pre-clipped Acceleration",
                        m1m3.preclippedAccelerationForces,
                    ),
                    Forces(
                        "Applied Acceleration",
                        m1m3.appliedAccelerationForces,
                        ("acceleration", m1m3),
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
                        extra_widgets=[
                            ForceButton(True, "activeOptic", m1m3),
                            ForceButton(False, "activeOptic", m1m3),
                        ],
                    ),
                    PreclippedForces(
                        "Pre-clipped Azimuth", m1m3.preclippedAzimuthForces
                    ),
                    Forces(
                        "Applied Azimuth", m1m3.appliedAzimuthForces, ("azimuth", m1m3)
                    ),
                    PreclippedForces(
                        "Pre-clipped Balance", m1m3.preclippedBalanceForces
                    ),
                    Forces(
                        "Applied Balance", m1m3.appliedBalanceForces, ("balance", m1m3)
                    ),
                    PreclippedForces(
                        "Pre-clipped Elevation", m1m3.preclippedElevationForces
                    ),
                    Forces("Applied Elevation", m1m3.appliedElevationForces),
                    PreclippedForces("Pre-clipped Offset", m1m3.preclippedOffsetForces),
                    Forces(
                        "Applied Offset", m1m3.appliedOffsetForces, ("offset", m1m3)
                    ),
                    PreclippedForces("Pre-clipped Static", m1m3.preclippedStaticForces),
                    Forces(
                        "Applied Static", m1m3.appliedStaticForces, ("static", m1m3)
                    ),
                    PreclippedForces(
                        "Pre-clipped Thermal", m1m3.preclippedThermalForces
                    ),
                    Forces(
                        "Applied Thermal", m1m3.appliedThermalForces, ("thermal", m1m3)
                    ),
                    PreclippedForces(
                        "Pre-clipped Velocity", m1m3.preclippedVelocityForces
                    ),
                    Forces(
                        "Applied Velocity",
                        m1m3.appliedVelocityForces,
                        ("velocity", m1m3),
                    ),
                ],
                Qt.Horizontal,
            )
        )

        plotLayout = QVBoxLayout()

        layout.addLayout(dataLayout)
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
