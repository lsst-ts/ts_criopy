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

__all__ = ["VelocityWidget"]

from .CacheWidget import CacheWidget

from PySide2.QtCore import Qt, Slot, QPointF, QDateTime
from PySide2.QtCharts import QtCharts

import time
import numpy as np


class VelocityWidget(CacheWidget):
    """Display signal as velocity (first acceleration integral).

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

        xAxis = QtCharts.QDateTimeAxis()
        xAxis.setTickCount(10)
        xAxis.setFormat("mm:ss.zzz")

        if self.chartView.logY:
            yAxis = QtCharts.QLogValueAxis()
        else:
            yAxis = QtCharts.QValueAxis()

        xAxis.setTitleText("Time (s)")
        yAxis.setTitleText("Velocity (" + self.unit + ")")

        self.chart.addAxis(xAxis, Qt.AlignBottom)
        self.chart.addAxis(yAxis, Qt.AlignLeft)

        for s in self.chart.series():
            s.attachAxis(xAxis)
            s.attachAxis(yAxis)

        self.chart.axes(Qt.Horizontal)[0].setGridLineVisible(True)
        self.chart.axes(Qt.Horizontal)[0].setMinorGridLineVisible(True)

        self.chart.legend().setAlignment(Qt.AlignTop)

        self.integralBinningChanged(self.toolBar.getIntegralBinning())

        self.callSetupAxes = False

    def plotAll(self):
        """Plot all signals. Run as task in a thread."""

        min_value = []
        max_value = []
        min_timestamps = []
        max_timestamps = []
        for s in self.chart.series():
            signal = self.cache[s.name()]
            timestamps = [1000 * t for t in self.cache["timestamp"]]

            if len(signal) <= self.integralBinning:
                continue

            velocity = np.trapz(
                np.reshape(
                    signal[: len(signal) - len(signal) % self.integralBinning],
                    (-1, self.integralBinning),
                ),
                axis=1,
            )

            points = [
                QPointF(
                    (
                        timestamps[r * self.integralBinning]
                        + timestamps[(r + 1) * self.integralBinning - 1]
                    )
                    / 2.0,
                    velocity[r],
                )
                for r in range(len(velocity))
            ]
            s.replace(points)

            min_value.append(min(velocity))
            max_value.append(max(velocity))

            min_timestamps.append(timestamps[0])
            max_timestamps.append(timestamps[-1])

        if len(min_value) > 0:
            if len(self.chart.axes(Qt.Vertical)) == 0:
                self.callSetupAxes = True
            else:
                self.chart.axes(Qt.Vertical)[0].setRange(min(min_value), max(max_value))
                self.chart.axes(Qt.Horizontal)[0].setRange(
                    QDateTime.fromMSecsSinceEpoch(min(min_timestamps)),
                    QDateTime.fromMSecsSinceEpoch(max(max_timestamps)),
                )
        self.update_after = time.monotonic() + 0.5

    @Slot(int)
    def integralBinningChanged(self, newIntegralBinning):
        self.integralBinning = newIntegralBinning
