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
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ...salcomm import MetaSAL
from ..actuatorsdisplay import ForceActuatorItem
from ..custom_labels import WarningLabel
from .time_delta_label import TimeDeltaLabel
from .topic_collection import TopicCollection
from .topic_data import TopicField


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
    detail_widget : `QWidget`, optional
        Widget displaying details of selected actuator. If not provided, basic
        selected actuator data will be displayed.

    Methods
    -------
    update_values(data)
        Must be defined in every child. This is called when selection is
        changed or when new data become available. If data parameter is None,
        then no data has been received for selected read topic.

    Attributes
    ----------
    field : `TopicField | None`
        Selected field. Can be used to access details about the field.
    """

    field: TopicField | None = None

    def __init__(
        self,
        comm: MetaSAL,
        collection: TopicCollection,
        user_widget: QWidget,
        detail_widget: QWidget | None = None,
    ):
        super().__init__()

        self.comm = comm
        self.collection = collection
        self.user_widget = user_widget

        self.field: TopicField | None = None

        plot_layout = QVBoxLayout()
        selection_layout = QVBoxLayout()
        filter_layout = QHBoxLayout()

        w_left = QWidget()
        w_left.setLayout(plot_layout)
        self.addWidget(w_left)
        w_right = QWidget()
        w_right.setLayout(selection_layout)
        self.addWidget(w_right)

        self.setCollapsible(0, False)
        self.setStretchFactor(0, 10)
        self.setStretchFactor(1, 0)

        if detail_widget is not None:
            selection_layout.addWidget(detail_widget)
        else:
            self.selected_actuator_id_label = QLabel()
            self.selected_actuator_value_label = QLabel()
            self.selected_actuator_warning_label = WarningLabel()
            self.last_updated_label = TimeDeltaLabel()

            details_layout = QFormLayout()
            details_layout.addRow(QLabel("Selected Actuator Details"), QLabel(""))
            details_layout.addRow(
                QLabel("Actuator Id"), self.selected_actuator_id_label
            )
            details_layout.addRow(
                QLabel("Actuator Value"), self.selected_actuator_value_label
            )
            details_layout.addRow(
                QLabel("Actuator Warning"), self.selected_actuator_warning_label
            )
            details_layout.addRow(QLabel("Last Updated"), self.last_updated_label)
            selection_layout.addLayout(details_layout)

        selection_layout.addWidget(QLabel("Filter Data"))
        selection_layout.addLayout(filter_layout)

        self.topic_list = QListWidget()
        self.topic_list.currentRowChanged.connect(self.current_topic_changed)
        for topic in self.collection.topics:
            self.topic_list.addItem(topic.name)
        self.field_list = QListWidget()
        self.field_list.currentRowChanged.connect(self.current_field_changed)

        plot_layout.addWidget(self.user_widget)

        filter_layout.addWidget(self.topic_list)
        filter_layout.addWidget(self.field_list)

        self.topic_list.setCurrentRow(0)

    @Slot()
    def current_topic_changed(self, topic_index: int) -> None:
        if topic_index < 0:
            self._set_unknown()
            return

        self.field_list.clear()
        for field in self.collection.topics[topic_index].fields:
            self.field_list.addItem(field.name)

        field_index = self.collection.topics[topic_index].selected_field
        if field_index < 0:
            self._set_unknown()
            return

        self.field_list.setCurrentRow(field_index)
        self._change_field(topic_index, field_index)

    @Slot()
    def current_field_changed(self, field_index: int) -> None:
        topic_index = self.topic_list.currentRow()
        if topic_index < 0 or field_index < 0:
            self._set_unknown()
            return
        self._change_field(topic_index, field_index)
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

    def _set_unknown(self) -> None:
        self.last_updated_label.set_unknown()

    def updateSelectedActuator(self, selected_actuator: ForceActuatorItem) -> None:
        """
        Called from childrens to update currently selected actuator display.

        Parameters
        ----------
        selected_actuator : `ForceActuatorItem`
            Contains actuator ID (selected actuator ID), data (selected
            actuator current value) and warning (boolean, true if value is in
            warning).
        """
        if selected_actuator is None:
            self.selected_actuator_id_label.setText("not selected")
            self.selected_actuator_value_label.setText("")
            self.selected_actuator_warning_label.setText("")
            return

        self.selected_actuator_id_label.setText(str(selected_actuator.actuator_id))
        self.selected_actuator_value_label.setText(selected_actuator.getValue())
        self.selected_actuator_warning_label.setValue(selected_actuator.warning)

    def _change_field(self, topic_index: int, field_index: int) -> None:
        """
        Redraw actuators with new values fields.

        Para
        """
        topic = self.collection.topics[topic_index]
        self.field = topic.fields[field_index]
        try:
            self.collection.change_topic(topic_index, self.data_changed, self.comm)
            self.field_changed(self.field)

            data = getattr(self.comm.remote, topic.getTopic()).get()
            self.data_changed(data)
        except RuntimeError as err:
            print("TopicWindow._change_field:", err)
            pass

    def update_values(self, data: BaseMsgType) -> None:
        raise RuntimeError("Abstract method update_values")

    @Slot()
    def data_changed(self, data: BaseMsgType) -> None:
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
        if data is None:
            self._set_unknown()
        else:
            try:
                self.last_updated_label.setValue(data.timestamp)
            except AttributeError:
                self.last_updated_label.setValue(data.private_sndStamp)
