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

__all__ = ["CacheWidget"]

from ..GUI.TimeChart import AbstractChart
from .ChartView import ChartView
from .Unit import units, coefficients
from ..GUI.CustomLabels import DockWindow

from PySide2.QtCore import Qt, Slot
from PySide2.QtCharts import QtCharts

import concurrent.futures
import time
from lsst.ts.utils import make_done_future


class CacheWidget(DockWindow):
    """Display signal. Child classes shall override cacheUpdated.

    Parameters
    ----------
    title : `str`
        QDockWidget title and object name.
    cache : `VMSCache`
        Data cache.
    toolBar : `ToolBar`
        Provides getFrequencyRange() method.
    channels : `[(sensor, axis)]`
        Enabled channels.
    """

    def __init__(self, title, cache, SAMPLE_TIME, toolBar, channels=[]):
        super().__init__(title)
        self.setObjectName(title)
        self.SAMPLE_TIME = SAMPLE_TIME
        self.toolBar = toolBar

        self.chart = AbstractChart()

        self.updateTask = make_done_future()

        self.update_after = 0

        self.cache = cache

        self.chartView = ChartView(self.chart, QtCharts.QLineSeries)
        self.chartView.updateMaxSensor(self.cache.sensors())
        self.chartView.axisChanged.connect(self.axisChanged)
        self.chartView.unitChanged.connect(self.unitChanged)
        for channel in channels:
            self.chartView.addSerie(str(channel[0]) + " " + channel[1])

        self.coefficient = 1
        self.unit = units[0]
        self.setupAxes = True
        self._setupAxes()

        self.setWidget(self.chartView)

    @Slot(bool, bool)
    def axisChanged(self, logX, logY):
        self.setupAxes = True

    @Slot(str)
    def unitChanged(self, unit):
        self.coefficient = coefficients(unit)
        self.unit = unit
        self.setupAxes = True

    def _setupAxes(self):
        for a in self.chart.axes():
            self.chart.removeAxis(a)

        if len(self.chart.series()) == 0:
            return

        if self.chartView.logX:
            xAxis = QtCharts.QLogValueAxis()
        else:
            xAxis = QtCharts.QValueAxis()

        if self.chartView.logY:
            yAxis = QtCharts.QLogValueAxis()
        else:
            yAxis = QtCharts.QValueAxis()

        xAxis.setTitleText("Frequency (Hz)")
        yAxis.setTitleText("PSD ((" + self.unit + ")<sup>2</sup> Hz <sup>-1</sup>)")

        self.chart.addAxis(xAxis, Qt.AlignBottom)
        self.chart.addAxis(yAxis, Qt.AlignLeft)

        for s in self.chart.series():
            s.attachAxis(xAxis)
            s.attachAxis(yAxis)

        self.chart.axes(Qt.Horizontal)[0].setGridLineVisible(True)
        self.chart.axes(Qt.Horizontal)[0].setMinorGridLineVisible(True)

        self.chart.legend().setAlignment(Qt.AlignTop)

        self.frequencyChanged(*self.toolBar.getFrequencyRange())

        self.setupAxes = False

    def plotAll():
        """Plot all signals. Run as task in a thread. Should be overriden."""
        raise RuntimeError(
            "Abstract CacheWidget.plotAll called - please make sure it is implemented"
        )

    @Slot(int, int, float, float)
    def cacheUpdated(self, index, length, startTime, endTime):
        """Process and plot data.

        Parameters
        ----------
        index : `int`
        length : `int`
        startTime : `float`
        endTime : `float`
        """
        if self.setupAxes is True:
            self._setupAxes()
            self.update_after = 0

        if self.update_after < time.monotonic() and self.updateTask.done():
            with concurrent.futures.ThreadPoolExecutor() as pool:
                self.updateTask = pool.submit(self.plotAll)

    @Slot(float, float)
    def frequencyChanged(self, low, high):
        if len(self.chart.series()) == 0:
            self.setupAxes = True
            return

        self.chart.axes(Qt.Horizontal)[0].setRange(low, high)
