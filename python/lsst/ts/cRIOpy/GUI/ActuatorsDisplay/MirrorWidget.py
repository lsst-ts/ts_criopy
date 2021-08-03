from PySide2.QtWidgets import QWidget, QHBoxLayout

from . import (
    MirrorView,
    BumpTestScale,
    GaugeScale,
    OnOffScale,
    EnabledDisabledScale,
    WarningScale,
    Scales,
)


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
        self._bumpTest = BumpTestScale()
        self._enabled_disabled = EnabledDisabledScale()
        self._gauge = GaugeScale()
        self._onoff = OnOffScale()
        self._warning = WarningScale()

        layout = QHBoxLayout()
        layout.addWidget(self.mirrorView)
        layout.addWidget(self._gauge)
        layout.addWidget(self._bumpTest)
        layout.addWidget(self._enabled_disabled)
        layout.addWidget(self._onoff)
        layout.addWidget(self._warning)

        self._curentWidget = self._gauge
        self._bumpTest.hide()
        self._enabled_disabled.hide()
        self._onoff.hide()
        self._warning.hide()

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
        if scale == Scales.Scales.BUMP_TEST:
            self._replace(self._bumpTest)
        elif scale == Scales.Scales.ONOFF:
            self._replace(self._onoff)
        elif scale == Scales.Scales.WARNING:
            self._replace(self._warning)
        elif scale == Scales.Scales.ENABLED_DISABLED:
            self._replace(self._enabled_disabled)
        else:
            self._replace(self._gauge)

    def setRange(self, min, max):
        """Sets range used for color scaling.

        Parameters
        ----------
        min : `float`
           Minimal value.
        max : `float`
           Maximal value.
        """
        if self._curentWidget == self._gauge:
            self._gauge.setRange(min, max)
        self.setColorScale()

    def setColorScale(self):
        self.mirrorView.setColorScale(self._curentWidget)

    def setSelected(self, id):
        self.mirrorView.selected = self.mirrorView.getForceActuator(id)
