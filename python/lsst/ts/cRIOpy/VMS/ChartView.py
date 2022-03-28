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

__all__ = ["ChartView"]

from ..GUI.TimeChart import TimeChartView
from .Unit import menuUnits, units

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QMenu
from PySide2.QtCharts import QtCharts


class ChartView(TimeChartView):

    axisChanged = Signal(bool, bool)
    unitChanged = Signal(str)

    def __init__(self, title, serieType):
        super().__init__(title)
        self._serieType = serieType
        self._maxSensor = 0
        self.logX = False
        self.logY = False
        self.unit = menuUnits[0]

    def updateMaxSensor(self, maxSensor):
        self._maxSensor = max(self._maxSensor, maxSensor)

    def clear(self):
        self.chart().clearData()

    def addSerie(self, name):
        s = self._serieType()
        s.setName(name)
        self.chart().addSeries(s)
        if (
            len(self.chart().axes(Qt.Horizontal)) > 0
            and len(self.chart().axes(Qt.Vertical)) > 0
        ):
            s.attachAxis(self.chart().axes(Qt.Horizontal)[0])
            s.attachAxis(self.chart().axes(Qt.Vertical)[0])

    def removeSerie(self, name):
        self.chart().remove(name)

    def contextMenuEvent(self, event):
        contextMenu = QMenu()
        zoomOut = contextMenu.addAction("Zoom out")
        clear = contextMenu.addAction("Clear")
        unitMenu = contextMenu.addMenu("Unit")

        def addUnit(unit):
            action = unitMenu.addAction(unit)
            action.setCheckable(True)
            action.setChecked(unit == self.unit)
            return action

        units_actions = [addUnit(menuUnits[i]) for i in range(len(menuUnits))]

        for s in range(1, self._maxSensor + 1):
            for a in ["X", "Y", "Z"]:
                name = f"{s} {a}"
                action = contextMenu.addAction(name)
                action.setCheckable(True)
                action.setChecked(self.chart().findSerie(name) is not None)

        if isinstance(self._serieType, QtCharts.QLineSeries):
            contextMenu.addSeparator()
            logX = contextMenu.addAction("Log X")
            logX.setCheckable(True)
            logX.setChecked(self.logX)

            logY = contextMenu.addAction("Log Y")
            logY.setCheckable(True)
            logY.setChecked(self.logY)

        else:
            logX = None
            logY = None

        action = contextMenu.exec_(event.globalPos())
        # conversions
        if action is None:
            return
        elif action == zoomOut:
            self.chart().zoomReset()
        elif action == clear:
            self.clear()
        elif action in units_actions:
            self.unit = action.text()
            self.unitChanged.emit(units[menuUnits.index(self.unit)])
        elif action == logX:
            self.logX = action.isChecked()
            self.axisChanged.emit(self.logX, self.logY)
        elif action == logY:
            self.logY = action.isChecked()
            self.axisChanged.emit(self.logX, self.logY)
        else:
            name = action.text()
            if action.isChecked():
                self.addSerie(name)
            else:
                self.removeSerie(name)
