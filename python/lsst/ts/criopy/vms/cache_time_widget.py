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

__all__ = ["CacheTimeWidget"]

import time

from PySide2.QtCharts import QtCharts
from PySide2.QtCore import QDateTime, QPointF, Qt, Slot

from .bars import ToolBar
from .cache import Cache
from .cache_widget import CacheWidget


class CacheTimeWidget(CacheWidget):
    """Display time data comming from cache.

    Parameters
    ----------
    title : `str`
        QDockWidget title and object name.
    cache : `Cache`
        Data cache.
    toolBar : `ToolBar`
        Provides getFrequencyRange() method.
    channels : `[(sensor, axis)]`, optional
        Enabled channels.
    """

    def __init__(
        self,
        title: str,
        cache: Cache,
        toolBar: ToolBar,
        channels: list[tuple[int, int]] | None = None,
    ):
        super().__init__(title, cache, toolBar, channels)

    def setupAxes(self) -> None:
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

    def calculateValues(
        self, timestamps: list[float], signal: list[float]
    ) -> tuple[list[float] | None, list[float] | None]:
        raise NotImplementedError(
            "Abstract CacheTimeWidget.calculateValues called - please make sure"
            " all child classes implements getPoints method."
        )

    def plotAll(self) -> None:
        """Plot all signals. Run as task in a thread."""

        min_value = []
        max_value = []
        min_timestamps = []
        max_timestamps = []
        for s in self.chart.series():
            signal = self.cache[s.name()]
            timestamps = [1000 * t for t in self.cache["timestamp"]]

            (result_times, values) = self.calculateValues(timestamps, signal)
            if result_times is None or values is None:
                continue

            s.replace([QPointF(result_times[r], values[r]) for r in range(len(values))])

            min_value.append(min(values))
            max_value.append(max(values))

            min_timestamps.append(result_times[0])
            max_timestamps.append(result_times[-1])

        if len(min_value) > 0:
            if len(self.chart.axes(Qt.Vertical)) == 0:
                self.callSetupAxes = True
            else:
                self.chart.axes(Qt.Vertical)[0].setRange(min(min_value), max(max_value))
                self.chart.axes(Qt.Horizontal)[0].setRange(
                    QDateTime.fromMSecsSinceEpoch(int(min(min_timestamps))),
                    QDateTime.fromMSecsSinceEpoch(int(max(max_timestamps))),
                )
        self.update_after = time.monotonic() + 0.5

    @Slot()
    def integralBinningChanged(self, newIntegralBinning: int) -> None:
        self.integralBinning = newIntegralBinning
