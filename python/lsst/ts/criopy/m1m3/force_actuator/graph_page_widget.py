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
from lsst.ts.xml.tables.m1m3 import FATable

from ...gui.actuatorsdisplay import DataItemState, MirrorWidget
from ...salcomm import MetaSAL
from ..simulator import Simulator
from .widget import Widget


class GraphPageWidget(Widget):
    """
    Draw distribution of force actuators, and selected value. Intercept events
    callbacks to trigger updates.
    """

    def __init__(self, m1m3: MetaSAL | Simulator):
        self.mirror_widget = MirrorWidget(support=True)

        super().__init__(m1m3, self.mirror_widget)

        assert self.detail_widget is not None
        self.mirror_widget.mirror_view.selectionChanged.connect(self.detail_widget.update_selected_actuator)

    def change_values(self) -> None:
        """Called when data are changed."""
        assert self.field is not None
        self.mirror_widget.set_scale_type(self.field.scale_type)

    def update_values(self, data: BaseMsgType) -> None:
        """Called when new data are available through SAL callback.

        Parameters
        ----------
        data : `object`
            New data structure, passed from SAL handler.
        """
        warning_data = self.comm.remote.evt_forceActuatorWarning.get()

        if self.field is None:
            raise RuntimeError("field is None in GraphPageWidget.update_values")

        if data is None:
            values = None
        else:
            values = self.field.get_value(data)

        def get_warning(index: int) -> DataItemState:
            return (
                DataItemState.WARNING
                if warning_data.minorFault[index] or warning_data.majorFault[index]
                else DataItemState.ACTIVE
            )

        enabled = self.comm.remote.evt_enabledForceActuators.get()

        for fa in FATable:
            index = fa.index
            data_index = fa.get_index(self.field.value_index)
            if values is None or data_index is None:
                state = DataItemState.INACTIVE
            elif enabled is not None and not enabled.forceActuatorEnabled[index]:
                state = DataItemState.INACTIVE
                values[data_index] = None
            elif warning_data is not None or data_index is None:
                state = get_warning(index)
            else:
                state = DataItemState.ACTIVE

            try:
                value = None if (values is None or data_index is None) else values[data_index]
            except IndexError as err:
                print("Error", data, data_index, values, self.field)
                raise err

            self.mirror_widget.mirror_view.update_force_actuator(fa, value, state)

        if values is None:
            self.mirror_widget.set_range(0, 0)
            return

        # filter out None values
        values = [v for v in values if v is not None and not (np.isnan(v))]
        if len(values) == 0:
            self.mirror_widget.set_range(0, 0)
        else:
            self.mirror_widget.set_range(min(values), max(values))

        if self.detail_widget is None:
            return

        selected = self.mirror_widget.mirror_view.selected()
        if selected is not None:
            if selected.data is not None:
                self.detail_widget.selected_actuator_value_label.setText(selected.get_value())
            if warning_data is not None:
                self.detail_widget.selected_actuator_warning_label.setValue(
                    bool(get_warning(selected.actuator.index))
                )
