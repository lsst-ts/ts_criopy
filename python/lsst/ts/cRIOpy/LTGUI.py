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
import typing

from asyncqt import asyncClose
from lsst.ts import salobj
from lsst.ts.idl.enums import LaserTracker
from PySide2.QtCore import QSettings, Slot
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

from .LaserTracker import ApplicationControlWidget, OverviewPageWidget
from .GUI.SAL import Application, SALErrorCodeWidget, SALLog, SALStatusBar


class EUI(QMainWindow):
    def __init__(self, laser_tracker):
        super().__init__()
        self.laser_tracker = laser_tracker

        controlWidget = QGroupBox("Application Control")
        applicationControl = ApplicationControlWidget(self.laser_tracker)
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
            "Overview": partial(OverviewPageWidget, self.laser_tracker),
            "SAL Log": partial(SALLog.Widget, self.laser_tracker),
            "SAL Errors" : partial(SALErrorCodeWidget, self.laser_tracker),
        }

        self.windows = {}

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
        self.status_label = QLabel("Unknow")
        self.t2sa_label = QLabel("---")
        self.setStatusBar(SALStatusBar([self.laser_tracker], [self.status_label, self.t2sa_label]))

        self.laser_tracker.summaryState.connect(self.summary_state)
        self.laser_tracker.t2saStatus.connect(self.t2sa_status)
        self.laser_tracker.laserStatus.connect(self.laser_status)

        self.setMinimumSize(700, 400)

        settings = QSettings("LSST.TS", "LTGUI")
        try:
            self.restoreGeometry(settings.value("geometry"))
            self.restoreState(settings.value("windowState"))
        except AttributeError:
            self.resize(1000, 700)

    @Slot()
    def summary_state(self, data: typing.Any) -> None:
        self.status_label.setText(str(salobj.State(data.summaryState)))

    @Slot()
    def t2sa_status(self, data : typing.Any) -> None:
        self.t2sa_label.setText(str(LaserTracker.T2SAStatus(data.status)))

    @Slot()
    def laser_status(self, data : typing.Any) -> None:
        self.status_label.setText(str(LaserTracker.LaserStatus(data.status)))

    def addPage(self, name, widget):
        self.applicationPagination.addItem(name)
        self.tabWidget.addTab(widget, name)

    @Slot(bool)
    def make_window(self, checked):
        name = self.applicationPagination.currentItem().text()
        widget = self.TABS[name]()
        widget.setWindowTitle(f"{name}:{len(self.windows[name])+1}")
        widget.show()
        self.windows[name].append(widget)

    @Slot(int)
    def changePage(self, row):
        if row < 0:
            return
        self.tabWidget.setCurrentIndex(row)

    @asyncClose
    async def closeEvent(self, event):
        for windows in self.windows.values():
            for window in windows:
                window.close()
        settings = QSettings("LSST.TS", "LTGUI")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        await asyncio.gather(
            self.laser_tracker.close(),
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
        MTM1M3.DetailedState.PROFILEHARDPOINTCORRECTIONS: "<font color='red'>"
        "Profile Hardpoint Corrections</font>",
    }
    try:
        return _map[detailedState]
    except KeyError:
        return f"<font color='red'>Unknow : {detailedState}</font>"


def run():
    # Create the Qt Application
    app = Application(EUI)
    app.addComm("LaserTracker")

    app.run()
