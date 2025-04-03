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


from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.enums.MTM1M3 import DetailedStates
from PySide6.QtWidgets import QLabel

from .aircompressor import CompressorPageWidget
from .gui.sal import Application, EUIWindow, LogWidget, SALErrorCodeWidget, SALStatusBar
from .m1m3 import (
    ActuatorOverviewPageWidget,
    AirPageWidget,
    ApplicationControlWidget,
    BoosterValveWidget,
    CellLightPageWidget,
    DCAccelerometerPageWidget,
    ForceBalanceSystemPageWidget,
    GyroPageWidget,
    HardpointsWidget,
    HardpointTestPageWidget,
    IMSPageWidget,
    InclinometerPageWidget,
    InterlockPageWidget,
    LVDTPageWidget,
    OffsetsWidget,
    OuterLoopPageWidget,
    OverviewPageWidget,
    PIDPageWidget,
    PowerPageWidget,
    SlewControllerPageWidget,
    force_actuator,
)
from .salcomm import MetaSAL


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
        self.add_page("LVDT", LVDTPageWidget, self.m1m3)
        self.add_page("Inclinometer", InclinometerPageWidget, self.m1m3)
        self.add_page("Interlock", InterlockPageWidget, self.m1m3)
        self.add_page("Lights", CellLightPageWidget, self.m1m3)
        self.add_page("Air", AirPageWidget, self.m1m3)
        self.add_page("Power", PowerPageWidget, self.m1m3)
        self.add_page("PID", PIDPageWidget, self.m1m3)
        self.add_page("Force Balance System", ForceBalanceSystemPageWidget, self.m1m3)
        self.add_page("Slew Controller", SlewControllerPageWidget, self.m1m3)
        self.add_page("Booster Valve", BoosterValveWidget, self.m1m3)
        self.add_page(
            "Force Actuator Bump Test", force_actuator.BumpTestPageWidget, self.m1m3
        )
        self.add_page("Hardpoint Test", HardpointTestPageWidget, self.m1m3)
        self.add_page("Enabled Force Actuators", force_actuator.Enabled, self.m1m3)
        self.add_page("Force Actuator Graph", force_actuator.GraphPageWidget, self.m1m3)
        self.add_page(
            "Force Actuator Histogram", force_actuator.HistogramPageWidget, self.m1m3
        )
        self.add_page("Force Actuator Value", force_actuator.ValuePageWidget, self.m1m3)
        self.add_page("Compressor 1", CompressorPageWidget, self.compressor_1)
        self.add_page("Compressor 2", CompressorPageWidget, self.compressor_2)
        self.add_page("Outer loop", OuterLoopPageWidget, self.m1m3)
        self.add_page("SAL Log", LogWidget, self.m1m3)
        self.add_page("SAL Errors", SALErrorCodeWidget, self.m1m3)

        self.status_label = QLabel("Unknown")
        self.setStatusBar(SALStatusBar([self.m1m3, self.mtmount], [self.status_label]))

        self.m1m3.detailedState.connect(self.detailed_state)

    def detailed_state(self, data: BaseMsgType) -> None:
        self.status_label.setText(detailedStateString(data.detailedState))


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
        DetailedStates.DISABLED: "Disabled",
        DetailedStates.FAULT: "<font color='red'>Fault</font>",
        DetailedStates.OFFLINE: "<font color='red'>Offline</font>",
        DetailedStates.STANDBY: "Standby",
        DetailedStates.PARKED: "<font color='green'>Parked</font>",
        DetailedStates.RAISING: "<font color='magenta'>Raising</font>",
        DetailedStates.ACTIVE: "<font color='blue'>Active</font>",
        DetailedStates.LOWERING: "<font color='magenta'>Lowering</font>",
        DetailedStates.PARKEDENGINEERING: (
            "<font color='green'>Parked Engineering</font>"
        ),
        DetailedStates.RAISINGENGINEERING: (
            "<font color='magenta'>Raising Engineering</font>"
        ),
        DetailedStates.ACTIVEENGINEERING: (
            "<font color='blue'>Active Engineering</font>"
        ),
        DetailedStates.LOWERINGENGINEERING: (
            "<font color='magenta'>Lowering Engineering</font>"
        ),
        DetailedStates.LOWERINGFAULT: ("<font color='red'>Lowering Fault</font>"),
        DetailedStates.PROFILEHARDPOINTCORRECTIONS: (
            "<font color='red'>Profile Hardpoint Corrections</font>"
        ),
        DetailedStates.PAUSEDRAISING: "<font color='pink'>Paused Rasing</font>",
        DetailedStates.PAUSEDRAISINGENGINEERING: "<font color='pink'>Paused Rasing Engineering</font>",
        DetailedStates.PAUSEDLOWERING: "<font color='pink'>Paused Lowering</font>",
        DetailedStates.PAUSEDLOWERINGENGINEERING: "<font color='pink'>Paused Lowering Engineering</font>",
    }
    try:
        return _map[detailedState]
    except KeyError:
        return f"<font color='red'>Unknow : {detailedState}</font>"


def run() -> None:
    # Create the Qt Application
    app = Application(EUI)
    app.add_comm("MTM1M3", num_messages=500, consume_messages_timeout=0.2)
    app.add_comm(
        "MTMount",
        include=[
            "azimuth",
            "elevation",
            "heartbeat",
            "simulationMode",
            "softwareVersions",
        ],
    )
    app.add_comm("MTAirCompressor", index=1)
    app.add_comm("MTAirCompressor", index=2)

    app.run()
