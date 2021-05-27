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
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QListWidget,
)
from .QTHelpers import setWarningLabel
from .TopicData import Topics
from .TimeDeltaLabel import TimeDeltaLabel


class ForceActuatorWidget(QWidget):
    """
    Abstract class for widget and graphics display of selected M1M3 values.
    Children classes must implement updateValues(data) method.

    Parameters
    ----------

    m1m3 : `SALComm`
        SALComm instance to communicate with SAL.
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

    def __init__(self, m1m3, userWidget):
        super().__init__()
        self.m1m3 = m1m3

        self.fieldDataIndex = None

        self.layout = QHBoxLayout()
        self.plotLayout = QVBoxLayout()
        self.selectionLayout = QVBoxLayout()
        self.detailsLayout = QFormLayout()
        self.filterLayout = QHBoxLayout()
        self.layout.addLayout(self.plotLayout)
        self.layout.addLayout(self.selectionLayout)
        self.selectionLayout.addLayout(self.detailsLayout)
        self.selectionLayout.addWidget(QLabel("Filter Data"))
        self.selectionLayout.addLayout(self.filterLayout)
        self.setLayout(self.layout)

        self.selectedActuatorIdLabel = QLabel("")
        self.selectedActuatorValueLabel = QLabel("")
        self.selectedActuatorWarningLabel = QLabel("")
        self.lastUpdatedLabel = TimeDeltaLabel()

        self.topicList = QListWidget()
        self.topicList.setFixedWidth(256)
        self.topicList.currentRowChanged.connect(self.currentTopicChanged)
        self.topics = Topics()
        for topic in self.topics.topics:
            self.topicList.addItem(topic.name)
        self.fieldList = QListWidget()
        self.fieldList.setFixedWidth(256)
        self.fieldList.currentRowChanged.connect(self.currentFieldChanged)

        self.plotLayout.addWidget(userWidget)

        self.detailsLayout.addRow(QLabel("Selected Actuator Details"), QLabel(""))
        self.detailsLayout.addRow(QLabel("Actuator Id"), self.selectedActuatorIdLabel)
        self.detailsLayout.addRow(
            QLabel("Actuator Value"), self.selectedActuatorValueLabel
        )
        self.detailsLayout.addRow(
            QLabel("Actuator Warning"), self.selectedActuatorWarningLabel
        )
        self.detailsLayout.addRow(QLabel("Last Updated"), self.lastUpdatedLabel)

        self.filterLayout.addWidget(self.topicList)
        self.filterLayout.addWidget(self.fieldList)

        self.topicList.setCurrentRow(0)

    @Slot(int)
    def currentTopicChanged(self, topicIndex):
        if topicIndex < 0:
            self._setUnknown()
            return

        self.fieldList.clear()
        for field in self.topics.topics[topicIndex].fields:
            self.fieldList.addItem(field[0])

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
            Contains id (selected actuator ID), data (selected actuator current value) and warning (boolean, true if value is in warning).
        """
        if s is None:
            self.selectedActuatorIdLabel.setText("not selected")
            self.selectedActuatorValueLabel.setText("")
            self.selectedActuatorWarningLabel.setText("")
            return

        self.selectedActuatorIdLabel.setText(str(s.id))
        self.selectedActuatorValueLabel.setText(str(s.data))
        setWarningLabel(self.selectedActuatorWarningLabel, s.warning)

    def _changeField(self, topicIndex, fieldIndex):
        """
        Redraw actuators with new values.
        """
        topic = self.topics.topics[topicIndex]
        field = topic.fields[fieldIndex]
        self.fieldGetter = field[1]
        self.fieldDataIndex = field[2]()
        try:
            self.topics.changeTopic(topicIndex, self.dataChanged, self.m1m3)

            data = getattr(self.m1m3.remote, topic.getTopic()).get()
            self.dataChanged(data)
        except RuntimeError as err:
            print("ForceActuatorWidget._changeField", err)
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
