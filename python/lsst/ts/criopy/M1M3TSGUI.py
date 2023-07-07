#!/usr/bin/env python

# This file is part of M1M3 TS GUI.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from PySide2.QtCore import QSettings, Qt
from PySide2.QtGui import QCloseEvent
from PySide2.QtWidgets import QMainWindow
from qasync import asyncClose

from .gui.sal import Application, SALLog, SALStatusBar
from .m1m3ts import (
    CoolantPumpWidget,
    FlowMeterWidget,
    GlycolLoopTemperatureWidget,
    MixingValveWidget,
    ThermalValuePageWidget,
)
from .m1m3ts.M1M3TSGUI import ThermalStatesDock
from .salcomm import MetaSAL


class EUI(QMainWindow):
    def __init__(self, m1m3ts: MetaSAL):
        super().__init__()

        self.m1m3ts = m1m3ts

        self.setStatusBar(SALStatusBar([self.m1m3ts]))

        thermalValues = ThermalValuePageWidget(self.m1m3ts)
        mixingValve = MixingValveWidget(self.m1m3ts)
        coolantPump = CoolantPumpWidget(self.m1m3ts)
        glycolLoopTemperature = GlycolLoopTemperatureWidget(self.m1m3ts)
        flowMeter = FlowMeterWidget(self.m1m3ts)
        stateDock = ThermalStatesDock(self.m1m3ts)
        logDock = SALLog.Dock(self.m1m3ts)

        menuBar = self.menuBar()

        viewMenu = menuBar.addMenu("&Views")
        viewMenu.addAction(thermalValues.toggleViewAction())
        viewMenu.addAction(mixingValve.toggleViewAction())
        viewMenu.addAction(coolantPump.toggleViewAction())
        viewMenu.addAction(glycolLoopTemperature.toggleViewAction())
        viewMenu.addAction(flowMeter.toggleViewAction())
        viewMenu.addSeparator()
        viewMenu.addAction(stateDock.toggleViewAction())
        viewMenu.addAction(logDock.toggleViewAction())

        settings = QSettings("LSST.TS", "M1M3TSGUI")
        try:
            self.restoreGeometry(settings.value("geometry"))
            self.restoreState(settings.value("windowState"))
        except AttributeError:
            self.resize(1000, 700)

        self.addDockWidget(Qt.RightDockWidgetArea, thermalValues)
        self.addDockWidget(Qt.RightDockWidgetArea, mixingValve)
        self.addDockWidget(Qt.RightDockWidgetArea, coolantPump)
        self.addDockWidget(Qt.RightDockWidgetArea, glycolLoopTemperature)
        self.addDockWidget(Qt.RightDockWidgetArea, flowMeter)
        self.addDockWidget(Qt.LeftDockWidgetArea, stateDock)
        self.addDockWidget(Qt.BottomDockWidgetArea, logDock)

        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)

    @asyncClose
    async def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings("LSST.TS", "M1M3TSGUI")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        await self.m1m3ts.close()
        super().closeEvent(event)


def run() -> None:
    app = Application(EUI)
    app.addComm("MTM1M3TS")
    app.run()
