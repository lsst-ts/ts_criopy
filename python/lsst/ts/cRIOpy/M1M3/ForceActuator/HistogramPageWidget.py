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

from PySide2.QtCharts import QtCharts
from PySide2.QtCore import QSettings
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QInputDialog, QMenu

from ...GUI import Histogram
from .Widget import Widget


class HistogramView(QtCharts.QChartView):
    def __init__(self):
        self.histogram = Histogram()
        super().__init__(self.histogram)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRubberBand(QtCharts.QChartView.HorizontalRubberBand)

        self.config = None

    def update(self, values):
        self.histogram.update(values)

    def setName(self, names: (str, str)):
        self.config = "/".join(names)
        settings = QSettings("LSST.TS", "M1M3GUI")
        self.setNumberOfBins(int(settings.value(self.config + "/nbins", 50)))

    def setNumberOfBins(self, nbins: int) -> None:
        self.histogram.nbins = nbins
        if self.config is not None:
            settings = QSettings("LSST.TS", "M1M3GUI")
            settings.setValue(self.config + "/nbins", nbins)

    def contextMenuEvent(self, event):
        contextMenu = QMenu()

        contextMenu.addAction(f"Number of bins: {self.histogram.nbins}")

        action = contextMenu.exec_(event.globalPos())
        if action is None:
            return

        if action.text().startswith("Number of bins:"):
            nbins, ok = QInputDialog.getInt(
                self,
                "Number of bins",
                "Number of bins",
                self.histogram.nbins,
                0,
                200,
            )
            if ok:
                self.setNumberOfBins(nbins)


class HistogramPageWidget(Widget):
    """
    Plot histogram of force actuators values.
    """

    def __init__(self, m1m3):
        self.histogramView = HistogramView()
        super().__init__(m1m3, self.histogramView)

    def updateValues(self, data, changed):
        """Called when new data are available through SAL callback.

        Parameters
        ----------
        data : `object`
            New data structure, passed from SAL handler.
        changed : `bool`
            True when data shall be added as a new value selection. Mirror View
            is cleared when true, and new FA items are created.
        """
        if changed:
            self.histogramView.setName(self.getCurrentFieldName())

        if data is None:
            return

        self.histogramView.update(self.field.getValue(data))