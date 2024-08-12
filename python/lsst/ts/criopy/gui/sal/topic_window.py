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
    Children classes must implement updateValues(data) method.

    Parameters
    ----------

    comm : `MetaSAL`
        SAL instance to communicate with SAL.
    collection : `TopicCollection`
        Collections of data associated with widget.
    user_widget : `QWidget`
        Widget to be displayed on left from value selection. Its content shall
        be update in updateValues(data) method.
    detail_widget : `QWidget`, optional
        Widget displaying details of selected actuator. If not provided, basic
        selected actuator data will be displayed.

    Methods
    -------

    updateValues(data)
        Must be defined in every child. This is called when selection is
        changed or when new data become available. If data parameter is None,
        then no data has been received for selected read topic.
    """

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

        self.field: TopicField | None = None

        plot_layout = QVBoxLayout()
        selection_layout = QVBoxLayout()
        filterLayout = QHBoxLayout()

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
            self.selectedActuatorIdLabel = QLabel()
            self.selectedActuatorValueLabel = QLabel()
            self.selectedActuatorWarningLabel = WarningLabel()
            self.lastUpdatedLabel = TimeDeltaLabel()

            details_layout = QFormLayout()
            details_layout.addRow(QLabel("Selected Actuator Details"), QLabel(""))
            details_layout.addRow(QLabel("Actuator Id"), self.selectedActuatorIdLabel)
            details_layout.addRow(
                QLabel("Actuator Value"), self.selectedActuatorValueLabel
            )
            details_layout.addRow(
                QLabel("Actuator Warning"), self.selectedActuatorWarningLabel
            )
            details_layout.addRow(QLabel("Last Updated"), self.lastUpdatedLabel)
            selection_layout.addLayout(details_layout)

        selection_layout.addWidget(QLabel("Filter Data"))
        selection_layout.addLayout(filterLayout)

        self.topicList = QListWidget()
        self.topicList.currentRowChanged.connect(self.currentTopicChanged)
        for topic in self.collection.topics:
            self.topicList.addItem(topic.name)
        self.fieldList = QListWidget()
        self.fieldList.currentRowChanged.connect(self.currentFieldChanged)

        plot_layout.addWidget(user_widget)

        filterLayout.addWidget(self.topicList)
        filterLayout.addWidget(self.fieldList)

        self.topicList.setCurrentRow(0)

    @Slot()
    def currentTopicChanged(self, topic_index: int) -> None:
        if topic_index < 0:
            self._setUnknown()
            return

        self.fieldList.clear()
        for field in self.collection.topics[topic_index].fields:
            self.fieldList.addItem(field.name)

        field_index = self.collection.topics[topic_index].selectedField
        if field_index < 0:
            self._setUnknown()
            return

        self.fieldList.setCurrentRow(field_index)
        self._changeField(topic_index, field_index)

    @Slot()
    def currentFieldChanged(self, field_index: int) -> None:
        topic_index = self.topicList.currentRow()
        if topic_index < 0 or field_index < 0:
            self._setUnknown()
            return
        self._changeField(topic_index, field_index)
        self.collection.topics[topic_index].selectedField = field_index

    def _setUnknown(self) -> None:
        self.lastUpdatedLabel.setUnknown()

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
            self.selectedActuatorIdLabel.setText("not selected")
            self.selectedActuatorValueLabel.setText("")
            self.selectedActuatorWarningLabel.setText("")
            return

        self.selectedActuatorIdLabel.setText(str(selected_actuator.actuator_id))
        self.selectedActuatorValueLabel.setText(selected_actuator.getValue())
        self.selectedActuatorWarningLabel.setValue(selected_actuator.warning)

    def _changeField(self, topic_index: int, field_index: int) -> None:
        """
        Redraw actuators with new values.
        """
        topic = self.collection.topics[topic_index]
        self.field = topic.fields[field_index]
        try:
            self.collection.change_topic(topic_index, self.dataChanged, self.comm)

            data = getattr(self.comm.remote, topic.getTopic()).get()
            self.dataChanged(data)
        except RuntimeError as err:
            print("TopicWindow._changeField:", err)
            pass

    def updateValues(self, data: BaseMsgType) -> None:
        raise RuntimeError("Abstract method updateValues")

    @Slot()
    def dataChanged(self, data: BaseMsgType) -> None:
        """
        Called when selected data are updated.

        Parameters
        ----------

        """
        self.updateValues(data)
        if data is None:
            self._setUnknown()
        else:
            try:
                self.lastUpdatedLabel.setTime(data.timestamp)
            except AttributeError:
                self.lastUpdatedLabel.setTime(data.private_sndStamp)
