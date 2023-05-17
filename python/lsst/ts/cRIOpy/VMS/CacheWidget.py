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

import concurrent.futures
import time

from lsst.ts.utils import make_done_future
from PySide2.QtCharts import QtCharts
from PySide2.QtCore import Slot

from ..GUI.CustomLabels import DockWindow
from ..GUI.TimeChart import AbstractChart
from .ChartView import ChartView
from .Unit import coefficients, units


class CacheWidget(DockWindow):
    """Display signal. Child classes shall override plotAll and possibly
    frequencyChanged and integralBinningChanged.

    Parameters
    ----------
    title : `str`
        QDockWidget title and object name.
    cache : `VMS.Cache`
        Data cache.
    toolBar : `ToolBar`
        Provides getFrequencyRange() method.
    channels : `[(sensor, axis)]`
        Enabled channels.
    """

    def __init__(
        self, title, cache, toolBar, channels: list[tuple[int, int]] | None = None
    ):
        super().__init__(title)
        self.setObjectName(title)
        self.toolBar = toolBar

        self.chart = AbstractChart()

        self.updateTask = make_done_future()

        self.update_after = 0

        self.cache = cache

        self.chartView = ChartView(self.chart, QtCharts.QLineSeries)
        self.chartView.updateMaxSensor(self.cache.sensors())
        self.chartView.axisChanged.connect(self.axisChanged)
        self.chartView.unitChanged.connect(self.unitChanged)
        if channels is not None:
            for channel in channels:
                self.chartView.addSerie(f"{channel[0]} {channel[1]}")

        self.coefficient = 1
        self.unit = units[0]
        self.callSetupAxes = True
        self.setupAxes()

        self.setWidget(self.chartView)

    @Slot()
    def axisChanged(self, log_x: bool, log_y: bool) -> None:
        self.callSetupAxes = True

    @Slot()
    def unitChanged(self, unit: str) -> None:
        self.coefficient = coefficients(unit)
        self.unit = unit
        self.callSetupAxes = True

    def setupAxes(self) -> None:
        raise RuntimeError(
            "Abstract CacheWidget.setupAxes called - please make sure the"
            " method is implemented in all child classes"
        )

    def _plotAll(self) -> None:
        try:
            self.plotAll()
        except Exception as ex:
            print(str(ex))

    def plotAll(self) -> None:
        """Plot all signals. Run as task in a thread. Should be overriden."""
        raise RuntimeError(
            "Abstract CacheWidget.plotAll called - please make sure the method"
            " is implemented in all child classes"
        )

    @Slot()
    def cacheUpdated(
        self, index: int, length: int, startTime: float, endTime: float
    ) -> None:
        """Process and plot data. Signaled when new data become available.

        Parameters
        ----------
        index : `int`
            VMS index (1 - M1M3, 2 - M2, 3 - CameraRotator)
        length : `int`
            Number of points in cache.
        startTime : `float`
            Start timestamp.
        endTime : `float`
            End timestamp.
        """
        if self.callSetupAxes is True:
            self.setupAxes()
            self.update_after = 0

        if self.update_after < time.monotonic() and self.updateTask.done():
            with concurrent.futures.ThreadPoolExecutor() as pool:
                self.updateTask = pool.submit(self._plotAll)

    @Slot()
    def frequencyChanged(self, lowFrequency: float, highFrequency: float) -> None:
        pass

    @Slot()
    def integralBinningChanged(self, newBinning: int) -> None:
        pass
