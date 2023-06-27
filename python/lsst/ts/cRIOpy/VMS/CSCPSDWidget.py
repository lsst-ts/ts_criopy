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

__all__ = ["CSCPSDWidget"]

import math
import typing

import numpy as np
from PySide2.QtCharts import QtCharts
from PySide2.QtCore import QPointF, Qt, Slot

from ..GUI import AbstractChart
from ..GUI.CustomLabels import DockWindow
from .Bars import ToolBar
from .ChartView import ChartView
from .Unit import coefficients, units


class CSCPSDWidget(DockWindow):
    """Display CSC calculated PSD (Power Spectral Density).

    Attributes
    ----------
    coefficient : float
        Coefficient for conversion from default unit (m/s^2).

    Parameters
    ----------
    title : `str`
        QDockWidget title and object name.
    toolBar : `ToolBar`
        Provides getFrequencyRange() method.
    psd : `QSignal`
        PSD SAL signal.
    num_sensor : `int`
        Number of sensors.
    channels : `[(channel, axis)]`, optional
        Channels to plot. Defaults to empty array, user should select channels
        from context menu.
    """

    coefficient: float = 1

    def __init__(
        self,
        title: str,
        toolBar: ToolBar,
        psd: typing.Any,
        num_sensor: int,
        channels: list[tuple[int, int]] | None = None,
    ):
        super().__init__(title)
        self.toolBar = toolBar

        self.chart = AbstractChart()

        self.chartView = ChartView(self.chart, QtCharts.QLineSeries)
        self.chartView.updateMaxSensor(num_sensor)
        self.chartView.axisChanged.connect(self.axisChanged)
        self.chartView.unitChanged.connect(self.unitChanged)
        if channels is not None:
            for channel in channels:
                self.chartView.addSerie(f"{channel[0]} {channel[1]}")

        # coefficient for conver
        self.unit = units[0]
        self.callSetupAxes = True
        self.setupAxes()

        self.setWidget(self.chartView)

        psd.connect(self.psd)

    @Slot()
    def axisChanged(self, log_x: bool, log_y: bool) -> None:
        self.callSetupAxes = True

    @Slot()
    def unitChanged(self, unit: str) -> None:
        self.coefficient = coefficients(unit)
        self.unit = unit
        self.callSetupAxes = True

    def setupAxes(self) -> None:
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

    @Slot()
    def frequencyChanged(self, lowFrequency: float, highFrequency: float) -> None:
        if len(self.chart.series()) == 0:
            self.callSetupAxes = True
            return

        self.chart.axes(Qt.Horizontal)[0].setRange(lowFrequency, highFrequency)  # type: ignore

    @Slot()
    def psd(self, psd: typing.Any) -> None:
        if self.callSetupAxes is True:
            self.setupAxes()

        def plot(serie: QtCharts.QLineSeries, psd: typing.Any) -> tuple[float, float]:
            """Plot recieved PSD.

            Parameters
            ----------
            serie : `QLineSeries`
                Line serie.
            psd : `MTVMS_psd`
                Data to plot

            Returns
            -------
            min : `float`
                PSD subplot minimum value.
            max : `float`
                PSD subplot maximum value.
            """
            data = np.array(
                list(
                    filter(
                        lambda x: not math.isnan(x),
                        getattr(psd, "accelerationPSD" + s.name()[2]),
                    )
                )
            )
            if self.coefficient != 1:
                data = (np.sqrt(data) * self.coefficient) ** 2
            frequencies = np.arange(
                psd.minPSDFrequency,
                psd.maxPSDFrequency,
                (psd.maxPSDFrequency - psd.minPSDFrequency) / len(data),
            )
            points = [QPointF(frequencies[r], data[r]) for r in range(len(data))]
            serie.replace(points)

            return min(data), max(data)

        min_psd = []
        max_psd = []
        for s in self.chart.series():
            if int(s.name()[0]) == psd.sensor:
                min_p, max_p = plot(s, psd)
                min_psd.append(min_p)
                max_psd.append(max_p)

        if len(min_psd) > 0:
            if len(self.chart.axes(Qt.Vertical)) == 0:  # type: ignore
                self.callSetupAxes = True
            else:
                self.chart.axes(Qt.Vertical)[0].setRange(min(min_psd), max(max_psd))  # type: ignore
