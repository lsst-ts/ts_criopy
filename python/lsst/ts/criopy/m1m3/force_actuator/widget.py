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

import typing

import numpy
from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.tables.m1m3 import FAIndex, FATable
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ...gui import WarningLabel
from ...gui.actuatorsdisplay import ForceActuatorItem
from ...gui.sal import TimeDeltaLabel, TopicData
from ...salcomm import MetaSAL, command
from .topics import Topics
from .update_window import UpdateWindow


class Widget(QSplitter):
    """
    Abstract class for widget and graphics display of selected M1M3 values.
    Children classes must implement change_values and update_values(data)
    methods.

    Parameters
    ----------

    m1m3 : `SALComm`
        SALComm instance to communicate with SAL.
    userWidget : `QWidget`
        Widget to be displayed on left from value selection. Its content shall
        be update in update_values(data) method.
    """

    def __init__(self, m1m3: MetaSAL, userWidget: QWidget):
        super().__init__()
        self.m1m3 = m1m3

        self.updateWindows: dict[str, QWidget] = {}

        self.field: typing.Any | None = None
        self._topic: TopicData | None = None

        plot_layout = QVBoxLayout()
        selection_layout = QVBoxLayout()
        details_layout = QGridLayout()
        filter_layout = QGridLayout()

        selection_layout.addLayout(details_layout)
        selection_layout.addLayout(filter_layout)

        self.selected_actuator_id_label = QLabel()
        self.selected_actuator_value_label = QLabel()
        self.selected_actuator_warning_label = WarningLabel()
        self.last_updated_label = TimeDeltaLabel()

        self.near_selected_ids_label = QLabel()
        self.near_selected_value_label = QLabel()

        self.far_selected_ids_label = QLabel()
        self.far_selected_value_label = QLabel()

        self.topic_list = QListWidget()
        self.topic_list.setFixedWidth(256)
        self.topic_list.currentRowChanged.connect(self.currentTopicChanged)
        self.topics = Topics()
        for topic in self.topics.topics:
            self.topic_list.addItem(topic.name)
        self.fieldList = QListWidget()
        self.fieldList.setFixedWidth(256)
        self.fieldList.currentRowChanged.connect(self.currentFieldChanged)

        plot_layout.addWidget(userWidget)

        def addDetails(
            row: int, name: str, label: QLabel, nears: QLabel, fars: QLabel
        ) -> None:
            details_layout.addWidget(QLabel(name), row, 0)
            details_layout.addWidget(label, row, 1)
            details_layout.addWidget(nears, row, 2)
            details_layout.addWidget(fars, row, 3)

        addDetails(
            0,
            "<b>Variable</b>",
            QLabel("<b>Selected</b>"),
            QLabel("<b>Near Neighbors</b>"),
            QLabel("<b>Far Neighbors</b>"),
        )
        addDetails(
            1,
            "<b>Id</b>",
            self.selected_actuator_id_label,
            self.near_selected_ids_label,
            self.far_selected_ids_label,
        )
        addDetails(
            2,
            "<b>Value</b>",
            self.selected_actuator_value_label,
            self.near_selected_value_label,
            self.far_selected_value_label,
        )
        addDetails(
            3,
            "<b>Last Updated</b>",
            self.last_updated_label,
            QLabel("<b>Warning</b>"),
            self.selected_actuator_warning_label,
        )

        self.forces_moments = [
            QLabel("---"),
            QLabel("---"),
            QLabel("---"),
            QLabel("---"),
            QLabel("---"),
            QLabel("---"),
            QLabel("---"),
        ]

        details_layout.addWidget(QLabel("<b>Forces</b>"), 4, 0)
        details_layout.addWidget(self.forces_moments[6], 5, 0)
        for i, a in enumerate("XYZ"):
            details_layout.addWidget(QLabel(f"<b>{a}</b>"), 4, i + 1)
            details_layout.addWidget(self.forces_moments[i], 5, i + 1)

        details_layout.addWidget(QLabel("<b>Moments</b>"), 6, 0)
        for i, a in enumerate("XYZ"):
            details_layout.addWidget(QLabel(f"<b>{a}</b>"), 6, i + 1)
            details_layout.addWidget(self.forces_moments[i + 3], 7, i + 1)

        self.editButton = QPushButton("&Modify")
        self.editButton.clicked.connect(self.editValues)
        self.clearButton = QPushButton("&Zero")
        self.clearButton.clicked.connect(self.zeroValues)

        details_layout.addWidget(self.editButton, 8, 0, 1, 2)
        details_layout.addWidget(self.clearButton, 8, 2, 1, 2)

        filter_layout.addWidget(QLabel("Topic"), 1, 1)
        filter_layout.addWidget(QLabel("Field"), 1, 2)
        filter_layout.addWidget(self.topic_list, 2, 1)
        filter_layout.addWidget(self.fieldList, 2, 2)

        self.topic_list.setCurrentRow(0)

        w_left = QWidget()
        w_left.setLayout(plot_layout)
        w_right = QWidget()
        w_right.setLayout(selection_layout)
        w_right.setMaximumWidth(w_right.size().width())
        self.addWidget(w_left)
        self.addWidget(w_right)

        self.setCollapsible(0, False)
        self.setStretchFactor(0, 10)
        self.setStretchFactor(1, 1)

    def change_values(self) -> None:
        """Called when new values were selected by the user."""
        raise NotImplementedError(
            "change_values method must be implemented in all Widget childrens"
        )

    def update_values(self, data: BaseMsgType) -> None:
        """Called when new data are available through SAL callback.

        Parameters
        ----------
        data : `object`
            New data structure, passed from SAL handler.
        """
        raise NotImplementedError(
            "update_values method must be implemented in all Widget childrens"
        )

    @Slot()
    def currentTopicChanged(self, topic_index: int) -> None:
        if topic_index < 0:
            self._set_unknown()
            return

        self.fieldList.clear()
        for field in self.topics.topics[topic_index].fields:
            self.fieldList.addItem(field.name)

        field_index = self.topics.topics[topic_index].selected_field
        if field_index < 0:
            self._set_unknown()
            return

        self.fieldList.setCurrentRow(field_index)
        self.__change_field(topic_index, field_index)

    @Slot()
    def currentFieldChanged(self, field_index: int) -> None:
        topic_index = self.topic_list.currentRow()
        if topic_index < 0 or field_index < 0:
            self._set_unknown()
            return
        self.__change_field(topic_index, field_index)
        self.topics.topics[topic_index].selected_field = field_index

    @Slot()
    def editValues(self) -> None:
        def get_axis(topic: TopicData) -> str:
            axis = ""
            for f in topic.fields:
                if f.value_index == FAIndex.X:
                    axis += "x"
                elif f.value_index == FAIndex.Y:
                    axis += "y"
                elif f.value_index == FAIndex.Z:
                    axis += "z"
            return "".join(sorted(set(axis)))

        if self._topic is None or self._topic.command is None:
            return

        suffix = self._topic.command
        try:
            self.updateWindows[suffix].show()
        except KeyError:
            w = UpdateWindow(self.m1m3, suffix, get_axis(self._topic))
            w.show()
            self.updateWindows[suffix] = w

    @asyncSlot()
    async def zeroValues(self) -> None:
        if self.field is None or self._topic is None or self._topic.command is None:
            return
        await command(
            self, getattr(self.m1m3.remote, "cmd_clear" + self._topic.command)
        )

    def _set_unknown(self) -> None:
        self.last_updated_label.set_unknown()

    def getCurrentFieldName(self) -> tuple[str, str]:
        if self._topic is None or self._topic.topic is None or self.field is None:
            raise RuntimeError(
                "Topic or field is None in Widget.getCurrentFieldName:"
                f" {self._topic}, {self.field}"
            )
        return (self._topic.topic, self.field.field_name)

    def _get_data(self) -> typing.Any:
        if self._topic is None:
            raise RuntimeError("Topic is None in Widget._get_data")
        topic = self._topic.getTopic()
        if isinstance(topic, str):
            return getattr(self.m1m3.remote, topic).get()
        return topic

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

        if self.field is None:
            raise RuntimeError("field not selected in Widget.updateSelectedActuator")

        self.selected_actuator_id_label.setText(
            str(selected_actuator.actuator.actuator_id)
        )
        self.selected_actuator_value_label.setText(selected_actuator.getValue())
        self.selected_actuator_warning_label.setValue(selected_actuator.warning)

        data = self.field.getValue(self._get_data())

        # near neighbour
        near_ids = FATable[selected_actuator.actuator.index].near_neighbors
        near_indices = list(
            selected_actuator.actuator.near_neighbors_indices(self.field.value_index)
        )

        if len(near_indices) == 0:
            self.near_selected_ids_label.setText("---")
            self.near_selected_value_label.setText("---")
        else:
            self.near_selected_ids_label.setText(",".join(map(str, near_ids)))
            self.near_selected_value_label.setText(
                f"{selected_actuator.formatValue(numpy.average([data[i] for i in near_indices]))}"
            )

        far_ids = filter(
            lambda f: f not in near_ids,
            FATable[selected_actuator.actuator.index].far_neighbors,
        )
        farIndices = list(
            selected_actuator.actuator.only_far_neighbors_indices(
                self.field.value_index
            )
        )
        if len(farIndices) == 0:
            self.far_selected_ids_label.setText("---")
            self.far_selected_value_label.setText("---")
        else:
            self.far_selected_ids_label.setText(",".join(map(str, far_ids)))
            self.far_selected_value_label.setText(
                f"{selected_actuator.formatValue(numpy.average([data[i] for i in farIndices]))}"
            )

    def __setModifyCommand(self, command: str | None) -> None:
        enabled = command is not None
        self.editButton.setEnabled(enabled)
        self.clearButton.setEnabled(enabled)

    def __change_field(self, topic_index: int, field_index: int) -> None:
        """
        Redraw actuators with new values.
        """
        self._topic = self.topics.topics[topic_index]
        self.__setModifyCommand(self._topic.command)
        self.field = self._topic.fields[field_index]
        # try:
        self.topics.change_topic(topic_index, self.data_changed, self.m1m3)
        data = self._get_data()
        self.change_values()
        self.update_values(data)
        self.data_changed(data)
        # except RuntimeError as err:
        #    print("ForceActuator.Widget.__change_field", err)
        #    self._topic = None
        #    pass

    @Slot()
    def data_changed(self, data: BaseMsgType) -> None:
        """
        Called when selected data are updated.

        Parameters
        ----------
        data : `class`
            Class holding data. See SALComm for details.
        """
        self.update_values(data)
        if data is None:
            self._set_unknown()
            return

        try:
            self.last_updated_label.setValue(data.timestamp)
        except AttributeError:
            self.last_updated_label.setValue(data.private_sndStamp)

        for i, axis in enumerate("xyz"):
            try:
                d = getattr(data, f"f{axis}")
                self.forces_moments[i].setText(f"{d:.3f} N")
            except AttributeError:
                self.forces_moments[i].setText("-N-")

            try:
                d = getattr(data, f"m{axis}")
                self.forces_moments[i + 3].setText(f"{d:.3f} Nm")
            except AttributeError:
                self.forces_moments[i + 3].setText("-N-")

        try:
            self.forces_moments[6].setText(f"{getattr(data, 'forceMagnitude'):.3f} N")
        except AttributeError:
            pass
