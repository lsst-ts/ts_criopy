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


import numpy as np
from lsst.ts.salobj import BaseMsgType
from PySide6.QtCharts import QChartView
from PySide6.QtCore import QPointF, QSettings, Qt
from PySide6.QtGui import QContextMenuEvent, QFont, QPainter
from PySide6.QtWidgets import QGraphicsTextItem, QInputDialog, QMenu

from ...gui import Histogram
from ...salcomm import MetaSAL
from .widget import Widget


class HistogramView(QChartView):
    def __init__(self) -> None:
        self.histogram = Histogram()
        super().__init__(self.histogram)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRubberBand(QChartView.HorizontalRubberBand)

        self.config: str | None = None

    def update(self, values: list[float]) -> None:
        values = [v for v in values if np.isfinite(v)]
        if len(values) > 0:
            self.histogram.plot(values)
        else:
            scene = self.scene()
            text = QGraphicsTextItem("No valid values!")
            text.setDefaultTextColor(Qt.red)
            text.setFont(QFont("Helvetica", min(self.width(), self.height()) / 20.0))
            text.setPos(QPointF(self.rect().center()) - text.boundingRect().center())
            scene.addItem(text)

            self.chart().hide()
            self.show()

    def setName(self, names: tuple[str, str]) -> None:
        self.config = "/".join(names)
        settings = QSettings("LSST.TS", "M1M3GUI")
        self.setNumberOfBins(int(settings.value(self.config + "/nbins", 50)))

    def setNumberOfBins(self, nbins: int) -> None:
        self.histogram.nbins = nbins
        if self.config is not None:
            settings = QSettings("LSST.TS", "M1M3GUI")
            settings.setValue(self.config + "/nbins", nbins)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
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

    def __init__(self, m1m3: MetaSAL):
        self.histogramView = HistogramView()
        super().__init__(m1m3, self.histogramView)

    def change_values(self) -> None:
        (topic, field) = self.get_current_field_name()
        if topic is None or field is None:
            return
        self.histogramView.setName((topic, field))

    def update_values(self, data: BaseMsgType) -> None:
        """Called when new data are available through SAL callback.

        Parameters
        ----------
        data : `object`
            New data structure, passed from SAL handler.
        """
        if data is None or self.field is None:
            return

        self.histogramView.update(self.field.get_value(data))
