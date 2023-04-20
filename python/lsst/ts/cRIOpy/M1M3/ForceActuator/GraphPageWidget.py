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

from ...GUI.ActuatorsDisplay import ForceActuator, MirrorWidget
from ...M1M3FATable import (
    FATABLE,
    FATABLE_ID,
    FATABLE_INDEX,
    FATABLE_ORIENTATION,
    FATABLE_XPOSITION,
    FATABLE_YPOSITION,
)
from .Widget import Widget


class GraphPageWidget(Widget):
    """
    Draw distribution of force actuators, and selected value. Intercept events
    callbacks to trigger updates.
    """

    def __init__(self, m1m3):
        self.mirrorWidget = MirrorWidget()
        super().__init__(m1m3, self.mirrorWidget)

        self.mirrorWidget.mirrorView.selectionChanged.connect(
            self.updateSelectedActuator
        )

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
        warningData = self.m1m3.remote.evt_forceActuatorWarning.get()

        if data is None:
            values = None
        else:
            values = self.field.getValue(data)

        if changed:
            self.mirrorWidget.mirrorView.clear()
            self.mirrorWidget.setScaleType(self.field.scaleType)

        def getWarning(index):
            return (
                ForceActuator.STATE_WARNING
                if warningData.minorFault[index] or warningData.majorFault[index]
                else ForceActuator.STATE_ACTIVE
            )

        for row in FATABLE:
            index = row[FATABLE_INDEX]
            dataIndex = row[self.field.valueIndex]
            if values is None or dataIndex is None:
                state = ForceActuator.STATE_INACTIVE
            elif warningData is not None or dataIndex is None:
                state = getWarning(index)
            else:
                state = ForceActuator.STATE_ACTIVE

            id = row[FATABLE_ID]
            value = None if (values is None or dataIndex is None) else values[dataIndex]

            if changed:
                self.mirrorWidget.mirrorView.addForceActuator(
                    id,
                    index,
                    row[FATABLE_XPOSITION] * 1000,
                    row[FATABLE_YPOSITION] * 1000,
                    row[FATABLE_ORIENTATION],
                    value,
                    dataIndex,
                    state,
                )
            else:
                self.mirrorWidget.mirrorView.updateForceActuator(id, value, state)

        if values is None:
            self.mirrorWidget.setRange(0, 0)
            return

        self.mirrorWidget.setRange(min(values), max(values))

        selected = self.mirrorWidget.mirrorView.selected
        if selected is not None:
            if selected.data is not None:
                self.selectedActuatorValueLabel.setText(selected.getValue())
            if warningData is not None:
                self.selectedActuatorWarningLabel.setValue(getWarning(selected.index))
