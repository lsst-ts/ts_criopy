#!/usr/bin/env python3.8

from functools import partial

from PySide2.QtCore import Slot, Signal, QSettings, Qt
from PySide2.QtWidgets import QMainWindow

import astropy.units as u
from asyncqt import asyncClose
import numpy as np

from .GUI.SAL import SALLog, Application
from .VMS import (
    BoxChartWidget,
    Cache,
    DisplacementWidget,
    ToolBar,
    StatusBar,
    PSDWidget,
    VelocityWidget,
    RawAccelerationWidget,
)


class EUI(QMainWindow):
    SAMPLE_TIME = 1 * u.ms.to(u.s)
    """Sample time (seconds)"""

    SYSTEMS = ["M1M3", "M2", "Rotator"]

    cacheUpdated = Signal(int, int, float, float)

    def __init__(self, *comms):
        super().__init__()

        self.comms = comms

        for comm in self.comms:
            comm.data.connect(self.data)

        self.caches = [Cache(0, 3), Cache(0, 6), Cache(0, 3)]

        logDock = SALLog.Dock(self.comms)

        menuBar = self.menuBar()

        viewMenu = menuBar.addMenu("&Views")
        viewMenu.addAction(logDock.toggleViewAction())
        viewMenu.addSeparator()
        viewMenu.addAction("Remove all", self.removeAll)

        i = 0
        for s in self.SYSTEMS:
            m = menuBar.addMenu(s)
            m.addAction(
                "New &raw graph",
                partial(
                    self._addCacheWidget, i, "Raw acceleration", RawAccelerationWidget
                ),
            )
            m.addAction("New &box graph", partial(self.addBox, i))
            m.addAction(
                "New &PSD graph", partial(self._addCacheWidget, i, "PSD", PSDWidget)
            )
            m.addAction(
                "New &Velocity graph",
                partial(self._addCacheWidget, i, "Velocity", VelocityWidget),
            )
            m.addAction(
                "New &Displacement graph",
                partial(self._addCacheWidget, i, "Displacement", DisplacementWidget),
            )
            i += 1

        self.toolBar = ToolBar()
        self.addToolBar(self.toolBar)

        self.statusBar = StatusBar(self.SYSTEMS, self.SAMPLE_TIME)
        self.cacheUpdated.connect(self.statusBar.cacheUpdated)
        self.setStatusBar(self.statusBar)

        self.addDockWidget(Qt.BottomDockWidgetArea, logDock)

        self.setMinimumSize(700, 400)

        settings = QSettings("LSST.TS", "VMSGUI")
        try:
            self.restoreGeometry(settings.value("geometry"))
            self.restoreState(settings.value("windowState"))
        except AttributeError:
            self.resize(1000, 700)

        self.toolBar.intervalChanged.connect(self.intervalChanged)

        self.toolBar.frequencyChanged.emit(*self.toolBar.getFrequencyRange())
        self.toolBar.intervalChanged.emit(self.toolBar.interval.value())

        self.toolBar.intervalChanged.connect(self.intervalChanged)

        self.toolBar.frequencyChanged.emit(*self.toolBar.getFrequencyRange())
        self.toolBar.intervalChanged.emit(self.toolBar.interval.value())

    def _addCacheWidget(self, index, prefix, ChartTypeClass):
        prefix = prefix + " " + self.SYSTEMS[index] + ":"
        id = self.getNextId(prefix)
        aWidget = ChartTypeClass(
            prefix + str(id),
            self.caches[index],
            self.SAMPLE_TIME,
            self.toolBar,
        )
        self.cacheUpdated.connect(aWidget.cacheUpdated)
        self.toolBar.frequencyChanged.connect(aWidget.frequencyChanged)
        self.toolBar.integralBinningChanged.connect(aWidget.integralBinningChanged)
        self.addDockWidget(Qt.TopDockWidgetArea, aWidget)

    def addBox(self, index):
        prefix = "Box " + self.SYSTEMS[index] + ":"
        id = self.getNextId(prefix)
        self.addDockWidget(
            Qt.TopDockWidgetArea,
            BoxChartWidget(prefix + str(id), self.comms[index], []),
        )

    def removeAll(self):
        for child in self.children():
            if child.objectName()[:3] in ["PSD", "Box", "Vel", "Acc"]:
                self.removeDockWidget(child)
                del child

    def getNextId(self, prefix):
        id = 1
        for child in self.children():
            if child.objectName().startswith(prefix):
                id = int(child.objectName()[len(prefix) :]) + 1
        return id

    @Slot(map)
    def data(self, data):
        cache = self.caches[data.MTVMSID - 1]
        added, chunk_removed = cache.newChunk(data, self.SAMPLE_TIME)
        if added:
            self.cacheUpdated.emit(
                data.MTVMSID - 1,
                len(cache),
                cache.startTime(),
                cache.endTime(),
            )

    @Slot(float)
    def intervalChanged(self, interval):
        newSize = int(np.ceil(interval / self.SAMPLE_TIME))
        for cache in self.caches:
            cache.resize(newSize)

    @asyncClose
    async def closeEvent(self, event):
        settings = QSettings("LSST.TS", "VMSGUI")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        self.toolBar.storeSettings()
        for comm in self.comms:
            await comm.close()
        super().closeEvent(event)


def run():
    # Create the Qt Application
    app = Application(EUI)
    for index in range(1, 4):
        app.addComm("MTVMS", index=index, manual={"data": {"queue_len": 400}})
    app.run()
