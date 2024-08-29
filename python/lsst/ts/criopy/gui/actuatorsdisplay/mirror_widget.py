# This file is part of Telescope & Site EUI.
#
# Developed for the LSST Telescope and Site Systems.  This product includes
# software developed by the LSST Project (https://www.lsst.org).  See the
# COPYRIGHT file at the top-level directory of this distribution for details of
# code ownership.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QHBoxLayout, QWidget

from .bump_test_scale import BumpTestScale
from .enabled_disabled_scale import EnabledDisabledScale
from .gauge_scale import GaugeScale
from .integer_scale import IntegerScale
from .mirror_view import MirrorView
from .on_off_scale import OnOffScale
from .scales import Scales
from .waiting_scale import WaitingScale
from .warning_scale import WarningScale


class MirrorWidget(QWidget):
    """View of mirror with actuators.

    Attributes
    ----------
    mirrorView : `MirrorView`
        Widget displaying mirror with actuators and gauge showing color scale.
    gauge : `GaugeScale`
        Gauge showing color scale used in actuators.
    """

    def __init__(self) -> None:
        super().__init__()

        self.mirrorView = MirrorView()
        self._bumpTest = BumpTestScale()
        self._enabled_disabled = EnabledDisabledScale()
        self._gauge = GaugeScale()
        self._integer = IntegerScale()
        self._onoff = OnOffScale()
        self._waiting = WaitingScale()
        self._warning = WarningScale()

        layout = QHBoxLayout()
        layout.addWidget(self.mirrorView)
        layout.addWidget(self._gauge)
        layout.addWidget(self._bumpTest)
        layout.addWidget(self._enabled_disabled)
        layout.addWidget(self._onoff)
        layout.addWidget(self._waiting)
        layout.addWidget(self._warning)

        self._curentWidget = self._gauge
        self._bumpTest.hide()
        self._enabled_disabled.hide()
        self._onoff.hide()
        self._waiting.hide()
        self._warning.hide()

        self.setLayout(layout)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.mirrorView.resetTransform()
        self.mirrorView.update_scale()

    def _replace(self, newWidget: QWidget) -> None:
        if self._curentWidget == newWidget:
            return
        self._curentWidget.hide()
        self._curentWidget = newWidget
        self._curentWidget.show()

    def setScaleType(self, scale: Scales) -> None:
        """Sets scale type.

        Parameters
        ----------
        scale : `Scales`
            One of the Scales enum number.
        """
        if scale == Scales.BUMP_TEST:
            self._replace(self._bumpTest)
        elif scale == Scales.ONOFF:
            self._replace(self._onoff)
        elif scale == Scales.WARNING:
            self._replace(self._warning)
        elif scale == Scales.ENABLED_DISABLED:
            self._replace(self._enabled_disabled)
        elif scale == Scales.WAITING:
            self._replace(self._waiting)
        elif scale == Scales.INTEGER:
            self._replace(self._integer)
        else:
            self._replace(self._gauge)

    def setRange(self, min_value: float, max_value: float) -> None:
        """Sets range used for color scaling.

        Parameters
        ----------
        min_value : `float`
           Minimal value.
        max_value : `float`
           Maximal value.
        """
        if self._curentWidget == self._gauge:
            self._gauge.setRange(min_value, max_value)
        self.set_color_scale()

    def set_color_scale(self) -> None:
        self.mirrorView.set_color_scale(self._curentWidget)

    def set_selected(self, actuator_id: int) -> None:
        """Sets current selected force actuators. Emits update signals.

        Parameters
        ----------
        actuator_id : `int`
            Selected actuator ID.
        """
        self.mirrorView.set_selected_id(actuator_id)

    def empty(self) -> bool:
        return len(self.mirrorView.items()) == 0

    def clear(self) -> None:
        self.mirrorView.clear()
