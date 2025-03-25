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

from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.enums import MTM1M3
from lsst.ts.xml.tables.m1m3 import FATable, ForceActuatorData, actuator_id_to_index
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
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
from qasync import asyncSlot

from ...gui import Colors, TimeChart, TimeChartView
from ...gui.sal import LogWidget
from ...salcomm import MetaSAL, command


def is_tested(state: int) -> int:
    if state in [
        MTM1M3.BumpTest.TRIGGERED,
        MTM1M3.BumpTest.TESTINGPOSITIVE,
        MTM1M3.BumpTest.TESTINGPOSITIVEWAIT,
        MTM1M3.BumpTest.TESTINGNEGATIVE,
        MTM1M3.BumpTest.TESTINGNEGATIVEWAIT,
    ]:
        return 1
    return 0


def get_tested_fas(
    primary_status: list[int], secondary_status: list[int]
) -> list[ForceActuatorData]:
    """Returns currently tested force actuators.

    Parameters
    ----------
    primary_status : list[int]
        Array of primary cylinder/axis bump test states
    secondary_status : list[int]
        List of secondary cylinder/axis bump test states

    Returns
    -------
    tested : list[ForceActuatorData]
        Currently tested force actuators.
    """
    return [
        fa
        for fa in FATable
        if (
            is_tested(primary_status[fa.z_index])
            or (fa.s_index is not None and is_tested(secondary_status[fa.s_index]))
        )
    ]


def get_min_tested_distance(
    fa: ForceActuatorData, tested_fas: list[ForceActuatorData]
) -> float:
    return 10 if len(tested_fas) == 0 else min([tf.distance(fa) for tf in tested_fas])


def can_be_tested(
    fa: ForceActuatorData, tested_fas: list[ForceActuatorData], test_distance: float
) -> bool:
    return get_min_tested_distance(fa, tested_fas) > test_distance


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
        self.tested_id: int | None = None

        self._test_running: bool = False

        actuator_box = QGroupBox("Actuator")
        self.actuators_table = QTableWidget(
            int(max([row.actuator_id for row in FATable])) % 100, 12
        )
        self.actuators_table.setShowGrid(False)

        def set_none(r: int, c: int) -> None:
            item = QTableWidgetItem("")
            item.setFlags(Qt.NoItemFlags)
            self.actuators_table.setItem(r, c, item)

        for i in range(4):
            mr = int(
                min(
                    [
                        row.actuator_id
                        for row in FATable
                        if row.actuator_id > (100 + 100 * i)
                    ]
                )
            )
            for r in range(mr):
                for c in range(i * 3, (i * 3) + 2):
                    set_none(r, c)

        for tr in range(len(FATable)):
            actuator_id = FATable[tr].actuator_id
            row = (actuator_id % 100) - 1
            colOffset = 3 * (int(actuator_id / 100) - 1)

            def get_item(text: str) -> QTableWidgetItem:
                item = QTableWidgetItem(text)
                item.setData(Qt.UserRole, actuator_id)
                return item

            self.actuators_table.setItem(row, 0 + colOffset, get_item(str(actuator_id)))
            self.actuators_table.setItem(row, 1 + colOffset, get_item("P"))
            if FATable[tr].s_index is None:
                set_none(row, 2 + colOffset)
            else:
                self.actuators_table.setItem(
                    row,
                    2 + colOffset,
                    get_item("Y" if (FATable[tr].x_index is None) else "X"),
                )

        self.actuators_table.horizontalHeader().hide()
        self.actuators_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.actuators_table.horizontalHeader().setStretchLastSection(False)
        self.actuators_table.verticalHeader().hide()
        self.actuators_table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )

        self.actuators_table.itemSelectionChanged.connect(self.item_selection_changed)
        self.actuators_table.setSizePolicy(
            QSizePolicy.Minimum, QSizePolicy.MinimumExpanding
        )
        self.actuators_table.setFixedWidth(
            sum([self.actuators_table.columnWidth(c) for c in range(12)])
            + self.actuators_table.verticalScrollBar().geometry().height() / 2
            + 1
        )
        actuator_layout = QVBoxLayout()
        actuator_layout.addWidget(self.actuators_table)
        actuator_box.setLayout(actuator_layout)

        def test_progress_bar() -> QProgressBar:
            pb = QProgressBar()
            pb.setMaximum(6)
            return pb

        self.primary_progress_bar = test_progress_bar()
        self.secondary_progress_label = QLabel("Secondary")
        self.secondary_progress_bar = test_progress_bar()

        self.progress_group = QGroupBox("Test progress")
        progress_layout = QGridLayout()
        progress_layout.addWidget(QLabel("Primary"), 0, 0)
        progress_layout.addWidget(self.primary_progress_bar, 0, 1)
        progress_layout.addWidget(self.secondary_progress_label, 1, 0)
        progress_layout.addWidget(self.secondary_progress_bar, 1, 1)
        # progress_layout.addStretch(1)
        self.progress_group.setLayout(progress_layout)
        self.progress_group.setMaximumWidth(410)

        self.chart: TimeChart | None = None
        self.chart_view = TimeChartView()
        self.chart_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        def make_button(text: str, clicked: typing.Callable[[], None]) -> QPushButton:
            button = QPushButton(text)
            button.setEnabled(False)
            button.clicked.connect(clicked)
            return button

        self.bump_test_all_button = make_button("Bump test all", self.bump_test_all)
        self.bump_test_button = make_button(
            "Run bump test", self.send_bump_test_command
        )
        self.kill_bump_test_button = make_button(
            "Stop bump test(s)", self.issue_command_kill_bump_test
        )

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.bump_test_all_button)
        button_layout.addWidget(self.bump_test_button)
        button_layout.addWidget(self.kill_bump_test_button)

        layout = QVBoxLayout()
        forms = QHBoxLayout()
        forms.addWidget(actuator_box)
        forms.addWidget(self.progress_group)
        forms.addWidget(LogWidget(self.m1m3))
        layout.addLayout(forms)
        layout.addWidget(self.chart_view)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.m1m3.detailedState.connect(self.detailed_state_data)
        self.m1m3.forceActuatorBumpTestStatus.connect(
            self.force_actuator_bump_test_status
        )

    def _recheck_bump_test_button(self, test_enabled: bool = True) -> None:
        detailed_state = self.m1m3.remote.evt_detailedState.get()
        if detailed_state is None or detailed_state.detailedState not in [
            MTM1M3.DetailedStates.PARKEDENGINEERING
        ]:
            self.bump_test_button.setEnabled(False)
        else:
            self.bump_test_button.setEnabled(test_enabled)

    @Slot()
    def item_selection_changed(self) -> None:
        """Called when an actuator is selected from the list."""
        items = self.actuators_table.selectedItems()
        if len(items) == 0:
            return
        if len(items) > 1:
            actuators = f"{items[0].data(Qt.UserRole)}..{items[-1].data(Qt.UserRole)}"
        else:
            actuators = f"{items[0].data(Qt.UserRole)}"

        self._recheck_bump_test_button()
        self.bump_test_button.setText(f"Run bump test for FA ID {actuators}")

    def toggledTest(self, toggled: bool) -> None:
        """Called when primary or secondary tests check box are toggled."""
        self._recheck_bump_test_button(self.actuators_table.currentItem() is not None)

    @asyncSlot()
    async def bump_test_all(self) -> None:
        for i in range(4):
            colOffset = i * 3
            self.actuators_table.setRangeSelected(
                QTableWidgetSelectionRange(
                    0,
                    1 + colOffset,
                    self.actuators_table.rowCount() - 1,
                    2 + colOffset,
                ),
                False,
            )
            self.actuators_table.setRangeSelected(
                QTableWidgetSelectionRange(
                    0, colOffset, self.actuators_table.rowCount() - 1, colOffset
                ),
                True,
            )
        await self._test_items(self.actuators_table.selectedItems())
        self.bump_test_button.setEnabled(False)

    @asyncSlot()
    async def send_bump_test_command(self) -> None:
        """Call M1M3 bump test command."""

        await self._test_items(self.actuators_table.selectedItems())

    async def _test_items(self, items: list[QTableWidgetItem]) -> None:
        fa_status = self.m1m3.remote.evt_forceActuatorBumpTestStatus.get()
        tested_fas = get_tested_fas(fa_status.primaryTest, fa_status.secondaryTest)
        test_distance = (
            self.m1m3.remote.evt_forceActuatorSettings.get().bumpTestMinimalDistance
        )

        for item in items:
            index = actuator_id_to_index(item.data(Qt.UserRole))
            if index is None:
                continue

            fa = FATable[index]
            if can_be_tested(fa, tested_fas, test_distance):
                self.actuators_table.scrollToItem(item)
                item.setSelected(False)

                await self._test_fa(fa, item.text())
                tested_fas.append(fa)

                await asyncio.sleep(0.1)

    async def _test_fa(self, fa: ForceActuatorData, axis: str) -> None:
        self.tested_id = fa.actuator_id
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

        self.progress_group.setTitle(f"Test progress {self.tested_id}")
        if self.s_index is not None:
            self.secondary_progress_label.setText("Y" if self.x_index is None else "X")

        await command(
            self,
            self.m1m3.remote.cmd_forceActuatorBumpTest,
            actuatorId=self.tested_id,
            testPrimary=not (axis == "X" or axis == "Y"),
            testSecondary=not (axis == "P") and self.s_index is not None,
        )
        self.kill_bump_test_button.setText(f"Stop bump test FA ID {self.tested_id}")

    @asyncSlot()
    async def issue_command_kill_bump_test(self) -> None:
        """Kill bump test."""
        self.actuators_table.setRangeSelected(
            QTableWidgetSelectionRange(0, 0, self.actuators_table.rowCount() - 1, 11),
            False,
        )
        await command(self, self.m1m3.remote.cmd_killForceActuatorBumpTest)

    @Slot()
    def detailed_state_data(self, data: BaseMsgType) -> None:
        """Called when detailedState event is received. Intercept to
        enable/disable form buttons."""
        if data.detailedState == MTM1M3.DetailedStates.PARKEDENGINEERING:
            self.bump_test_all_button.setEnabled(True)
            self.bump_test_button.setEnabled(
                self.actuators_table.currentItem() is not None
            )
            self.kill_bump_test_button.setEnabled(False)
            self.x_index = self.y_index = self.z_index = None
        else:
            self.bump_test_all_button.setEnabled(False)
            self.bump_test_button.setEnabled(False)
            self.kill_bump_test_button.setEnabled(False)

    @Slot()
    def appliedForces(self, data: BaseMsgType) -> None:
        """Adds applied forces to graph."""
        chart_data: list[float] = []
        if self.x_index is not None:
            chart_data.append(data.xForces[self.x_index])
        if self.y_index is not None:
            chart_data.append(data.yForces[self.y_index])
        if self.z_index is not None:
            chart_data.append(data.zForces[self.z_index])

        if self.chart is not None:
            self.chart.append(data.timestamp, chart_data, cache_index=0)

    @Slot()
    def forceActuatorData(self, data: BaseMsgType) -> None:
        """Adds measured forces to graph."""
        chart_data: list[float] = []
        if self.x_index is not None:
            chart_data.append(data.xForce[self.x_index])
        if self.y_index is not None:
            chart_data.append(data.yForce[self.y_index])
        if self.z_index is not None:
            chart_data.append(data.zForce[self.z_index])

        if self.chart is not None:
            self.chart.append(data.timestamp, chart_data, cache_index=1)

    @asyncSlot()
    async def force_actuator_bump_test_status(self, data: BaseMsgType) -> None:
        """Received when an actuator finish/start running bump tests or the
        actuator reports progress of the bump test."""

        test_progress = [
            "Unknown",
            "Not tested",
            "Triggered",
            "Testing positive",
            "Positive wait zero",
            "Testing negative",
            "Negative wait zero",
            "Passed",
            "Failed timeout",
        ]

        # test progress
        if self.z_index is not None:
            self.primary_progress_bar.setEnabled(True)
            val = data.primaryTest[self.z_index]
            self.primary_progress_bar.setFormat(
                f"ID {self.tested_id} - {test_progress[val]} - %v"
            )
            self.primary_progress_bar.setValue(min(8, val))
        else:
            self.primary_progress_bar.setEnabled(False)

        if self.s_index is not None:
            self.secondary_progress_bar.setEnabled(True)
            val = data.secondaryTest[self.s_index]
            self.secondary_progress_bar.setFormat(
                f"ID {self.tested_id} - {test_progress[val]} - %v"
            )
            self.secondary_progress_bar.setValue(min(8, val))
        else:
            self.secondary_progress_bar.setEnabled(False)

        tested_fas = get_tested_fas(data.primaryTest, data.secondaryTest)

        test_distance = (
            self.m1m3.remote.evt_forceActuatorSettings.get().bumpTestMinimalDistance
        )

        # list display
        for fa in FATable:
            actuator_id = fa.actuator_id

            row = (actuator_id % 100) - 1
            col_offset = 3 * (int(actuator_id / 100) - 1)

            def get_color(value: int) -> QColor:
                if value == MTM1M3.BumpTest.NOTTESTED:
                    return (
                        Qt.cyan
                        if can_be_tested(fa, tested_fas, test_distance)
                        else Qt.gray
                    )
                elif value == MTM1M3.BumpTest.TRIGGERED:
                    return Colors.WARNING
                elif value == MTM1M3.BumpTest.PASSED:
                    return Colors.OK
                elif value >= MTM1M3.BumpTest.FAILED_TIMEOUT:
                    return Colors.ERROR
                elif not (value == 0):
                    return Qt.magenta
                return Qt.transparent

            p_color = get_color(data.primaryTest[fa.z_index])

            self.actuators_table.item(row, col_offset + 1).setBackground(p_color)
            if fa.s_index is not None:
                s_color = get_color(data.secondaryTest[fa.s_index])
                self.actuators_table.item(row, col_offset + 2).setBackground(s_color)
                if p_color == s_color:
                    self.actuators_table.item(row, col_offset).setBackground(p_color)
            else:
                self.actuators_table.item(row, col_offset).setBackground(p_color)

        # no tests running..
        # first check that we are still in PARKEDENGINEERING
        detailed_state = self.m1m3.remote.evt_detailedState.get()
        if detailed_state is None or detailed_state.detailedState not in [
            MTM1M3.DetailedStates.PARKEDENGINEERING
        ]:
            self.bump_test_all_button.setEnabled(False)
            self.bump_test_button.setEnabled(False)
            self.kill_bump_test_button.setEnabled(False)
            return

        if len(get_tested_fas(data.primaryTest, data.secondaryTest)) == 0:
            selected = self.actuators_table.selectedItems()
            if len(selected) > 0:
                await self._test_items(selected)
            elif self._test_running:
                self.bump_test_all_button.setEnabled(True)
                self.bump_test_button.setEnabled(
                    self.actuators_table.currentItem() is not None
                    and self._any_cylinder()
                )
                self.kill_bump_test_button.setEnabled(False)
                self.x_index = self.y_index = self.z_index = None
                self.m1m3.appliedForces.disconnect(self.appliedForces)
                self.m1m3.forceActuatorData.disconnect(self.forceActuatorData)
                self._test_running = False

        elif self._test_running is False:
            self.kill_bump_test_button.setEnabled(True)
            self.m1m3.appliedForces.connect(self.appliedForces)
            self.m1m3.forceActuatorData.connect(self.forceActuatorData)
            self._test_running = True

    # helper functions. Helps correctly enable/disable Run bump test button.
    def _any_cylinder_running(self) -> bool:
        return self._test_running is True and self._any_cylinder()

    def _any_cylinder(self) -> bool:
        return len(self.actuators_table.selectedItems()) > 0
