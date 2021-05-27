from PySide2.QtWidgets import QWidget, QHBoxLayout

from . import MirrorView, Gauge


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

        layout = QHBoxLayout()
        layout.addWidget(self.mirrorView)
        layout.addWidget(self.gauge)

        self.setLayout(layout)

    def resizeEvent(self, event):
        self.mirrorView.resetTransform()
        self.mirrorView.scale(*self.mirrorView.scaleHints())

    def setRange(self, min, max):
        """Sets range used for color scaling.

        Parameters
        ----------
        min : `float`
           Minimal value.
        max : `float`
           Maximal value.
        """
        self.mirrorView.setRange(min, max)
        self.gauge.setRange(min, max)
