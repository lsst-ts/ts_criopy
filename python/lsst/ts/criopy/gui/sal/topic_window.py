# This file is part of M1M3 SS GUI.
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
# along with this program. If not, see <https://www.gnu.org/licenses/>.


from lsst.ts.salobj import BaseMsgType
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QListWidget,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ...salcomm import MetaSAL
from .topic_collection import TopicCollection
from .topic_data import TopicData, TopicField
from .topic_detail_widget import TopicDetailWidget


class TopicWindow(QSplitter):
    """
    Abstract class for widget and graphics display of selected M1M3 values.
    Children classes must implement update_values(data) method.

    Parameters
    ----------
    comm : `MetaSAL`
        SAL instance to communicate with SAL.
    collection : `TopicCollection`
        Collections of data associated with widget.
    user_widget : `QWidget`
        Widget to be displayed on left from value selection. Its content shall
        be update in update_values(data) method.
    detail_widget : `TopicDetailWidget`, optional
        Widget displaying details of selected actuator.

    Methods
    -------
    update_values(data)
        Must be defined in every child. This is called when selection is
        changed or when new data become available. If data parameter is None,
        then no data has been received for selected read topic.

    Attributes
    ----------
    topic : `TopicData | None`
        Selected Topic.
    field : `TopicField | None`
        Selected field. Can be used to access details about the field.
    """

    topic: TopicData | None = None
    field: TopicField | None = None

    def __init__(
        self,
        comm: MetaSAL,
        collection: TopicCollection,
        user_widget: QWidget,
        detail_widget: TopicDetailWidget | None = None,
    ):
        super().__init__()

        self.comm = comm
        self.collection = collection
        self.user_widget = user_widget

        plot_layout = QVBoxLayout()
        selection_layout = QVBoxLayout()
        filter_layout = QGridLayout()

        w_left = QWidget()
        w_left.setLayout(plot_layout)
        self.addWidget(w_left)
        w_right = QWidget()
        w_right.setLayout(selection_layout)
        w_right.setMaximumWidth(w_right.size().width())
        self.addWidget(w_right)

        self.setCollapsible(0, False)
        self.setStretchFactor(0, 10)
        self.setStretchFactor(1, 0)

        self.detail_widget = detail_widget

        if self.detail_widget is not None:
            selection_layout.addWidget(self.detail_widget)

        selection_layout.addWidget(QLabel("Filter Data"))
        selection_layout.addLayout(filter_layout)

        self.topic_list = QListWidget()
        self.topic_list.currentRowChanged.connect(self.current_topic_changed)
        for topic in self.collection.topics:
            self.topic_list.addItem(topic.name)
        self.field_list = QListWidget()
        self.field_list.currentRowChanged.connect(self.current_field_changed)

        plot_layout.addWidget(self.user_widget)

        filter_layout.addWidget(QLabel("Topic"), 1, 1)
        filter_layout.addWidget(QLabel("Field"), 1, 2)
        filter_layout.addWidget(self.topic_list, 2, 1)
        filter_layout.addWidget(self.field_list, 2, 2)

        self.topic_list.setCurrentRow(0)

    @Slot()
    def current_topic_changed(self, topic_index: int) -> None:
        if topic_index < 0:
            self.no_data()
            return

        self.field_list.clear()
        for field in self.collection.topics[topic_index].fields:
            self.field_list.addItem(field.name)

        field_index = self.collection.topics[topic_index].selected_field
        if field_index < 0:
            self.no_data()
            return

        self.field_list.setCurrentRow(field_index)
        self.change_field(topic_index, field_index)

    @Slot()
    def current_field_changed(self, field_index: int) -> None:
        topic_index = self.topic_list.currentRow()
        if topic_index < 0 or field_index < 0:
            self.no_data()
            return
        self.change_field(topic_index, field_index)
        self.collection.topics[topic_index].selected_field = field_index

    def field_changed(self, field: TopicField) -> None:
        """
        May be overwritten in child classes to setup scaling etc.

        Parameters
        ----------
        field : `TopicField`
            New topic.
        """
        pass

    def no_data(self) -> None:
        if self.detail_widget is not None:
            self.detail_widget.data_changed(None)

    def get_current_field_name(self) -> tuple[str, str]:
        if self.topic is None or self.field is None:
            raise RuntimeError(
                "Topic or field is None in get_current_field_name:"
                f" {self.topic}, {self.field}"
            )
        assert self.topic.topic is not None
        assert self.field.field_name is not None
        return (self.topic.topic, self.field.field_name)

    def change_field(self, topic_index: int, field_index: int) -> BaseMsgType | None:
        """
        Redraw actuators with new values fields.

        Parameters
        ----------
        topic_index : `int`
        field_index : `int`
        """
        self.topic = self.collection.topics[topic_index]
        self.field = self.topic.fields[field_index]
        try:
            self.collection.change_topic(topic_index, self.data_changed, self.comm)
            self.field_changed(self.field)

            data = getattr(self.comm.remote, self.topic.getTopic()).get()
            self.data_changed(data)
            return data

        except RuntimeError as err:
            print("TopicWindow.change_field:", err)
            return None

    def update_values(self, data: BaseMsgType) -> None:
        """
        Called when new data are available through SAL callback. Needs to be
        overwritten in all childs.

        Parameters
        ----------
        data : `BaseMsgType | None`
            New data structure, passed from SAL handler.
        """
        raise NotImplementedError("Abstract method update_values called.")

    @Slot()
    def data_changed(self, data: BaseMsgType | None) -> None:
        """
        Called when selected data are updated.

        Parameters
        ----------
        data : `BaseMsgType`
            New values, retrieved from SAL.
        """
        if self.field is None:
            raise RuntimeError("update_values was called with empty field.")

        self.update_values(data)
        if self.detail_widget is not None:
            self.detail_widget.data_changed(data)
