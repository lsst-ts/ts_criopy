# This file is part of M1M3 SS GUI.
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

from PySide2.QtCore import Slot, Qt
from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTableWidgetSelectionRange,
    QHeaderView,
    QSizePolicy,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QProgressBar,
)
from asyncqt import asyncSlot

from lsst.ts.idl.enums import MTM1M3

from ..M1M3FATable import (
    FATABLE,
    FATABLE_ID,
    FATABLE_XINDEX,
    FATABLE_YINDEX,
    FATABLE_SINDEX,
    actuatorIDToIndex,
)
from ..GUI.TimeChart import TimeChart, TimeChartView
from ..GUI.SAL import SALLog


class ForceActuatorBumpTestPageWidget(QWidget):
    """
    Enable user to select actuator for bump test. Show graphs depicting actual
    demand and measured forces. Shows button to run a bump test and stop any
    running bump test.

    Parameters
    ----------

    m1m3 : `SALComm object`
        SALComm communication object.
    """

    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3

        self.xIndex = self.yIndex = self.zIndex = self.sIndex = self.testedId = None
        self._testRunning = False

        actuatorBox = QGroupBox("Actuator")
        self.actuatorsTable = QTableWidget(
            max([row[FATABLE_ID] for row in FATABLE]) % 100, 12
        )
        self.actuatorsTable.setShowGrid(False)

        def setNone(r, c):
            item = QTableWidgetItem("")
            item.setFlags(Qt.NoItemFlags)
            self.actuatorsTable.setItem(r, c, item)

        for i in range(4):
            mr = min(
                [
                    row[FATABLE_ID]
                    for row in FATABLE
                    if row[FATABLE_ID] > (100 + 100 * i)
                ]
            )
            for r in range(mr):
                for c in range(i * 3, (i * 3) + 2):
                    setNone(r, c)

        for tr in range(len(FATABLE)):
            actuatorId = FATABLE[tr][FATABLE_ID]
            row = (actuatorId % 100) - 1
            colOffset = 3 * (int(actuatorId / 100) - 1)

            def getItem(text):
                item = QTableWidgetItem(text)
                item.setData(Qt.UserRole, actuatorId)
                return item

            self.actuatorsTable.setItem(row, 0 + colOffset, getItem(str(actuatorId)))
            self.actuatorsTable.setItem(row, 1 + colOffset, getItem("P"))
            if FATABLE[tr][FATABLE_SINDEX] is None:
                setNone(row, 2 + colOffset)
            else:
                self.actuatorsTable.setItem(
                    row,
                    2 + colOffset,
                    getItem("Y" if (FATABLE[tr][FATABLE_XINDEX] is None) else "X"),
                )

        self.actuatorsTable.horizontalHeader().hide()
        self.actuatorsTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.actuatorsTable.horizontalHeader().setStretchLastSection(False)
        self.actuatorsTable.verticalHeader().hide()
        self.actuatorsTable.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

        self.actuatorsTable.itemSelectionChanged.connect(self.itemSelectionChanged)
        self.actuatorsTable.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.MinimumExpanding
        )
        self.actuatorsTable.setFixedWidth(
            sum([self.actuatorsTable.columnWidth(c) for c in range(12)])
            + self.actuatorsTable.verticalScrollBar().geometry().height() / 2
            + 1
        )
        actuatorLayout = QVBoxLayout()
        actuatorLayout.addWidget(self.actuatorsTable)
        actuatorBox.setLayout(actuatorLayout)

        def testPB():
            pb = QProgressBar()
            pb.setMaximum(6)
            return pb

        self.primaryPB = testPB()
        self.primaryLabelPB = QLabel("Primary")

        self.secondaryPB = testPB()
        self.secondaryLabelPB = QLabel("Seconday")

        self.progressGroup = QGroupBox("Test progress")
        progressLayout = QGridLayout()
        progressLayout.addWidget(self.primaryLabelPB, 0, 0)
        progressLayout.addWidget(self.primaryPB, 0, 1)
        progressLayout.addWidget(self.secondaryLabelPB, 1, 0)
        progressLayout.addWidget(self.secondaryPB, 1, 1)
        # progressLayout.addStretch(1)
        self.progressGroup.setLayout(progressLayout)
        self.progressGroup.setMaximumWidth(410)

        self.chart = None
        self.chart_view = TimeChartView()
        self.chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        def makeButton(text, clicked):
            button = QPushButton(text)
            button.setEnabled(False)
            button.clicked.connect(clicked)
            return button

        self.bumpTestAllButton = makeButton("Bump test all", self.bumpTestAll)
        self.bumpTestButton = makeButton("Run bump test", self.issueCommandBumpTest)
        self.killBumpTestButton = makeButton(
            "Stop bump test", self.issueCommandKillBumpTest
        )

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.bumpTestAllButton)
        self.buttonLayout.addWidget(self.bumpTestButton)
        self.buttonLayout.addWidget(self.killBumpTestButton)

        self.layout = QVBoxLayout()
        self.forms = QHBoxLayout()
        self.forms.addWidget(actuatorBox)
        self.forms.addWidget(self.progressGroup)
        self.forms.addWidget(SALLog.Widget(self.m1m3))
        self.layout.addLayout(self.forms)
        self.layout.addWidget(self.chart_view)
        self.layout.addLayout(self.buttonLayout)
        self.setLayout(self.layout)

        self.m1m3.detailedState.connect(self.detailedState)
        self.m1m3.forceActuatorBumpTestStatus.connect(self.forceActuatorBumpTestStatus)

    @Slot()
    def itemSelectionChanged(self):
        """Called when an actuator is selected from the list."""
        items = self.actuatorsTable.selectedItems()
        if len(items) == 0:
            return
        if len(items) > 1:
            actuators = f"{items[0].data(Qt.UserRole)}..{items[-1].data(Qt.UserRole)}"
        else:
            actuators = f"{items[0].data(Qt.UserRole)}"

        self.bumpTestButton.setEnabled(not (self._anyCylinderRunning()))
        self.bumpTestButton.setText(f"Run bump test for FA ID {actuators}")

    def toggledTest(self, toggled):
        """Called when primary or secondary tests check box are toggled."""
        self.bumpTestButton.setEnabled(
            self.actuatorsTable.currentItem() is not None
            and not (self._anyCylinderRunning())
        )

    @asyncSlot()
    async def bumpTestAll(self):
        for i in range(4):
            colOffset = i * 3
            self.actuatorsTable.setRangeSelected(
                QTableWidgetSelectionRange(
                    0,
                    1 + colOffset,
                    self.actuatorsTable.rowCount() - 1,
                    2 + colOffset,
                ),
                False,
            )
            self.actuatorsTable.setRangeSelected(
                QTableWidgetSelectionRange(
                    0, colOffset, self.actuatorsTable.rowCount() - 1, colOffset
                ),
                True,
            )
        await self._testItem(self.actuatorsTable.selectedItems()[0])
        self.bumpTestButton.setEnabled(False)

    @asyncSlot()
    async def issueCommandBumpTest(self):
        """Call M1M3 bump test command."""
        await self._testItem(self.actuatorsTable.selectedItems()[0])

    async def _testItem(self, item):
        self.actuatorsTable.scrollToItem(item)
        self.testedId = item.data(Qt.UserRole)
        item.setSelected(False)
        self.zIndex = actuatorIDToIndex(self.testedId)

        self.xIndex = FATABLE[self.zIndex][FATABLE_XINDEX]
        self.yIndex = FATABLE[self.zIndex][FATABLE_YINDEX]
        self.sIndex = FATABLE[self.zIndex][FATABLE_SINDEX]

        items = []
        if self.xIndex is not None:
            items.append("X")
        if self.yIndex is not None:
            items.append("Y")
        items.append("Z")
        items = (
            list(map(lambda s: "Applied " + s, items))
            + [None]
            + list(map(lambda s: "Measured " + s, items))
        )

        if self.chart is not None:
            self.chart.clearData()

        self.chart = TimeChart({"Force (N)": items})

        self.chart_view.setChart(self.chart)

        self.progressGroup.setTitle(f"Test progress {self.testedId}")
        if self.sIndex is not None:
            self.secondaryLabelPB.setText("Y" if self.xIndex is None else "X")

        await self.m1m3.remote.cmd_forceActuatorBumpTest.set_start(
            actuatorId=self.testedId,
            testPrimary=not (item.text() == "X" or item.text() == "Y"),
            testSecondary=not (item.text() == "P") and self.sIndex is not None,
        )
        self.killBumpTestButton.setText(f"Stop bump test FA ID {self.testedId}")

    @asyncSlot()
    async def issueCommandKillBumpTest(self):
        """Kill bump test."""
        self.actuatorsTable.setRangeSelected(
            QTableWidgetSelectionRange(0, 0, self.actuatorsTable.rowCount() - 1, 11),
            False,
        )
        await self.m1m3.remote.cmd_killForceActuatorBumpTest.start()

    @Slot(map)
    def detailedState(self, data):
        """Called when detailedState event is received. Intercept to
        enable/disable form buttons."""
        if data.detailedState == MTM1M3.DetailedState.PARKEDENGINEERING:
            self.bumpTestAllButton.setEnabled(True)
            self.bumpTestButton.setEnabled(
                self.actuatorsTable.currentItem() is not None
            )
            self.killBumpTestButton.setEnabled(False)
            self.xIndex = self.yIndex = self.zIndex = None
        else:
            self.bumpTestAllButton.setEnabled(False)
            self.bumpTestButton.setEnabled(False)
            self.killBumpTestButton.setEnabled(False)

    @Slot(map)
    def appliedForces(self, data):
        """Adds applied forces to graph."""
        chartData = []
        if self.xIndex is not None:
            chartData.append(data.xForces[self.xIndex])
        if self.yIndex is not None:
            chartData.append(data.yForces[self.yIndex])
        if self.zIndex is not None:
            chartData.append(data.zForces[self.zIndex])

        self.chart.append(data.timestamp, chartData, cache_index=0)

    @Slot(map)
    def forceActuatorData(self, data):
        """Adds measured forces to graph."""
        chartData = []
        if self.xIndex is not None:
            chartData.append(data.xForce[self.xIndex])
        if self.yIndex is not None:
            chartData.append(data.yForce[self.yIndex])
        if self.zIndex is not None:
            chartData.append(data.zForce[self.zIndex])

        self.chart.append(data.timestamp, chartData, cache_index=1)

    @asyncSlot(map)
    async def forceActuatorBumpTestStatus(self, data):
        """Received when an actuator finish/start running bump tests or the
        actuator reports progress of the bump test."""

        testProgress = [
            "Not tested",
            "Testing start zero",
            "Testing positive",
            "Positive wait zero",
            "Testing negative",
            "Negative wait zero",
            "Passed",
            "Failed",
        ]

        # test progress
        if self.zIndex is not None:
            self.primaryPB.setEnabled(True)
            val = data.primaryTest[self.zIndex]
            self.primaryPB.setFormat(f"ID {self.testedId} - {testProgress[val]} - %v")
            self.primaryPB.setValue(min(6, val))
        else:
            self.primaryPB.setEnabled(False)

        if self.sIndex is not None:
            self.secondaryPB.setEnabled(True)
            val = data.secondaryTest[self.sIndex]
            self.secondaryPB.setFormat(f"ID {self.testedId} - {testProgress[val]} - %v")
            self.secondaryPB.setValue(min(6, val))
        else:
            self.secondaryPB.setEnabled(False)

        # list display
        for index in range(156):
            actuatorId = FATABLE[index][FATABLE_ID]
            row = (actuatorId % 100) - 1
            colOffset = 3 * (int(actuatorId / 100) - 1)

            def getColor(value):
                if value == 6:
                    return Qt.green
                elif value == 7:
                    return Qt.red
                elif not (value == 0):
                    return Qt.magenta
                return Qt.transparent

            pColor = getColor(data.primaryTest[index])

            self.actuatorsTable.item(row, colOffset + 1).setBackground(pColor)
            sIndex = FATABLE[index][FATABLE_SINDEX]
            if sIndex is not None:
                sColor = getColor(data.secondaryTest[sIndex])
                self.actuatorsTable.item(row, colOffset + 2).setBackground(sColor)
                if pColor == sColor:
                    self.actuatorsTable.item(row, colOffset).setBackground(pColor)
            else:
                self.actuatorsTable.item(row, colOffset).setBackground(pColor)

        # no tests running..
        if data.actuatorId < 0:
            selected = self.actuatorsTable.selectedItems()
            if len(selected) > 0:
                await self._testItem(selected[0])
            elif self._testRunning:
                self.bumpTestAllButton.setEnabled(True)
                self.bumpTestButton.setEnabled(
                    self.actuatorsTable.currentItem() is not None
                    and self._anyCylinder()
                )
                self.killBumpTestButton.setEnabled(False)
                self.xIndex = self.yIndex = self.zIndex = None
                self.m1m3.appliedForces.disconnect(self.appliedForces)
                self.m1m3.forceActuatorData.disconnect(self.forceActuatorData)
                self._testRunning = False

        elif self._testRunning is False:
            self.bumpTestButton.setEnabled(False)
            self.killBumpTestButton.setEnabled(True)
            self.m1m3.appliedForces.connect(self.appliedForces)
            self.m1m3.forceActuatorData.connect(self.forceActuatorData)
            self._testRunning = True

    # helper functions. Helps correctly enable/disable Run bump test button.
    def _anyCylinderRunning(self):
        return self._testRunning is True and self._anyCylinder()

    def _anyCylinder(self):
        return len(self.actuatorsTable.selectedItems()) > 0
