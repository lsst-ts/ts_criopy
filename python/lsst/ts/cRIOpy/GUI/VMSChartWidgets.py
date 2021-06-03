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
#
# You should have received a copy of the GNU General Public License along with
# this program.If not, see <https://www.gnu.org/licenses/>.

__all__ = ["BoxChartWidget", "PSDWidget"]

from .TimeChart import TimeChartView, AbstractChart
from .TimeBoxChart import TimeBoxChart
from .VMSUnit import menuUnits, units, coefficients
from .CustomLabels import DockWindow

from PySide2.QtCore import Qt, Slot, Signal, QPointF
from PySide2.QtWidgets import QMenu
from PySide2.QtCharts import QtCharts

import concurrent.futures
import numpy as np
import time
from lsst.ts.salobj import make_done_future


class VMSChartView(TimeChartView):

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


class BoxChartWidget(DockWindow):
    """Display box chart with accelerometer data.

    Parameters
    ----------
    title : `str`
        QDockWidget title and object name.
    comm : `SALComm`
        SALComm object providing data.
    channels : `[(sensor, axis)]`
        Enabled channels.
    """

    def __init__(self, title, comm, channels):
        super().__init__(title)
        self.channels = channels
        self.chart = TimeBoxChart()
        self.chartView = VMSChartView(self.chart, QtCharts.QBoxPlotSeries)
        self.setWidget(self.chartView)

        comm.data.connect(self.data)
        self.chartView.unitChanged.connect(self.chart.unitChanged)

    @Slot(map)
    def data(self, data):
        self.chartView.updateMaxSensor(data.sensor)
        for axis in ["X", "Y", "Z"]:
            name = f"{str(data.sensor)} {axis}"
            serie = self.chart.findSerie(name)
            if serie is not None:
                self.chart.append(
                    serie,
                    data.timestamp,
                    getattr(data, f"acceleration{axis}"),
                )
                self.chart.axes(Qt.Vertical)[0].setTitleText(
                    "Acceleration (" + self.chart.unit + ")"
                )


class PSDWidget(DockWindow):
    """Display signal PSD.

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

        self.chartView = VMSChartView(self.chart, QtCharts.QLineSeries)
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

        def downsample(psd, N):
            """Downsample PSD so no too many points are plot. Replace PSD with
            max of subarray and frequency with mean frequency.
            Parameters
            ----------
            psd : `[float]`
                Original, full scale PSD. len(psd) ~= N // 2
            N : `int`
                Size of original signal.
            """
            fMin = self.chart.axes(Qt.Horizontal)[0].min()
            fMax = self.chart.axes(Qt.Horizontal)[0].max()

            frequencies = np.fft.rfftfreq(N, self.SAMPLE_TIME)

            f = iter(frequencies)
            rMin = 0
            try:
                while next(f) < fMin:
                    rMin += 1
                rMax = rMin
                try:
                    while next(f) < fMax:
                        rMax += 1
                except StopIteration:
                    pass
                rMin = max(0, rMin - 2)
                rMax = min(len(frequencies) - 1, rMax + 2)
            except StopIteration:
                return (psd[-2:-1], frequencies[-2:-1])

            psd = psd[rMin:rMax]
            frequencies = frequencies[rMin:rMax]
            dataPerPixel = len(psd) / self.chart.plotArea().width()
            # downsample if points are less than 2 pixels apart, so the points
            # are at least 2 pixels apart
            if dataPerPixel > 0.5:
                s = int(np.floor(dataPerPixel * 2.0))
                N = len(psd)
                psd = [max(psd[i : i + s]) for i in range(0, N, s)]
                # frequencies are monotonic constant step. So to calculate
                # average, only took boundary members and divide by two
                frequencies = [
                    (frequencies[i] + frequencies[min(i + s, N - 1)]) / 2
                    for i in range(0, N, s)
                ]
            return (psd, frequencies)

        def plot(serie, signal):
            """Calculates and plot PSD - Power Spectral Density. Downsamples
            the calculated PSD so reasonable number of points is displayed.

            Parameters
            ----------
            serie : `QLineSeries`
                Line serie.
            signal : `[float]`
                Input signal.

            Returns
            -------
            min : `float`
                PSD subplot minimum value.
            max : `float`
                PSD subplot maximum value.
            """
            N = len(signal)
            if N < 10:
                return 0, 0
            # as input is real only, fft is symmetric; rfft is enough
            psd = np.abs(np.fft.rfft(np.array(signal) * self.coefficient)) ** 2

            (psd, frequencies) = downsample(psd, N)

            points = [QPointF(frequencies[r], psd[r]) for r in range(len(psd))]
            serie.replace(points)

            return min(psd), max(psd)

        def plotAll():
            """Plot all signals. Run as task in thread."""
            #   min_psd, max_psd = plot(
            #   0,
            #   np.mean(
            #      [self.cache[s + self.samples[0]] for s in ["1", "2", "3"]],
            #      axis=0,
            #   ),
            #   )
            #   self.chart.axes(Qt.Vertical)[0].setRange(min_psd, max_psd)
            min_psd = []
            max_psd = []
            for s in self.chart.series():
                min_p, max_p = plot(s, self.cache[s.name()])
                min_psd.append(min_p)
                max_psd.append(max_p)

            if len(min_psd) > 0:
                if len(self.chart.axes(Qt.Vertical)) == 0:
                    self.setupAxes = True
                else:
                    self.chart.axes(Qt.Vertical)[0].setRange(min(min_psd), max(max_psd))
            self.update_after = time.monotonic() + 0.5

        if self.setupAxes is True:
            self._setupAxes()
            self.update_after = 0

        if self.update_after < time.monotonic() and self.updateTask.done():
            with concurrent.futures.ThreadPoolExecutor() as pool:
                self.updateTask = pool.submit(plotAll)

    @Slot(float, float)
    def frequencyChanged(self, low, high):
        if len(self.chart.series()) == 0:
            self.setupAxes = True
            return

        self.chart.axes(Qt.Horizontal)[0].setRange(low, high)
