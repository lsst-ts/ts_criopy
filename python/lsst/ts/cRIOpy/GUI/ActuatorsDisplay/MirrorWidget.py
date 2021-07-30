from PySide2.QtWidgets import QWidget, QHBoxLayout

from . import MirrorView, Gauge, OnOff


class MirrorWidget(QWidget):
    """Widget displaying mirror with actuators and gauge showing color scale."""

    mirrorView = None
    """View of mirror with actuators.
    """

    gauge = None
    """Gauge showing color scale used in actuators.
    """

    def __init__(self):
        super().__init__()

        self.mirrorView = MirrorView()
        self.gauge = Gauge()
        self.onoff = OnOff()

        layout = QHBoxLayout()
        layout.addWidget(self.mirrorView)
        layout.addWidget(self.gauge)
        layout.addWidget(self.onoff)

        self._curentWidget = self.gauge
        self.onoff.hide()

        self.setLayout(layout)

    def resizeEvent(self, event):
        self.mirrorView.resetTransform()
        self.mirrorView.scale(*self.mirrorView.scaleHints())

    def _replace(self, newWidget):
        if self._curentWidget == newWidget:
            return
        self._curentWidget.hide()
        self._curentWidget = newWidget
        self._curentWidget.show()

    def setScaleType(self, scale):
        if scale == 1:
            self._replace(self.onoff)
        else:
            self._replace(self.gauge)

    def setRange(self, min, max):
        """Sets range used for color scaling.

        Parameters
        ----------
        min : `float`
           Minimal value.
        max : `float`
           Maximal value.
        """
        self.gauge.setRange(min, max)
        self.mirrorView.setColorScale(self._curentWidget)
