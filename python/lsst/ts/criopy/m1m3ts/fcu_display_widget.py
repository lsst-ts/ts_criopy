# This file is part of M1M3 TS GUI.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["FCUDisplayWidget"]

import math

from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.tables.m1m3 import FCUTable

from ..gui.actuatorsdisplay import DataItemState, MirrorWidget
from ..gui.sal import TopicField, TopicWindow
from ..salcomm import MetaSAL
from .thermal_data import Thermals


class FCUDisplayWidget(TopicWindow):
    def __init__(self, m1m3ts: MetaSAL):
        self.mirror_widget = MirrorWidget(thermal=True)

        super().__init__(m1m3ts, Thermals(), self.mirror_widget)

    def field_changed(self, field: TopicField) -> None:
        """Called when data are changed."""
        if field is not None:
            self.mirror_widget.set_scale_type(field.scale_type)

    def update_values(self, data: BaseMsgType) -> None:
        if data is None:
            values = None
        else:
            assert self.field is not None
            values = self.field.getValue(data)

        enabled = self.comm.remote.evt_enabledILC.get()

        for fcu in FCUTable:
            value = math.nan if values is None else float(values[fcu.index])
            state = (
                DataItemState.INACTIVE
                if enabled is None or enabled.enabled[fcu.index] is False
                else DataItemState.ACTIVE
            )
            self.mirror_widget.mirror_view.update_fcu(fcu, value, state)

        if values is None:
            self.mirror_widget.set_range(0, 0)
            return

        values = [v for v in values if v is not None]
        self.mirror_widget.set_range(min(values), max(values))
