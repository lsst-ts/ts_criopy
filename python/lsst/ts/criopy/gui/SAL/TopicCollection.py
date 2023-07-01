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

__all__ = ["TopicCollection"]

from PySide2.QtCore import Slot

from ...salcomm import MetaSAL
from .TopicData import TopicData


class TopicCollection:
    """Collection of topics. Used to store topic belonging to the same
    display.


    Attributes
    ----------
    *topics : `TopicData`
        Display topics. Holds topics and fields available for display.
    """

    def __init__(self, *topics: TopicData) -> None:
        super().__init__()
        self.__last_index: int | None = None

        self.topics = topics

    def change_topic(self, topic_index: int | None, slot: Slot, comm: MetaSAL) -> None:
        if self.__last_index is not None:
            topic = self.topics[self.__last_index].topic
            if topic is not None:
                getattr(comm, topic).disconnect(slot)

        self.__last_index = topic_index
        if topic_index is None:
            return

        topic = self.topics[topic_index].topic
        if topic is not None:
            getattr(comm, topic).connect(slot)
