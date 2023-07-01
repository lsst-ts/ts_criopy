#!/usr/bin/env python

# This file is part of cRIO/VMS GUI.
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
from functools import partial

import astropy.units as u
from asyncqt import asyncClose
from PySide2.QtCore import QSettings, Qt, Signal, Slot
from PySide2.QtGui import QCloseEvent
from PySide2.QtWidgets import QMainWindow

from .gui.SAL import Application, SALLog
from .salcomm import MetaSAL
from .VMS import (
    BoxChartWidget,
    Cache,
    CacheWidget,
    CSCPSDWidget,
    DisplacementWidget,
    MiscellaneousWidget,
    PSDWidget,
    RawAccelerationWidget,
    StatusBar,
    ToolBar,
    VelocityWidget,
)


class EUI(QMainWindow):
    SYSTEMS = ["M1M3", "M2", "Rotator"]

    cacheUpdated = Signal(int, int, float, float)

    def __init__(self, *comms: MetaSAL):
        super().__init__()

        self.caches = [Cache(1000, 3), Cache(1000, 6), Cache(1000, 3)]

        self.comms = comms

        for comm in self.comms:
            comm.data.connect(self.data)
            comm.fpgaState.connect(self.fpgaState)

        logDock = SALLog.Dock(*self.comms)

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
                    self._addCacheWidget,
                    i,
                    "Raw acceleration",
                    RawAccelerationWidget,
                ),
            )
            m.addAction("New &box graph", partial(self._addBox, i))
            m.addAction(
                "New &PSD graph",
                partial(self._addCacheWidget, i, "PSD", PSDWidget),
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

        self.statusBar: StatusBar = StatusBar(self.SYSTEMS)
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

    def _addCSCPSDWidget(self, index: int) -> None:
        prefix = "CSC PSD " + self.SYSTEMS[index] + ":"
        actuator_id = self.getNextId(prefix)
        aWidget = CSCPSDWidget(
            prefix + str(actuator_id),
            self.toolBar,
            self.comms[index].psd,
            self.caches[index].sensors(),
        )
        self.toolBar.frequencyChanged.connect(aWidget.frequencyChanged)
        self.addDockWidget(Qt.TopDockWidgetArea, aWidget)

    def _addCacheWidget(
        self, index: int, prefix: str, chartTypeClass: CacheWidget
    ) -> None:
        prefix = prefix + " " + self.SYSTEMS[index] + ":"
        actuator_id = self.getNextId(prefix)
        aWidget = chartTypeClass(
            prefix + str(actuator_id),
            self.caches[index],
            self.toolBar,
        )
        self.cacheUpdated.connect(aWidget.cacheUpdated)
        self.toolBar.frequencyChanged.connect(aWidget.frequencyChanged)
        self.toolBar.integralBinningChanged.connect(aWidget.integralBinningChanged)
        self.addDockWidget(Qt.TopDockWidgetArea, aWidget)

    def _addBox(self, index: int) -> None:
        prefix = "Box " + self.SYSTEMS[index] + ":"
        actuator_id = self.getNextId(prefix)
        self.addDockWidget(
            Qt.TopDockWidgetArea,
            BoxChartWidget(prefix + str(actuator_id), self.comms[index], []),
        )

    def _showMiscellaneous(self, index: int) -> None:
        widget = self._miscellaneous[index]
        if widget.isHidden():
            self.addDockWidget(Qt.TopDockWidgetArea, widget)
            widget.show()

    def removeAll(self) -> None:
        for child in self.children():
            if child.objectName()[:3] in ["PSD", "Box", "Vel", "Acc"]:
                self.removeDockWidget(child)
                del child

    def getNextId(self, prefix: str) -> int:
        actuator_id = 1
        for child in self.children():
            if child.objectName().startswith(prefix):
                actuator_id = int(child.objectName()[len(prefix) :]) + 1
        return actuator_id

    @Slot()
    def data(self, data: typing.Any) -> None:
        cache = self.caches[data.salIndex - 1]
        added, chunk_removed = cache.newChunk(data)
        if added:
            self.cacheUpdated.emit(
                data.salIndex - 1,
                len(cache),
                cache.startTime(),
                cache.endTime(),
            )

    @Slot()
    def fpgaState(self, fpgaState: typing.Any) -> None:
        index = fpgaState.salIndex - 1
        self.statusBar.sampleTimes[index] = fpgaState.period
        self.caches[index].setSampleTime(fpgaState.period * u.ms.to(u.s))

    @Slot()
    def intervalChanged(self, interval: int) -> None:
        for i, c in enumerate(self.caches):
            c.setInterval(interval)

    @asyncClose
    async def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings("LSST.TS", "VMSGUI")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        self.toolBar.storeSettings()
        for comm in self.comms:
            await comm.close()
        super().closeEvent(event)


def run() -> None:
    # Create the Qt Application
    app = Application(EUI)
    for index in range(1, 4):
        app.addComm("MTVMS", index=index, manual={"data": {"queue_len": 400}})
    app.run()
