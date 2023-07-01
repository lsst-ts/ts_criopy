# -'''- coding: utf-8 -'''-

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

# You should have received a copy of the GNU General Public License along with
# this program.If not, see <https://www.gnu.org/licenses/>.

import typing

from lsst.ts.idl.enums import MTM1M3
from PySide2.QtWidgets import QLabel

from .AirCompressor import CompressorsPageWidget
from .GUI.SAL import Application, EUIWindow, SALErrorCodeWidget, SALLog, SALStatusBar
from .M1M3 import (
    ActuatorOverviewPageWidget,
    AirPageWidget,
    ApplicationControlWidget,
    BoosterValveWidget,
    CellLightPageWidget,
    DCAccelerometerPageWidget,
    ForceActuator,
    ForceBalanceSystemPageWidget,
    GyroPageWidget,
    HardpointsWidget,
    HardpointTestPageWidget,
    IMSPageWidget,
    InclinometerPageWidget,
    InterlockPageWidget,
    OffsetsWidget,
    OverviewPageWidget,
    PIDPageWidget,
    PowerPageWidget,
)
from .SALComm import MetaSAL


class EUI(EUIWindow):
    def __init__(
        self,
        m1m3: MetaSAL,
        mtmount: MetaSAL,
        compressor_1: MetaSAL,
        compressor_2: MetaSAL,
    ):
        super().__init__(
            "M1M3GUI",
            [m1m3, mtmount, compressor_1, compressor_2],
            (700, 400),
            ApplicationControlWidget(m1m3),
        )
        self.m1m3 = m1m3
        self.mtmount = mtmount
        self.compressor_1 = compressor_1
        self.compressor_2 = compressor_2

        self.add_page("Overview", OverviewPageWidget, self.m1m3, self.mtmount)
        self.add_page("Actuator Overview", ActuatorOverviewPageWidget, self.m1m3)
        self.add_page("Hardpoints", HardpointsWidget, self.m1m3)
        self.add_page("Offsets", OffsetsWidget, self.m1m3)
        self.add_page("DC Accelerometers", DCAccelerometerPageWidget, self.m1m3)
        self.add_page("Gyro", GyroPageWidget, self.m1m3)
        self.add_page("IMS", IMSPageWidget, self.m1m3)
        self.add_page("Inclinometer", InclinometerPageWidget, self.m1m3)
        self.add_page("Interlock", InterlockPageWidget, self.m1m3)
        self.add_page("Lights", CellLightPageWidget, self.m1m3)
        self.add_page("Air", AirPageWidget, self.m1m3)
        self.add_page("Power", PowerPageWidget, self.m1m3)
        self.add_page("PID", PIDPageWidget, self.m1m3)
        self.add_page("Force Balance System", ForceBalanceSystemPageWidget, self.m1m3)
        self.add_page("Booster Valve", BoosterValveWidget, self.m1m3)
        self.add_page(
            "Force Actuator Bump Test", ForceActuator.BumpTestPageWidget, self.m1m3
        )
        self.add_page("Hardpoint Test", HardpointTestPageWidget, self.m1m3)
        self.add_page("Enabled Force Actuators", ForceActuator.Enabled, self.m1m3)
        self.add_page("Force Actuator Graph", ForceActuator.GraphPageWidget, self.m1m3)
        self.add_page(
            "Force Actuator Histogram", ForceActuator.HistogramPageWidget, self.m1m3
        )
        self.add_page("Force Actuator Value", ForceActuator.ValuePageWidget, self.m1m3)
        self.add_page("Compressor 1", CompressorsPageWidget, self.compressor_1)
        self.add_page("Compressor 2", CompressorsPageWidget, self.compressor_2)
        self.add_page("SAL Log", SALLog.Widget, self.m1m3)
        self.add_page("SAL Errors", SALErrorCodeWidget, self.m1m3)

        self.statusLabel = QLabel("Unknown")
        self.setStatusBar(SALStatusBar([self.m1m3, self.mtmount], [self.statusLabel]))

        self.m1m3.detailedState.connect(self.detailed_state)

    def detailed_state(self, data: typing.Any) -> None:
        self.statusLabel.setText(detailedStateString(data.detailedState))


def detailedStateString(detailedState: int) -> str:
    """Returns string description of mirror state.

    Parameters
    ----------
    detailedState : `int`
        M1M3 detailed state.

    Returns
    -------
    stateString : `str`
        HTML string (usable in Qt) description of detailed state."""
    _map = {
        MTM1M3.DetailedState.DISABLED: "Disabled",
        MTM1M3.DetailedState.FAULT: "<font color='red'>Fault</font>",
        MTM1M3.DetailedState.OFFLINE: "<font color='red'>Offline</font>",
        MTM1M3.DetailedState.STANDBY: "Standby",
        MTM1M3.DetailedState.PARKED: "<font color='green'>Parked</font>",
        MTM1M3.DetailedState.RAISING: "<font color='magenta'>Raising</font>",
        MTM1M3.DetailedState.ACTIVE: "<font color='blue'>Active</font>",
        MTM1M3.DetailedState.LOWERING: "<font color='magenta'>Lowering</font>",
        MTM1M3.DetailedState.PARKEDENGINEERING: (
            "<font color='green'>Parked Engineering</font>"
        ),
        MTM1M3.DetailedState.RAISINGENGINEERING: (
            "<font color='magenta'>Raising Engineering</font>"
        ),
        MTM1M3.DetailedState.ACTIVEENGINEERING: (
            "<font color='blue'>Active Engineering</font>"
        ),
        MTM1M3.DetailedState.LOWERINGENGINEERING: (
            "<font color='magenta'>Lowering Engineering</font>"
        ),
        MTM1M3.DetailedState.LOWERINGFAULT: ("<font color='red'>Lowering Fault</font>"),
        MTM1M3.DetailedState.PROFILEHARDPOINTCORRECTIONS: (
            "<font color='red'>Profile Hardpoint Corrections</font>"
        ),
    }
    try:
        return _map[detailedState]
    except KeyError:
        return f"<font color='red'>Unknow : {detailedState}</font>"


def run() -> None:
    # Create the Qt Application
    app = Application(EUI)
    app.addComm("MTM1M3")
    app.addComm(
        "MTMount",
        include=[
            "azimuth",
            "elevation",
            "heartbeat",
            "simulationMode",
            "softwareVersions",
        ],
    )
    app.addComm("MTAirCompressor", index=1)
    app.addComm("MTAirCompressor", index=2)

    app.run()
