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

import typing

from ...gui.actuatorsdisplay import ForceActuatorItem, MirrorWidget
from ...m1m3_fa_table import FATABLE
from ...salcomm import MetaSAL
from .. import Simulator
from .widget import Widget


class GraphPageWidget(Widget):
    """
    Draw distribution of force actuators, and selected value. Intercept events
    callbacks to trigger updates.
    """

    def __init__(self, m1m3: MetaSAL | Simulator):
        self.mirrorWidget = MirrorWidget()

        for row in FATABLE:
            self.mirrorWidget.mirrorView.addForceActuator(
                row,
                None,
                None,
                ForceActuatorItem.STATE_INACTIVE,
            )

        self.mirrorWidget.mirrorView.selectionChanged.connect(
            self.updateSelectedActuator
        )

        super().__init__(m1m3, self.mirrorWidget)

    def changeValues(self) -> None:
        """Called when data are changed."""
        if self.field is None:
            raise RuntimeError("field is None in GraphPageWidget.changeValues")

        self.mirrorWidget.setScaleType(self.field.scaleType)

    def updateValues(self, data: typing.Any) -> None:
        """Called when new data are available through SAL callback.

        Parameters
        ----------
        data : `object`
            New data structure, passed from SAL handler.
        """
        warningData = self.m1m3.remote.evt_forceActuatorWarning.get()

        if self.field is None:
            raise RuntimeError("field is None in GraphPageWidget.updateValues")

        if data is None:
            values = None
        else:
            values = self.field.getValue(data)

        def get_warning(index: int) -> int:
            return (
                ForceActuatorItem.STATE_WARNING
                if warningData.minorFault[index] or warningData.majorFault[index]
                else ForceActuatorItem.STATE_ACTIVE
            )

        for row in FATABLE:
            index = row.index
            data_index = row.get_index(self.field.valueIndex)
            if values is None or data_index is None:
                state = ForceActuatorItem.STATE_INACTIVE
            elif warningData is not None or data_index is None:
                state = get_warning(index)
            else:
                state = ForceActuatorItem.STATE_ACTIVE

            value = (
                None if (values is None or data_index is None) else values[data_index]
            )

            self.mirrorWidget.mirrorView.updateForceActuator(
                row.actuator_id, value, state
            )

        if values is None:
            self.mirrorWidget.setRange(0, 0)
            return

        self.mirrorWidget.setRange(min(values), max(values))

        selected = self.mirrorWidget.mirrorView.selected()
        if selected is not None:
            if selected.data is not None:
                self.selectedActuatorValueLabel.setText(selected.getValue())
            if warningData is not None:
                self.selectedActuatorWarningLabel.setValue(
                    bool(get_warning(selected.actuator.index))
                )
