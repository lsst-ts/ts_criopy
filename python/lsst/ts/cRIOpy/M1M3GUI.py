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


import asyncio
from functools import partial

from asyncqt import asyncClose
from lsst.ts.idl.enums import MTM1M3
from PySide2.QtCore import QSettings, Slot
from PySide2.QtGui import QCloseEvent
from PySide2.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .AirCompressor import CompressorsPageWidget
from .GUI.SAL import Application, SALErrorCodeWidget, SALLog, SALStatusBar
from .GUI.SAL.SALComm import MetaSAL
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


class EUI(QMainWindow):
    def __init__(
        self,
        m1m3: MetaSAL,
        mtmount: MetaSAL,
        compressor_1: MetaSAL,
        compressor_2: MetaSAL,
    ):
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

        make_window = QPushButton("Open in &Window")
        make_window.clicked.connect(self.make_window)

        self.applicationPagination = QListWidget()
        self.applicationPagination.currentRowChanged.connect(self.changePage)

        self.tabWidget = QTabWidget()
        self.tabWidget.tabBar().hide()

        self.TABS = {
            "Overview": partial(OverviewPageWidget, self.m1m3, self.mtmount),
            "Actuator Overview": partial(ActuatorOverviewPageWidget, self.m1m3),
            "Hardpoints": partial(HardpointsWidget, self.m1m3),
            "Offsets": partial(OffsetsWidget, self.m1m3),
            "DC Accelerometers": partial(DCAccelerometerPageWidget, self.m1m3),
            "Gyro": partial(GyroPageWidget, self.m1m3),
            "IMS": partial(IMSPageWidget, self.m1m3),
            "Inclinometer": partial(InclinometerPageWidget, self.m1m3),
            "Interlock": partial(InterlockPageWidget, self.m1m3),
            "Lights": partial(CellLightPageWidget, self.m1m3),
            "Air": partial(AirPageWidget, self.m1m3),
            "Power": partial(PowerPageWidget, self.m1m3),
            "PID": partial(PIDPageWidget, self.m1m3),
            "Force Balance System": partial(ForceBalanceSystemPageWidget, self.m1m3),
            "Booster Valve": partial(BoosterValveWidget, self.m1m3),
            "Force Actuator Bump Test": partial(
                ForceActuator.BumpTestPageWidget, self.m1m3
            ),
            "Hardpoint Test": partial(HardpointTestPageWidget, self.m1m3),
            "Enabled Force Actuators": partial(ForceActuator.Enabled, self.m1m3),
            "Force Actuator Graph": partial(ForceActuator.GraphPageWidget, self.m1m3),
            "Force Actuator Histogram": partial(
                ForceActuator.HistogramPageWidget, self.m1m3
            ),
            "Force Actuator Value": partial(ForceActuator.ValuePageWidget, self.m1m3),
            "Compressor 1": partial(CompressorsPageWidget, self.compressor_1),
            "Compressor 2": partial(CompressorsPageWidget, self.compressor_2),
            "SAL Log": partial(SALLog.Widget, self.m1m3),
            "SAL Errors": partial(SALErrorCodeWidget, self.m1m3),
        }

        self.windows: dict[str, QWidget] = {}

        for title, tab in self.TABS.items():
            self.addPage(title, tab())
            self.windows[title] = []

        self.applicationPagination.setCurrentRow(0)

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(controlWidget)
        leftLayout.addWidget(make_window)
        leftLayout.addWidget(self.applicationPagination)

        layout = QHBoxLayout()
        layout.addLayout(leftLayout)
        layout.addWidget(self.tabWidget)

        m1m3Widget = QWidget()
        m1m3Widget.setLayout(layout)

        self.setCentralWidget(m1m3Widget)

        self.statusLabel = QLabel("Unknown")
        self.setStatusBar(SALStatusBar([self.m1m3, self.mtmount], [self.statusLabel]))

        self.setMinimumSize(700, 400)

        self.m1m3.detailedState.connect(self.detailed_state)

        settings = QSettings("LSST.TS", "M1M3GUI")
        try:
            self.restoreGeometry(settings.value("geometry"))
            self.restoreState(settings.value("windowState"))
        except AttributeError:
            self.resize(1000, 700)

    def detailed_state(self, data):
        self.statusLabel.setText(detailedStateString(data.detailedState))

    def addPage(self, name: str, widget: QWidget) -> None:
        self.applicationPagination.addItem(name)
        self.tabWidget.addTab(widget, name)

    @Slot()
    def make_window(self, checked: bool) -> None:
        name = self.applicationPagination.currentItem().text()
        widget = self.TABS[name]()
        widget.setWindowTitle(f"{name}:{len(self.windows[name])+1}")
        widget.show()
        self.windows[name].append(widget)

    def changePage(self, row: int) -> None:
        if row < 0:
            return
        self.tabWidget.setCurrentIndex(row)

    @asyncClose
    async def closeEvent(self, event: QCloseEvent) -> None:
        for windows in self.windows.values():
            for window in windows:
                window.close()
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
        MTM1M3.DetailedState.PARKEDENGINEERING: "<font color='green'>Parked Engineering</font>",
        MTM1M3.DetailedState.RAISINGENGINEERING: "<font color='magenta'>Raising Engineering</font>",
        MTM1M3.DetailedState.ACTIVEENGINEERING: "<font color='blue'>Active Engineering</font>",
        MTM1M3.DetailedState.LOWERINGENGINEERING: "<font color='magenta'>Lowering Engineering</font>",
        MTM1M3.DetailedState.LOWERINGFAULT: "<font color='red'>Lowering Fault</font>",
        MTM1M3.DetailedState.PROFILEHARDPOINTCORRECTIONS: "<font color='red'>"
        "Profile Hardpoint Corrections</font>",
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
