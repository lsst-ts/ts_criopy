# This file is part of the cRIO GUI.
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

from lsst.ts.salobj import BaseMsgType
from PySide6.QtCore import Slot

from ...salcomm import MetaSAL
from ..actuatorsdisplay import Scales

__all__ = ["TopicData", "TopicField"]


class TopicField:
    """
    Field inside topic. Holds together data needed to properly display values.

    Attributes
    ----------
    name : `str`
        Text displayed in selection list box.
    field_name : `str`
        Name of field inside SAL/DDS topic.
    value_index : `int`
        Variable kind.
    scale_type : `Scales`
        Scale type. Select scale used to display field values.
    fmt :  str (optional)
        Format
    """

    def __init__(
        self,
        name: str,
        field_name: str,
        value_index: int,
        scale_type: Scales = Scales.GAUGE,
        fmt: str | None = None,
    ):
        self.name = name
        self.field_name = field_name
        self.value_index = value_index
        self.scale_type = scale_type
        self.fmt = fmt

    def getValue(self, data: BaseMsgType) -> typing.Any:
        return getattr(data, self.field_name)


class OnOffField(TopicField):
    def __init__(self, name: str, field_name: str, value_index: int):
        super().__init__(name, field_name, value_index, Scales.ONOFF)


class WarningField(TopicField):
    def __init__(self, name: str, field_name: str, value_index: int):
        super().__init__(name, field_name, value_index, Scales.WARNING)


class WaitingField(TopicField):
    def __init__(self, name: str, field_name: str, value_index: int):
        super().__init__(name, field_name, value_index, Scales.WAITING)


class EnabledDisabledField(TopicField):
    def __init__(self, name: str, field_name: str, value_index: int):
        super().__init__(name, field_name, value_index, Scales.ENABLED_DISABLED)


class TopicData:
    """
    Holds topic available for display.

    Attributes
    ----------
    name : `str`
        Name to display in selection list box.
    fields : `[TopicField]`
        Fields available inside topic. Array of TopicField.
    topic : `str`
        Name of the topic. Equals to SAL/DDS topic name for telemetry, needs
        evt_ prefix for events.
    isEvent : `bool`, optional
        True if topic is an event. Data are extracted from remote with evt_
        prefix. Defaults to True
    command : `str`, optional
        If not None (the default value), suffix of commands to clear and apply
        (update) values.
    """

    def __init__(
        self,
        name: str,
        fields: list[TopicField],
        topic: str | None,
        isEvent: bool = True,
        command: str | None = None,
    ):
        self.name = name
        self.fields = fields
        self.selectedField = 0
        self.topic = topic
        self.isEvent = isEvent
        self.command = command

    def getTopic(self) -> str:
        if self.topic is None:
            raise RuntimeError("Called getTopic for topic-less Topic")
        if self.isEvent:
            return "evt_" + self.topic
        return "tel_" + self.topic

    def change_topic(self, index: int, slot: Slot, comm: MetaSAL) -> None:
        """Called when new topic is selected.

        Parameters
        ----------
        index: `int`
            New field index.
        slot: `Slot`
            Slot for data reception.
        comm: `MetaSAL`
            MetaSAL with data.
        """
        raise NotImplementedError("TopicData structure must implement change_topic")
