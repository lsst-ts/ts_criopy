#!/usr/bin/env python3.8
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


from PySide2.QtCore import QSettings, Slot
from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QMainWindow,
    QHBoxLayout,
    QListWidget,
    QTabWidget,
    QGroupBox,
)

from asyncqt import asyncClose
import asyncio

from lsst.ts.idl.enums import MTM1M3

from .GUI.SAL import (
    Application,
    ApplicationControlWidget,
    SALLog,
    SALErrorCodeWidget,
    SALStatusBar,
)

from .M1M3 import (
    ActuatorOverviewPageWidget,
    AirPageWidget,
    CellLightPageWidget,
    DCAccelerometerPageWidget,
    EnabledForceActuators,
    ForceActuatorGraphPageWidget,
    ForceActuatorValuePageWidget,
    ForceBalanceSystemPageWidget,
    ForceActuatorBumpTestPageWidget,
    GyroPageWidget,
    HardpointsWidget,
    IMSPageWidget,
    InclinometerPageWidget,
    InterlockPageWidget,
    OffsetsWidget,
    OverviewPageWidget,
    PIDPageWidget,
    PowerPageWidget,
)
from .AirCompressor import CompressorsPageWidget


class EUI(QMainWindow):
    def __init__(self, m1m3, mtmount, compressor_1, compressor_2):
        super().__init__()
        self.m1m3 = m1m3
        self.mtmount = mtmount
        self.compressor_1 = compressor_1
        self.compressor_2 = compressor_2

        controlWidget = QGroupBox("Application Control")
        applicationControl = ApplicationControlWidget(self.m1m3)
        applicationControlLayout = QVBoxLayout()
        applicationControlLayout.addWidget(applicationControl)
        controlWidget.setLayout(applicationControlLayout)

        self.applicationPagination = QListWidget()
        self.applicationPagination.currentRowChanged.connect(self.changePage)

        self.tabWidget = QTabWidget()
        self.tabWidget.tabBar().hide()

        self.addPage("Overview", OverviewPageWidget(self.m1m3, self.mtmount))
        self.addPage("Actuator Overview", ActuatorOverviewPageWidget(self.m1m3))
        self.addPage("Hardpoints", HardpointsWidget(self.m1m3))
        self.addPage("Offsets", OffsetsWidget(self.m1m3))
        self.addPage("DC Accelerometers", DCAccelerometerPageWidget(self.m1m3))
        self.addPage("Gyro", GyroPageWidget(self.m1m3))
        self.addPage("IMS", IMSPageWidget(self.m1m3))
        self.addPage("Inclinometer", InclinometerPageWidget(self.m1m3))
        self.addPage("Interlock", InterlockPageWidget(self.m1m3))
        self.addPage("Lights", CellLightPageWidget(self.m1m3))
        self.addPage("Air", AirPageWidget(self.m1m3))
        self.addPage("Power", PowerPageWidget(self.m1m3))
        self.addPage("PID", PIDPageWidget(self.m1m3))
        self.addPage("Force Balance System", ForceBalanceSystemPageWidget(self.m1m3))
        self.addPage(
            "Force Actuator Bump Test", ForceActuatorBumpTestPageWidget(self.m1m3)
        )
        self.addPage("Enabled Force Actuators", EnabledForceActuators(self.m1m3))
        self.addPage("Force Actuator Graph", ForceActuatorGraphPageWidget(self.m1m3))
        self.addPage("Force Actuator Value", ForceActuatorValuePageWidget(self.m1m3))
        self.addPage("Compressor 1", CompressorsPageWidget(self.compressor_1))
        self.addPage("Compressor 2", CompressorsPageWidget(self.compressor_2))
        self.addPage("SAL Log", SALLog.Widget(self.m1m3))
        self.addPage("SAL Errors", SALErrorCodeWidget(self.m1m3))

        self.applicationPagination.setCurrentRow(0)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(controlWidget)
        leftLayout.addWidget(self.applicationPagination)

        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addWidget(self.tabWidget)

        m1m3Widget = QWidget()
        m1m3Widget.setLayout(layout)

        self.setCentralWidget(m1m3Widget)
        self.setStatusBar(SALStatusBar([self.m1m3, self.mtmount], detailedStateString))

        self.setMinimumSize(700, 400)

        settings = QSettings("LSST.TS", "M1M3GUI")
        try:
            self.restoreGeometry(settings.value("geometry"))
            self.restoreState(settings.value("windowState"))
        except AttributeError:
            self.resize(1000, 700)

    def addPage(self, name, widget):
        self.applicationPagination.addItem(name)
        self.tabWidget.addTab(widget, name)

    @Slot(int)
    def changePage(self, row):
        if row < 0:
            return
        self.tabWidget.setCurrentIndex(row)

    @asyncClose
    async def closeEvent(self, event):
        settings = QSettings("LSST.TS", "M1M3GUI")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        await asyncio.gather(
            self.m1m3.close(),
            self.mtmount.close(),
            self.compressor_1.close(),
            self.compressor_2.close(),
        )
        super().closeEvent(event)


def detailedStateString(detailedState):
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
        MTM1M3.DetailedState.PARKEDENGINEERING: "<font color='green'>Parked Engineering</font>",
        MTM1M3.DetailedState.RAISINGENGINEERING: "<font color='magenta'>Raising Engineering</font>",
        MTM1M3.DetailedState.ACTIVEENGINEERING: "<font color='blue'>Active Engineering</font>",
        MTM1M3.DetailedState.LOWERINGENGINEERING: "<font color='magenta'>Lowering Engineering</font>",
        MTM1M3.DetailedState.LOWERINGFAULT: "<font color='red'>Lowering Fault</font>",
        MTM1M3.DetailedState.PROFILEHARDPOINTCORRECTIONS: "<font color='red'>Profile Hardpoint Corrections</font>",
    }
    try:
        return _map[detailedState]
    except KeyError:
        return f"<font color='red'>Unknow : {detailedState}</font>"


def run():
    # Create the Qt Application
    app = Application(EUI)
    app.addComm("MTM1M3")
    app.addComm(
        "MTMount", include=["azimuth", "elevation", "heartbeat", "simulationMode"]
    )
    app.addComm("MTAirCompressor", index=1)
    app.addComm("MTAirCompressor", index=2)

    app.run()
