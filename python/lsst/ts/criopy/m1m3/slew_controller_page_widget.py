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

from lsst.ts.xml.enums.MTM1M3 import DetailedStates, SetSlewControllerSettings
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QVBoxLayout, QWidget
from qasync import asyncSlot

from ..gui import ArrayItem, ArrayLabels, ColoredButton, Force
from ..gui.sal import Axis, ChartWidget
from ..salcomm import MetaSAL, command
from .force_grid import Forces, ForcesGrid, PreclippedForces


class ForceButton(ColoredButton):
    def __init__(self, use: bool, name: str, m1m3: MetaSAL):
        super().__init__("Use" if use else "Do not use")
        self.setObjectName(name)
        self.m1m3 = m1m3

        self.__use = use
        self.__active_state = False

        self.clicked.connect(self.enable_force)
        self.m1m3.slewControllerSettings.connect(self.slew_controller_settings)
        self.m1m3.detailedState.connect(self.detailed_state)

    @asyncSlot()
    async def enable_force(self) -> None:
        await command(
            self,
            self.m1m3.remote.cmd_setSlewControllerSettings,
            slewSettings=int(
                getattr(SetSlewControllerSettings, self.objectName().upper())
            ),
            enableSlewManagement=self.__use,
        )

    def set_button_enable(self, use: bool) -> None:
        self.setDisabled(use if self.__use else not (use))

    @Slot()
    def slew_controller_settings(self, data: typing.Any) -> None:
        name = self.objectName()
        if name == "BoosterValves":
            use = getattr(data, "trigger" + name)
        else:
            use = getattr(data, "use" + name)

        if use:
            self.setColor(Qt.green if self.__use else None)
        else:
            self.setColor(None if self.__use else Qt.red)

        if self.__active_state:
            self.set_button_enable(use)

    @Slot()
    def detailed_state(self, data: typing.Any) -> None:
        self.__active_state = data.detailedState in (
            DetailedStates.PARKEDENGINEERING,
            DetailedStates.RAISINGENGINEERING,
            DetailedStates.ACTIVEENGINEERING,
            DetailedStates.LOWERINGENGINEERING,
        )
        if self.__active_state:
            slew_controller_settings = self.m1m3.remote.evt_slewControllerSettings.get()
            if slew_controller_settings is not None:
                self.slew_controller_settings(slew_controller_settings)
            else:
                self.setEnabled(True)
        else:
            self.setDisabled(True)

    @classmethod
    def create(cls, name: str, m1m3: MetaSAL) -> list["ForceButton"]:
        return [ForceButton(True, name, m1m3), ForceButton(False, name, m1m3)]


class SlewControllerPageWidget(QWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        self.m1m3 = m1m3

        layout = QVBoxLayout()

        bv_buttons = [None] + ForceButton.create("BoosterValves", m1m3)

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
                        ForceButton.create("AccelerationForces", m1m3),
                    ),
                    PreclippedForces(
                        "<i>Pre-clipped Balance</i>", m1m3.preclippedBalanceForces
                    ),
                    Forces(
                        "Applied Balance",
                        m1m3.appliedBalanceForces,
                        ForceButton.create("BalanceForces", m1m3),
                    ),
                    PreclippedForces(
                        "<i>Pre-clipped Velocity</i>", m1m3.preclippedVelocityForces
                    ),
                    Forces(
                        "Applied Velocity",
                        m1m3.appliedVelocityForces,
                        ForceButton.create("VelocityForces", m1m3),
                    ),
                    ArrayLabels(*[f"<b>HP {i}</b>" for i in range(1, 7)]),
                    ArrayItem(
                        "measuredForce",
                        "Booster Valves",
                        Force,
                        m1m3.hardpointActuatorData,
                        extra_widgets=bv_buttons,
                    ),
                ],
                Qt.Horizontal,
            )
        )

        acceleration_axis = Axis(
            "Acceleration (N, Nm)", self.m1m3.appliedAccelerationForces
        )
        balance_axis = Axis("Balance (N, Nm)", self.m1m3.appliedBalanceForces)
        velocity_axis = Axis("Velocity (N, Nm)", self.m1m3.appliedVelocityForces)

        for ax in "xyz":
            acceleration_axis.addValue(ax.upper(), f"f{ax}")
            balance_axis.addValue(ax.upper(), f"f{ax}")
            velocity_axis.addValue(ax.upper(), f"f{ax}")

        for ax in "xyz":
            acceleration_axis.addValue("Moment " + ax.upper(), f"m{ax}")
            balance_axis.addValue("Moment " + ax.upper(), f"m{ax}")
            velocity_axis.addValue("Moment " + ax.upper(), f"m{ax}")

        layout.addWidget(ChartWidget(acceleration_axis, max_items=50 * 5))
        layout.addWidget(ChartWidget(balance_axis, max_items=50 * 5))
        layout.addWidget(ChartWidget(velocity_axis, max_items=50 * 5))

        self.setLayout(layout)
