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

__all__ = ["BoxChartWidget"]

import typing

from PySide2.QtCharts import QtCharts
from PySide2.QtCore import Qt, Slot

from ..gui import DockWindow
from ..salcomm import MetaSAL
from .chart_view import ChartView
from .time_box_chart import TimeBoxChart


class BoxChartWidget(DockWindow):
    """Display box chart with accelerometer data.

    Parameters
    ----------
    title : `str`
        QDockWidget title and object name.
    comm : `MetaSAL`
        SALComm object providing data.
    channels : `[(sensor, axis)]`
        Enabled channels.
    """

    def __init__(self, title: str, comm: MetaSAL, channels: list[tuple[int, str]]):
        super().__init__(title)
        self.channels = channels
        self.chart = TimeBoxChart()
        self.chartView = ChartView(self.chart, QtCharts.QBoxPlotSeries)
        self.setWidget(self.chartView)

        comm.data.connect(self.data)
        self.chartView.unitChanged.connect(self.chart.unitChanged)

    @Slot()
    def data(self, data: typing.Any) -> None:
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
