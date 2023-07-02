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

import asyncio
import typing

from asyncqt import asyncSlot
from lsst.ts.idl.enums import MTM1M3
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTableWidgetSelectionRange,
    QVBoxLayout,
    QWidget,
)

from ...gui import Colors
from ...gui.sal import SALLog
from ...gui.TimeChart import TimeChart, TimeChartView
from ...M1M3FATable import FATABLE, FATABLE_ZFA, actuator_id_to_index
from ...salcomm import MetaSAL, command


class BumpTestPageWidget(QWidget):
    """
    Enable user to select actuator for bump test. Show graphs depicting actual
    demand and measured forces. Shows button to run a bump test and stop any
    running bump test.

    Parameters
    ----------

    m1m3 : `SALComm object`
        SALComm communication object.
    """

    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        self.m1m3 = m1m3

        self.x_index: int | None = None
        self.y_index: int | None = None
        self.z_index: int | None = None
        self.s_index: int | None = None
        self.testedId: int | None = None
        self._testRunning = False

        actuatorBox = QGroupBox("Actuator")
        self.actuatorsTable = QTableWidget(
            int(max([row.actuator_id for row in FATABLE])) % 100, 12
        )
        self.actuatorsTable.setShowGrid(False)

        def set_none(r: int, c: int) -> None:
            item = QTableWidgetItem("")
            item.setFlags(Qt.NoItemFlags)
            self.actuatorsTable.setItem(r, c, item)

        for i in range(4):
            mr = int(
                min(
                    [
                        row.actuator_id
                        for row in FATABLE
                        if row.actuator_id > (100 + 100 * i)
                    ]
                )
            )
            for r in range(mr):
                for c in range(i * 3, (i * 3) + 2):
                    set_none(r, c)

        for tr in range(len(FATABLE)):
            actuatorId = FATABLE[tr].actuator_id
            row = (actuatorId % 100) - 1
            colOffset = 3 * (int(actuatorId / 100) - 1)

            def get_item(text: str) -> QTableWidgetItem:
                item = QTableWidgetItem(text)
                item.setData(Qt.UserRole, actuatorId)
                return item

            self.actuatorsTable.setItem(row, 0 + colOffset, get_item(str(actuatorId)))
            self.actuatorsTable.setItem(row, 1 + colOffset, get_item("P"))
            if FATABLE[tr].s_index is None:
                set_none(row, 2 + colOffset)
            else:
                self.actuatorsTable.setItem(
                    row,
                    2 + colOffset,
                    get_item("Y" if (FATABLE[tr].x_index is None) else "X"),
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

        def test_progress_bar() -> QProgressBar:
            pb = QProgressBar()
            pb.setMaximum(6)
            return pb

        self.primaryPB = test_progress_bar()
        self.primaryLabelPB = QLabel("Primary")

        self.secondaryPB = test_progress_bar()
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

        self.chart: TimeChart | None = None
        self.chart_view = TimeChartView()
        self.chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        def make_button(text: str, clicked: typing.Callable[[], None]) -> QPushButton:
            button = QPushButton(text)
            button.setEnabled(False)
            button.clicked.connect(clicked)
            return button

        self.bumpTestAllButton = make_button("Bump test all", self.bumpTestAll)
        self.bumpTestButton = make_button("Run bump test", self.issueCommandBumpTest)
        self.killBumpTestButton = make_button(
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

    def _recheckBumpTestButton(self, test_enabled: bool = True) -> None:
        detailedState = self.m1m3.remote.evt_detailedState.get()
        if detailedState is None or detailedState.detailedState not in [
            MTM1M3.DetailedState.PARKEDENGINEERING
        ]:
            self.bumpTestButton.setEnabled(False)
        else:
            self.bumpTestButton.setEnabled(
                test_enabled and not (self._anyCylinderRunning())
            )

    @Slot()
    def itemSelectionChanged(self) -> None:
        """Called when an actuator is selected from the list."""
        items = self.actuatorsTable.selectedItems()
        if len(items) == 0:
            return
        if len(items) > 1:
            actuators = f"{items[0].data(Qt.UserRole)}..{items[-1].data(Qt.UserRole)}"
        else:
            actuators = f"{items[0].data(Qt.UserRole)}"

        self._recheckBumpTestButton()
        self.bumpTestButton.setText(f"Run bump test for FA ID {actuators}")

    def toggledTest(self, toggled: bool) -> None:
        """Called when primary or secondary tests check box are toggled."""
        self._recheckBumpTestButton(self.actuatorsTable.currentItem() is not None)

    @asyncSlot()
    async def bumpTestAll(self) -> None:
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
    async def issueCommandBumpTest(self) -> None:
        """Call M1M3 bump test command."""
        await self._testItem(self.actuatorsTable.selectedItems()[0])

    async def _testItem(self, item: QTableWidgetItem) -> None:
        self.actuatorsTable.scrollToItem(item)
        self.testedId = item.data(Qt.UserRole)
        if self.testedId is None:
            return
        item.setSelected(False)
        index = actuator_id_to_index(self.testedId)
        if index is None:
            return

        fa = FATABLE[index]
        self.z_index = fa.z_index
        self.x_index = fa.x_index
        self.y_index = fa.y_index
        self.s_index = fa.s_index

        def add_timeChart() -> None:
            axis: list[str] = []
            if self.x_index is not None:
                axis.append("X")
            if self.y_index is not None:
                axis.append("Y")
            axis.append("Z")
            items = (
                ["Applied " + a for a in axis]
                + [None]
                + ["Measured " + a for a in axis]
            )

            if self.chart is not None:
                self.chart.clearData()

            self.chart = TimeChart({"Force (N)": items})

            self.chart_view.setChart(self.chart)

        asyncio.get_event_loop().call_soon(add_timeChart)

        self.progressGroup.setTitle(f"Test progress {self.testedId}")
        if self.s_index is not None:
            self.secondaryLabelPB.setText("Y" if self.x_index is None else "X")

        await command(
            self,
            self.m1m3.remote.cmd_forceActuatorBumpTest,
            actuatorId=self.testedId,
            testPrimary=not (item.text() == "X" or item.text() == "Y"),
            testSecondary=not (item.text() == "P") and self.s_index is not None,
        )
        self.killBumpTestButton.setText(f"Stop bump test FA ID {self.testedId}")

    @asyncSlot()
    async def issueCommandKillBumpTest(self) -> None:
        """Kill bump test."""
        self.actuatorsTable.setRangeSelected(
            QTableWidgetSelectionRange(0, 0, self.actuatorsTable.rowCount() - 1, 11),
            False,
        )
        await command(self, self.m1m3.remote.cmd_killForceActuatorBumpTest)

    @Slot()
    def detailedState(self, data: typing.Any) -> None:
        """Called when detailedState event is received. Intercept to
        enable/disable form buttons."""
        if data.detailedState == MTM1M3.DetailedState.PARKEDENGINEERING:
            self.bumpTestAllButton.setEnabled(True)
            self.bumpTestButton.setEnabled(
                self.actuatorsTable.currentItem() is not None
            )
            self.killBumpTestButton.setEnabled(False)
            self.x_index = self.y_index = self.z_index = None
        else:
            self.bumpTestAllButton.setEnabled(False)
            self.bumpTestButton.setEnabled(False)
            self.killBumpTestButton.setEnabled(False)

    @Slot()
    def appliedForces(self, data: typing.Any) -> None:
        """Adds applied forces to graph."""
        chartData: list[float] = []
        if self.x_index is not None:
            chartData.append(data.xForces[self.x_index])
        if self.y_index is not None:
            chartData.append(data.yForces[self.y_index])
        if self.z_index is not None:
            chartData.append(data.zForces[self.z_index])

        if self.chart is not None:
            self.chart.append(data.timestamp, chartData, cache_index=0)

    @Slot()
    def forceActuatorData(self, data: typing.Any) -> None:
        """Adds measured forces to graph."""
        chartData: list[float] = []
        if self.x_index is not None:
            chartData.append(data.xForce[self.x_index])
        if self.y_index is not None:
            chartData.append(data.yForce[self.y_index])
        if self.z_index is not None:
            chartData.append(data.zForce[self.z_index])

        if self.chart is not None:
            self.chart.append(data.timestamp, chartData, cache_index=1)

    @asyncSlot()
    async def forceActuatorBumpTestStatus(self, data: typing.Any) -> None:
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
        if self.z_index is not None:
            self.primaryPB.setEnabled(True)
            val = data.primaryTest[self.z_index]
            self.primaryPB.setFormat(f"ID {self.testedId} - {testProgress[val]} - %v")
            self.primaryPB.setValue(min(6, val))
        else:
            self.primaryPB.setEnabled(False)

        if self.s_index is not None:
            self.secondaryPB.setEnabled(True)
            val = data.secondaryTest[self.s_index]
            self.secondaryPB.setFormat(f"ID {self.testedId} - {testProgress[val]} - %v")
            self.secondaryPB.setValue(min(6, val))
        else:
            self.secondaryPB.setEnabled(False)

        # list display
        for index in range(FATABLE_ZFA):
            actuatorId = FATABLE[index].actuator_id
            row = (actuatorId % 100) - 1
            colOffset = 3 * (int(actuatorId / 100) - 1)

            def getColor(value: int) -> QColor:
                if value == 6:
                    return Colors.OK
                elif value == 7:
                    return Colors.ERROR
                elif not (value == 0):
                    return Qt.magenta
                return Qt.transparent

            pColor = getColor(data.primaryTest[index])

            self.actuatorsTable.item(row, colOffset + 1).setBackground(pColor)
            s_index = FATABLE[index].s_index
            if s_index is not None:
                sColor = getColor(data.secondaryTest[s_index])
                self.actuatorsTable.item(row, colOffset + 2).setBackground(sColor)
                if pColor == sColor:
                    self.actuatorsTable.item(row, colOffset).setBackground(pColor)
            else:
                self.actuatorsTable.item(row, colOffset).setBackground(pColor)

        # no tests running..
        # first check that we are still in PARKEDENGINEERING
        detailedState = self.m1m3.remote.evt_detailedState.get()
        if detailedState is None or detailedState.detailedState not in [
            MTM1M3.DetailedState.PARKEDENGINEERING
        ]:
            self.bumpTestAllButton.setEnabled(False)
            self.bumpTestButton.setEnabled(False)
            self.killBumpTestButton.setEnabled(False)
            return

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
                self.x_index = self.y_index = self.z_index = None
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
    def _anyCylinderRunning(self) -> bool:
        return self._testRunning is True and self._anyCylinder()

    def _anyCylinder(self) -> bool:
        return len(self.actuatorsTable.selectedItems()) > 0
