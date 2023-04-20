#!/usr/bin/env python

from asyncqt import asyncClose
from PySide2.QtCore import QSettings, Qt
from PySide2.QtWidgets import QMainWindow

from .GUI.SAL import Application, SALLog, SALStatusBar
from .M1M3TS import (
    CoolantPumpWidget,
    FlowMeterWidget,
    GlycolLoopTemperatureWidget,
    MixingValveWidget,
    ThermalValuePageWidget,
)
from .M1M3TS.M1M3TSGUI import ThermalStatesDock


class EUI(QMainWindow):
    def __init__(self, m1m3ts):
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
    async def closeEvent(self, event):
        settings = QSettings("LSST.TS", "M1M3TSGUI")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        await self.m1m3ts.close()
        super().closeEvent(event)


def run():
    app = Application(EUI)
    app.addComm("MTM1M3TS")
    app.run()
