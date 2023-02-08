#!/usr/bin/env python

from functools import partial

import astropy.units as u
from PySide2.QtCore import Slot, Signal, QSettings, Qt
from PySide2.QtWidgets import QMainWindow

from asyncqt import asyncClose

from .GUI.SAL import SALLog, Application
from .VMS import (
    BoxChartWidget,
    Cache,
    CSCPSDWidget,
    DisplacementWidget,
    MiscellaneousWidget,
    ToolBar,
    StatusBar,
    PSDWidget,
    VelocityWidget,
    RawAccelerationWidget,
)


class EUI(QMainWindow):
    SYSTEMS = ["M1M3", "M2", "Rotator"]

    cacheUpdated = Signal(int, int, float, float)

    def __init__(self, *comms):
        super().__init__()

        self.caches = [Cache(1000, 3), Cache(1000, 6), Cache(1000, 3)]

        self.comms = comms

        for comm in self.comms:
            comm.data.connect(self.data)
            comm.fpgaState.connect(self.fpgaState)

        logDock = SALLog.Dock(self.comms)

        menuBar = self.menuBar()

        viewMenu = menuBar.addMenu("&Views")
        viewMenu.addAction(logDock.toggleViewAction())
        viewMenu.addSeparator()
        viewMenu.addAction("Remove all", self.removeAll)

        self._miscellaneous = []

        for i, s in enumerate(self.SYSTEMS):
            m = menuBar.addMenu(s)
            m.addAction(
                "New &raw graph",
                partial(
                    self._addCacheWidget, i, "Raw acceleration", RawAccelerationWidget
                ),
            )
            m.addAction("New &box graph", partial(self._addBox, i))
            m.addAction(
                "New &PSD graph", partial(self._addCacheWidget, i, "PSD", PSDWidget)
            )
            m.addAction("&CSC PSD graph", partial(self._addCSCPSDWidget, i))
            m.addAction(
                "New &Velocity graph",
                partial(self._addCacheWidget, i, "Velocity", VelocityWidget),
            )
            m.addAction(
                "New &Displacement graph",
                partial(self._addCacheWidget, i, "Displacement", DisplacementWidget),
            )
            m.addSeparator()

            self._miscellaneous.append(
                MiscellaneousWidget("Miscellaneous " + s, self.comms[i])
            )
            m.addAction("&Miscellaneous", partial(self._showMiscellaneous, i))

        self.toolBar = ToolBar()
        self.addToolBar(self.toolBar)

        self.statusBar = StatusBar(self.SYSTEMS)
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

    def _addCSCPSDWidget(self, index):
        prefix = "CSC PSD " + self.SYSTEMS[index] + ":"
        id = self.getNextId(prefix)
        aWidget = CSCPSDWidget(
            prefix + str(id),
            self.toolBar,
            self.comms[index].psd,
            self.caches[index].sensors(),
        )
        self.toolBar.frequencyChanged.connect(aWidget.frequencyChanged)
        self.addDockWidget(Qt.TopDockWidgetArea, aWidget)

    def _addCacheWidget(self, index, prefix, ChartTypeClass):
        prefix = prefix + " " + self.SYSTEMS[index] + ":"
        id = self.getNextId(prefix)
        aWidget = ChartTypeClass(
            prefix + str(id),
            self.caches[index],
            self.toolBar,
        )
        self.cacheUpdated.connect(aWidget.cacheUpdated)
        self.toolBar.frequencyChanged.connect(aWidget.frequencyChanged)
        self.toolBar.integralBinningChanged.connect(aWidget.integralBinningChanged)
        self.addDockWidget(Qt.TopDockWidgetArea, aWidget)

    def _addBox(self, index):
        prefix = "Box " + self.SYSTEMS[index] + ":"
        id = self.getNextId(prefix)
        self.addDockWidget(
            Qt.TopDockWidgetArea,
            BoxChartWidget(prefix + str(id), self.comms[index], []),
        )

    def _showMiscellaneous(self, index):
        widget = self._miscellaneous[index]
        if widget.isHidden():
            self.addDockWidget(Qt.TopDockWidgetArea, widget)
            widget.show()

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
        cache = self.caches[data.salIndex - 1]
        added, chunk_removed = cache.newChunk(data)
        if added:
            self.cacheUpdated.emit(
                data.salIndex - 1,
                len(cache),
                cache.startTime(),
                cache.endTime(),
            )

    @Slot(map)
    def fpgaState(self, fpgaState):
        index = fpgaState.salIndex - 1
        self.statusBar.sampleTimes[index] = fpgaState.period
        self.caches[index].setSampleTime(fpgaState.period * u.ms.to(u.s))

    @Slot(float)
    def intervalChanged(self, interval):
        for i, c in enumerate(self.caches):
            c.setInterval(interval)

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
