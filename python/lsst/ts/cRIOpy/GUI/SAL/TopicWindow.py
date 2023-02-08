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

from PySide2.QtCore import Slot
from PySide2.QtWidgets import (
    QLabel,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QListWidget,
    QSplitter,
)
from ..CustomLabels import DockWindow, WarningLabel
from .TimeDeltaLabel import TimeDeltaLabel


class TopicWindow(DockWindow):
    """
    Abstract class for widget and graphics display of selected M1M3 values.
    Children classes must implement updateValues(data) method.

    Parameters
    ----------

    title : `str`
        Dock title and name.
    comm : `SALComm`
        SALComm instance to communicate with SAL.
    topics : `TopicData`
        Topics data associated with widget.
    userWidget : `QWidget`
        Widget to be displayed on left from value selection. Its content shall
        be update in updateValues(data) method.

    Methods
    -------

    updateValues(data)
        Must be defined in every child. This is called when selection is
        changed or when new data become available. If data parameter is None,
        then no data has been received for selected read topic.
    """

    def __init__(self, title, comm, topics, userWidget):
        super().__init__(title)

        self.comm = comm
        self.topics = topics

        splitter = QSplitter()

        self.field = None

        plotLayout = QVBoxLayout()
        selectionLayout = QVBoxLayout()
        detailsLayout = QFormLayout()
        filterLayout = QHBoxLayout()

        w_left = QWidget()
        w_left.setLayout(plotLayout)
        splitter.addWidget(w_left)
        w_right = QWidget()
        w_right.setLayout(selectionLayout)
        splitter.addWidget(w_right)

        splitter.setCollapsible(0, False)
        splitter.setStretchFactor(0, 10)
        splitter.setStretchFactor(1, 0)

        selectionLayout.addLayout(detailsLayout)
        selectionLayout.addWidget(QLabel("Filter Data"))
        selectionLayout.addLayout(filterLayout)

        self.selectedActuatorIdLabel = QLabel()
        self.selectedActuatorValueLabel = QLabel()
        self.selectedActuatorWarningLabel = WarningLabel()
        self.lastUpdatedLabel = TimeDeltaLabel()

        self.topicList = QListWidget()
        self.topicList.currentRowChanged.connect(self.currentTopicChanged)
        for topic in self.topics.topics:
            self.topicList.addItem(topic.name)
        self.fieldList = QListWidget()
        self.fieldList.currentRowChanged.connect(self.currentFieldChanged)

        plotLayout.addWidget(userWidget)

        detailsLayout.addRow(QLabel("Selected Actuator Details"), QLabel(""))
        detailsLayout.addRow(QLabel("Actuator Id"), self.selectedActuatorIdLabel)
        detailsLayout.addRow(QLabel("Actuator Value"), self.selectedActuatorValueLabel)
        detailsLayout.addRow(
            QLabel("Actuator Warning"), self.selectedActuatorWarningLabel
        )
        detailsLayout.addRow(QLabel("Last Updated"), self.lastUpdatedLabel)

        filterLayout.addWidget(self.topicList)
        filterLayout.addWidget(self.fieldList)

        self.topicList.setCurrentRow(0)

        self.setWidget(splitter)

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

    def updateSelectedActuator(self, s):
        """
        Called from childrens to update currently selected actuator display.

        Parameters
        ----------

        s : `map`
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

    def _changeField(self, topicIndex, fieldIndex):
        """
        Redraw actuators with new values.
        """
        topic = self.topics.topics[topicIndex]
        self.field = topic.fields[fieldIndex]
        try:
            self.topics.changeTopic(topicIndex, self.dataChanged, self.comm)

            data = getattr(self.comm.remote, topic.getTopic()).get()
            self.dataChanged(data)
        except RuntimeError as err:
            print("TopicWidget._changeField", err)
            pass

    @Slot(map)
    def dataChanged(self, data):
        """
        Called when selected data are updated.

        Parameters
        ----------

        """
        self.updateValues(data)
        if data is None:
            self._setUnknown()
        else:
            self.lastUpdatedLabel.setTime(data.timestamp)
