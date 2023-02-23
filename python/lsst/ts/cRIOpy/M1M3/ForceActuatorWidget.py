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

import numpy

from PySide2.QtCore import Slot
from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QListWidget,
    QSplitter,
)
from ..GUI import WarningLabel
from ..GUI.SAL import TimeDeltaLabel
from ..M1M3FATable import (
    FATABLE,
    FATABLE_NEAR_NEIGHBOR_INDEX,
    FATABLE_FAR_NEIGHBOR_INDEX,
    nearNeighborIndices,
    onlyFarNeighborIndices,
)
from .ForceActuatorTopics import ForceActuatorTopics


class ForceActuatorWidget(QSplitter):
    """
    Abstract class for widget and graphics display of selected M1M3 values.
    Children classes must implement updateValues(data, changed) method.

    Parameters
    ----------

    m1m3 : `SALComm`
        SALComm instance to communicate with SAL.
    userWidget : `QWidget`
        Widget to be displayed on left from value selection. Its content shall
        be update in updateValues(data) method.

    Methods
    -------

    updateValues(data, changed)
        Must be defined in every child. This is called when selection is
        changed or when new data become available. If data parameter is None,
        then no data has been received for selected read topic.
    """

    def __init__(self, m1m3, userWidget):
        super().__init__()
        self.m1m3 = m1m3

        self.field = None
        self._topic = None

        plotLayout = QVBoxLayout()
        selectionLayout = QVBoxLayout()
        detailsLayout = QGridLayout()
        filterLayout = QHBoxLayout()

        selectionLayout.addLayout(detailsLayout)
        selectionLayout.addWidget(QLabel("Filter Data"))
        selectionLayout.addLayout(filterLayout)

        self.selectedActuatorIdLabel = QLabel()
        self.selectedActuatorValueLabel = QLabel()
        self.selectedActuatorWarningLabel = WarningLabel()
        self.lastUpdatedLabel = TimeDeltaLabel()

        self.nearSelectedIdsLabel = QLabel()
        self.nearSelectedValueLabel = QLabel()
        self.nearSelectedWarningLabel = QLabel()
        self.nearSelectedUpdateLabel = QLabel()

        self.farSelectedIdsLabel = QLabel()
        self.farSelectedValueLabel = QLabel()
        self.farSelectedWarningLabel = QLabel()
        self.farSelectedUpdateLabel = QLabel()

        self.topicList = QListWidget()
        self.topicList.setFixedWidth(256)
        self.topicList.currentRowChanged.connect(self.currentTopicChanged)
        self.topics = ForceActuatorTopics()
        for topic in self.topics.topics:
            self.topicList.addItem(topic.name)
        self.fieldList = QListWidget()
        self.fieldList.setFixedWidth(256)
        self.fieldList.currentRowChanged.connect(self.currentFieldChanged)

        plotLayout.addWidget(userWidget)

        def addDetails(row, name, label, nears, fars):
            detailsLayout.addWidget(QLabel(name), row, 0)
            detailsLayout.addWidget(label, row, 1)
            detailsLayout.addWidget(nears, row, 2)
            detailsLayout.addWidget(fars, row, 3)

        addDetails(
            0,
            "Variable",
            QLabel("Selected"),
            QLabel("Near Neighbors"),
            QLabel("Far Neighbors"),
        )
        addDetails(
            1,
            "Id",
            self.selectedActuatorIdLabel,
            self.nearSelectedIdsLabel,
            self.farSelectedIdsLabel,
        )
        addDetails(
            2,
            "Value",
            self.selectedActuatorValueLabel,
            self.nearSelectedValueLabel,
            self.farSelectedValueLabel,
        )
        addDetails(
            3,
            "Warning",
            self.selectedActuatorWarningLabel,
            self.nearSelectedWarningLabel,
            self.farSelectedWarningLabel,
        )
        addDetails(
            4,
            "Last Updated",
            self.lastUpdatedLabel,
            self.nearSelectedUpdateLabel,
            self.farSelectedUpdateLabel,
        )

        filterLayout.addWidget(self.topicList)
        filterLayout.addWidget(self.fieldList)

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
        self.setStretchFactor(1, 0)

    @Slot(int)
    def currentTopicChanged(self, topicIndex):
        if topicIndex < 0:
            self._setUnknown()
            return

        self.fieldList.clear()
        for field in self.topics.topics[topicIndex].fields:
            self.fieldList.addItem(field.name)

        fieldIndex = self.topics.topics[topicIndex].selectedField
        if fieldIndex < 0:
            self._setUnknown()
            return

        self.fieldList.setCurrentRow(fieldIndex)
        self._changeField(topicIndex, fieldIndex)

    @Slot(int)
    def currentFieldChanged(self, fieldIndex):
        topicIndex = self.topicList.currentRow()
        if topicIndex < 0 or fieldIndex < 0:
            self._setUnknown()
            return
        self._changeField(topicIndex, fieldIndex)
        self.topics.topics[topicIndex].selectedField = fieldIndex

    def _setUnknown(self):
        self.lastUpdatedLabel.setUnknown()

    def getCurrentFieldName(self) -> (str, str):
        return (self._topic.topic, self.field.fieldName)

    def _getData(self):
        return getattr(self.m1m3.remote, self._topic.getTopic()).get()

    def _getFieldData(self):
        return self.field.getValue(self._getData())

    def updateSelectedActuator(self, s):
        """
        Called from childrens to update currently selected actuator display.

        Parameters
        ----------

        s : `ForceActuator`
            Contains id (selected actuator ID), data (selected actuator current
            value) and warning (boolean, true if value is in warning).
        """
        if s is None:
            self.selectedActuatorIdLabel.setText("not selected")
            self.selectedActuatorValueLabel.setText("")
            self.selectedActuatorWarningLabel.setText("")
            return

        self.selectedActuatorIdLabel.setText(str(s.id))
        self.selectedActuatorValueLabel.setText(s.getValue())
        self.selectedActuatorWarningLabel.setValue(s.warning)

        # near neighbour
        nearIDs = FATABLE[s.index][FATABLE_NEAR_NEIGHBOR_INDEX]
        nearIndices = nearNeighborIndices(s.index, self.field.valueIndex)
        field = self._getFieldData()
        self.nearSelectedIdsLabel.setText(",".join(map(str, nearIDs)))
        self.nearSelectedValueLabel.setText(
            f"{s.formatValue(numpy.average([field[i] for i in nearIndices]))}"
        )

        farIDs = filter(
            lambda f: f not in nearIDs, FATABLE[s.index][FATABLE_FAR_NEIGHBOR_INDEX]
        )
        farIndices = onlyFarNeighborIndices(s.index, self.field.valueIndex)
        self.farSelectedIdsLabel.setText(",".join(map(str, farIDs)))
        self.farSelectedValueLabel.setText(
            f"{s.formatValue(numpy.average([field[i] for i in farIndices]))}"
        )

    def _changeField(self, topicIndex, fieldIndex):
        """
        Redraw actuators with new values.
        """
        self._topic = self.topics.topics[topicIndex]
        self.field = self._topic.fields[fieldIndex]
        try:
            self.topics.changeTopic(topicIndex, self.dataChanged, self.m1m3)
            data = self._getData()
            self.updateValues(data, True)
            self.dataChanged(data)
        except RuntimeError as err:
            print("ForceActuatorWidget._changeField", err)
            self._topic = None
            pass

    @Slot(map)
    def dataChanged(self, data):
        """
        Called when selected data are updated.

        Parameters
        ----------
        data : `class`
            Class holding data. See SALComm for details.
        """
        self.updateValues(data, False)
        if data is None:
            self._setUnknown()
        else:
            try:
                self.lastUpdatedLabel.setTime(data.timestamp)
            except AttributeError:
                self.lastUpdatedLabel.setTime(data.private_sndStamp)
