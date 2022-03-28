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

__all__ = ["PSDWidget"]

from .CacheWidget import CacheWidget

from PySide2.QtCore import Qt, Slot, QPointF
from PySide2.QtCharts import QtCharts

import numpy as np
import time


class PSDWidget(CacheWidget):
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
        super().__init__(title, cache, SAMPLE_TIME, toolBar, channels)

    def setupAxes(self):
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

        self.callSetupAxes = False

    def plotAll(self):
        """Plot all signals. Run as task in a thread."""

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

        min_psd = []
        max_psd = []
        for s in self.chart.series():
            min_p, max_p = plot(s, self.cache[s.name()])
            min_psd.append(min_p)
            max_psd.append(max_p)

        if len(min_psd) > 0:
            if len(self.chart.axes(Qt.Vertical)) == 0:
                self.callSetupAxes = True
            else:
                self.chart.axes(Qt.Vertical)[0].setRange(min(min_psd), max(max_psd))
        self.update_after = time.monotonic() + 0.5

    @Slot(float, float)
    def frequencyChanged(self, lowFrequency, highFrequency):
        if len(self.chart.series()) == 0:
            self.callSetupAxes = True
            return

        self.chart.axes(Qt.Horizontal)[0].setRange(lowFrequency, highFrequency)
