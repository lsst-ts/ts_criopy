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


from lsst.ts.m1m3.utils import Simulator
from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.tables.m1m3 import FATable

from ...gui.actuatorsdisplay import ForceActuatorItem, MirrorWidget
from ...salcomm import MetaSAL
from .widget import Widget


class GraphPageWidget(Widget):
    """
    Draw distribution of force actuators, and selected value. Intercept events
    callbacks to trigger updates.
    """

    def __init__(self, m1m3: MetaSAL | Simulator):
        self.mirror_widget = MirrorWidget()

        for row in FATable:
            self.mirror_widget.mirror_view.addForceActuator(
                row,
                None,
                None,
                ForceActuatorItem.STATE_INACTIVE,
            )

        self.mirror_widget.mirror_view.selectionChanged.connect(
            self.updateSelectedActuator
        )

        super().__init__(m1m3, self.mirror_widget)

    def change_values(self) -> None:
        """Called when data are changed."""
        if self.field is None:
            raise RuntimeError("field is None in GraphPageWidget.change_values")

        self.mirror_widget.setScaleType(self.field.scale_type)

    def update_values(self, data: BaseMsgType) -> None:
        """Called when new data are available through SAL callback.

        Parameters
        ----------
        data : `object`
            New data structure, passed from SAL handler.
        """
        warning_data = self.m1m3.remote.evt_forceActuatorWarning.get()

        if self.field is None:
            raise RuntimeError("field is None in GraphPageWidget.update_values")

        if data is None:
            values = None
        else:
            values = self.field.getValue(data)

        def get_warning(index: int) -> int:
            return (
                ForceActuatorItem.STATE_WARNING
                if warning_data.minorFault[index] or warning_data.majorFault[index]
                else ForceActuatorItem.STATE_ACTIVE
            )

        enabled = self.m1m3.remote.evt_enabledForceActuators.get()

        for row in FATable:
            index = row.index
            data_index = row.get_index(self.field.value_index)
            if enabled is not None and not enabled.forceActuatorEnabled[index]:
                state = ForceActuatorItem.STATE_INACTIVE
                if values is not None:
                    values[index] = None
            elif values is None or data_index is None:
                state = ForceActuatorItem.STATE_INACTIVE
            elif warning_data is not None or data_index is None:
                state = get_warning(index)
            else:
                state = ForceActuatorItem.STATE_ACTIVE

            value = (
                None if (values is None or data_index is None) else values[data_index]
            )

            self.mirror_widget.mirror_view.update_force_actuator(
                row.actuator_id, value, state
            )

        if values is None:
            self.mirror_widget.setRange(0, 0)
            return

        # filter out None values
        values = [v for v in values if v is not None]
        self.mirror_widget.setRange(min(values), max(values))

        selected = self.mirror_widget.mirror_view.selected()
        if selected is not None:
            if selected.data is not None:
                self.selected_actuator_value_label.setText(selected.getValue())
            if warning_data is not None:
                self.selected_actuator_warning_label.setValue(
                    bool(get_warning(selected.actuator.index))
                )
