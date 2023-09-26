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
from PySide2.QtCore import Slot
from PySide2.QtWidgets import (
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
from ...m1m3_fa_table import FATABLE, FAIndex
from ...salcomm import MetaSAL, command
from .topics import Topics
from .update_window import UpdateWindow


class Widget(QSplitter):
    """
    Abstract class for widget and graphics display of selected M1M3 values.
    Children classes must implement changeValues and updateValues(data)
    methods.

    Parameters
    ----------

    m1m3 : `SALComm`
        SALComm instance to communicate with SAL.
    userWidget : `QWidget`
        Widget to be displayed on left from value selection. Its content shall
        be update in updateValues(data) method.
    """

    def __init__(self, m1m3: MetaSAL, userWidget: QWidget):
        super().__init__()
        self.m1m3 = m1m3

        self.updateWindows: dict[str, QWidget] = {}

        self.field: typing.Any | None = None
        self._topic: TopicData | None = None

        plotLayout = QVBoxLayout()
        selectionLayout = QVBoxLayout()
        detailsLayout = QGridLayout()
        filterLayout = QGridLayout()

        selectionLayout.addLayout(detailsLayout)
        selectionLayout.addLayout(filterLayout)

        self.selectedActuatorIdLabel = QLabel()
        self.selectedActuatorValueLabel = QLabel()
        self.selectedActuatorWarningLabel = WarningLabel()
        self.lastUpdatedLabel = TimeDeltaLabel()

        self.nearSelectedIdsLabel = QLabel()
        self.nearSelectedValueLabel = QLabel()

        self.farSelectedIdsLabel = QLabel()
        self.farSelectedValueLabel = QLabel()

        self.topicList = QListWidget()
        self.topicList.setFixedWidth(256)
        self.topicList.currentRowChanged.connect(self.currentTopicChanged)
        self.topics = Topics()
        for topic in self.topics.topics:
            self.topicList.addItem(topic.name)
        self.fieldList = QListWidget()
        self.fieldList.setFixedWidth(256)
        self.fieldList.currentRowChanged.connect(self.currentFieldChanged)

        plotLayout.addWidget(userWidget)

        def addDetails(
            row: int, name: str, label: QLabel, nears: QLabel, fars: QLabel
        ) -> None:
            detailsLayout.addWidget(QLabel(name), row, 0)
            detailsLayout.addWidget(label, row, 1)
            detailsLayout.addWidget(nears, row, 2)
            detailsLayout.addWidget(fars, row, 3)

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
            self.selectedActuatorIdLabel,
            self.nearSelectedIdsLabel,
            self.farSelectedIdsLabel,
        )
        addDetails(
            2,
            "<b>Value</b>",
            self.selectedActuatorValueLabel,
            self.nearSelectedValueLabel,
            self.farSelectedValueLabel,
        )
        addDetails(
            3,
            "<b>Last Updated</b>",
            self.lastUpdatedLabel,
            QLabel("<b>Warning</b>"),
            self.selectedActuatorWarningLabel,
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

        detailsLayout.addWidget(QLabel("<b>Forces</b>"), 4, 0)
        detailsLayout.addWidget(self.forces_moments[6], 5, 0)
        for i, a in enumerate("XYZ"):
            detailsLayout.addWidget(QLabel(f"<b>{a}</b>"), 4, i + 1)
            detailsLayout.addWidget(self.forces_moments[i], 5, i + 1)

        detailsLayout.addWidget(QLabel("<b>Moments</b>"), 6, 0)
        for i, a in enumerate("XYZ"):
            detailsLayout.addWidget(QLabel(f"<b>{a}</b>"), 6, i + 1)
            detailsLayout.addWidget(self.forces_moments[i + 3], 7, i + 1)

        self.editButton = QPushButton("&Modify")
        self.editButton.clicked.connect(self.editValues)
        self.clearButton = QPushButton("&Zero")
        self.clearButton.clicked.connect(self.zeroValues)

        detailsLayout.addWidget(self.editButton, 8, 0, 1, 2)
        detailsLayout.addWidget(self.clearButton, 8, 2, 1, 2)

        filterLayout.addWidget(QLabel("Topic"), 1, 1)
        filterLayout.addWidget(QLabel("Field"), 1, 2)
        filterLayout.addWidget(self.topicList, 2, 1)
        filterLayout.addWidget(self.fieldList, 2, 2)

        self.topicList.setCurrentRow(0)

        w_left = QWidget()
        w_left.setLayout(plotLayout)
        w_right = QWidget()
        w_right.setLayout(selectionLayout)
        w_right.setMaximumWidth(w_right.size().width())
        self.addWidget(w_left)
        self.addWidget(w_right)

        self.setCollapsible(0, False)
        self.setStretchFactor(0, 10)
        self.setStretchFactor(1, 1)

    def changeValues(self) -> None:
        """Called when new values were selected by the user."""
        raise NotImplementedError(
            "changeValues method must be implemented in all Widget childrens"
        )

    def updateValues(self, data: typing.Any) -> None:
        """Called when new data are available through SAL callback.

        Parameters
        ----------
        data : `object`
            New data structure, passed from SAL handler.
        """
        raise NotImplementedError(
            "updateValues method must be implemented in all Widget childrens"
        )

    @Slot()
    def currentTopicChanged(self, topicIndex: int) -> None:
        if topicIndex < 0:
            self._set_unknown()
            return

        self.fieldList.clear()
        for field in self.topics.topics[topicIndex].fields:
            self.fieldList.addItem(field.name)

        fieldIndex = self.topics.topics[topicIndex].selectedField
        if fieldIndex < 0:
            self._set_unknown()
            return

        self.fieldList.setCurrentRow(fieldIndex)
        self.__change_field(topicIndex, fieldIndex)

    @Slot()
    def currentFieldChanged(self, fieldIndex: int) -> None:
        topicIndex = self.topicList.currentRow()
        if topicIndex < 0 or fieldIndex < 0:
            self._set_unknown()
            return
        self.__change_field(topicIndex, fieldIndex)
        self.topics.topics[topicIndex].selectedField = fieldIndex

    @Slot()
    def editValues(self) -> None:
        def get_axis(topic: TopicData) -> str:
            axis = ""
            for f in topic.fields:
                if f.valueIndex == FAIndex.X:
                    axis += "x"
                elif f.valueIndex == FAIndex.Y:
                    axis += "y"
                elif f.valueIndex == FAIndex.Z:
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
        self.lastUpdatedLabel.setUnknown()

    def getCurrentFieldName(self) -> tuple[str, str]:
        if self._topic is None or self._topic.topic is None or self.field is None:
            raise RuntimeError(
                "Topic or field is None in Widget.getCurrentFieldName:"
                f" {self._topic}, {self.field}"
            )
        return (self._topic.topic, self.field.fieldName)

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
            self.selectedActuatorIdLabel.setText("not selected")
            self.selectedActuatorValueLabel.setText("")
            self.selectedActuatorWarningLabel.setText("")
            return

        if self.field is None:
            raise RuntimeError("field not selected in Widget.updateSelectedActuator")

        self.selectedActuatorIdLabel.setText(
            str(selected_actuator.actuator.actuator_id)
        )
        self.selectedActuatorValueLabel.setText(selected_actuator.getValue())
        self.selectedActuatorWarningLabel.setValue(selected_actuator.warning)

        data = self.field.getValue(self._get_data())

        # near neighbour
        nearIDs = FATABLE[selected_actuator.actuator.index].near_neighbors
        nearIndices = list(
            selected_actuator.actuator.near_neighbors_indices(self.field.valueIndex)
        )

        if len(nearIndices) == 0:
            self.nearSelectedIdsLabel.setText("---")
            self.nearSelectedValueLabel.setText("---")
        else:
            self.nearSelectedIdsLabel.setText(",".join(map(str, nearIDs)))
            self.nearSelectedValueLabel.setText(
                f"{selected_actuator.formatValue(numpy.average([data[i] for i in nearIndices]))}"
            )

        farIDs = filter(
            lambda f: f not in nearIDs,
            FATABLE[selected_actuator.actuator.index].far_neighbors,
        )
        farIndices = list(
            selected_actuator.actuator.only_far_neighbors_indices(self.field.valueIndex)
        )
        if len(farIndices) == 0:
            self.farSelectedIdsLabel.setText("---")
            self.farSelectedValueLabel.setText("---")
        else:
            self.farSelectedIdsLabel.setText(",".join(map(str, farIDs)))
            self.farSelectedValueLabel.setText(
                f"{selected_actuator.formatValue(numpy.average([data[i] for i in farIndices]))}"
            )

    def __setModifyCommand(self, command: str | None) -> None:
        enabled = command is not None
        self.editButton.setEnabled(enabled)
        self.clearButton.setEnabled(enabled)

    def __change_field(self, topicIndex: int, fieldIndex: int) -> None:
        """
        Redraw actuators with new values.
        """
        self._topic = self.topics.topics[topicIndex]
        self.__setModifyCommand(self._topic.command)
        self.field = self._topic.fields[fieldIndex]
        try:
            self.topics.change_topic(topicIndex, self.dataChanged, self.m1m3)
            data = self._get_data()
            self.changeValues()
            self.updateValues(data)
            self.dataChanged(data)
        except RuntimeError as err:
            print("ForceActuator.Widget.__change_field", err)
            self._topic = None
            pass

    @Slot()
    def dataChanged(self, data: typing.Any) -> None:
        """
        Called when selected data are updated.

        Parameters
        ----------
        data : `class`
            Class holding data. See SALComm for details.
        """
        self.updateValues(data)
        if data is None:
            self._set_unknown()
            return

        try:
            self.lastUpdatedLabel.setTime(data.timestamp)
        except AttributeError:
            self.lastUpdatedLabel.setTime(data.private_sndStamp)

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

        self.forces_moments[6].setText(f"{getattr(data,'forceMagnitude'):.3f} N")
