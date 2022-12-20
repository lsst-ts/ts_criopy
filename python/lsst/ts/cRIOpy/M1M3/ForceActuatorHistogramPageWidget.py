from PySide2.QtCharts import QtCharts
from PySide2.QtGui import QPainter
from PySide2.QtWidgets import QMenu, QInputDialog

from .ForceActuatorWidget import ForceActuatorWidget
from ..GUI import Histogram


class HistogramView(QtCharts.QChartView):
    def __init__(self):
        self.histogram = Histogram()
        super().__init__(self.histogram)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRubberBand(QtCharts.QChartView.HorizontalRubberBand)

    def update(self, values):
        self.histogram.update(values)

    def setNumberOfBins(self, nbins):
        self.histogram.nbins = nbins

    def contextMenuEvent(self, event):
        contextMenu = QMenu()

        contextMenu.addAction(f"Number of bins: {self.histogram.nbins}")

        action = contextMenu.exec_(event.globalPos())

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


class ForceActuatorHistogramPageWidget(ForceActuatorWidget):
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
        if data is None:
            return

        self.histogramView.update(self.field.getValue(data))
