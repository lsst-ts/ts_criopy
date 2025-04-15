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

from lsst.ts.m1m3.utils import BumpTestKind, BumpTestRunner, ForceActuatorBumpTest
from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.enums import MTM1M3
from lsst.ts.xml.tables.m1m3 import FATable, actuator_id_to_index
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTableWidgetSelectionRange,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ...gui import Colors
from ...gui.sal import LogWidget
from ...salcomm import MetaSAL, command
from .bump_test_progress import BumpTestProgressWidget
from .force_actuator_chart import ForceChartWidget


def is_tested(state: int) -> bool:
    if state in [
        MTM1M3.BumpTest.TRIGGERED,
        MTM1M3.BumpTest.TESTINGPOSITIVE,
        MTM1M3.BumpTest.TESTINGPOSITIVEWAIT,
        MTM1M3.BumpTest.TESTINGNEGATIVE,
        MTM1M3.BumpTest.TESTINGNEGATIVEWAIT,
    ]:
        return True
    return False


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

        self._runner: BumpTestRunner | None = None

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

        self.progress_widget = BumpTestProgressWidget(self.m1m3)
        self.force_charts = ForceChartWidget()

        def make_button(text: str, clicked: typing.Callable[[], None]) -> QPushButton:
            button = QPushButton(text)
            button.setEnabled(False)
            button.clicked.connect(clicked)
            return button

        self.allow_parallel = QCheckBox("Run in parallel")

        self.bump_test_all_button = make_button("Bump test all", self.bump_test_all)
        self.bump_test_button = make_button(
            "Run bump test", self.send_bump_test_command
        )
        self.kill_bump_test_button = make_button(
            "Stop bump test(s)", self.issue_command_kill_bump_test
        )

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.allow_parallel)
        button_layout.addWidget(self.bump_test_all_button)
        button_layout.addWidget(self.bump_test_button)
        button_layout.addWidget(self.kill_bump_test_button)

        forms = QHBoxLayout()
        forms.addWidget(actuator_box)
        forms.addWidget(self.progress_widget)
        forms.addWidget(LogWidget(self.m1m3))

        layout = QVBoxLayout()
        layout.addLayout(forms)
        layout.addLayout(button_layout)
        layout.addWidget(self.force_charts)

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
        todo: list[ForceActuatorBumpTest] = []

        for item in items:
            item.setSelected(False)

            index = actuator_id_to_index(item.data(Qt.UserRole))
            if index is None:
                continue

            fa = FATable[index]

            if item.text() == "P":
                todo.append(ForceActuatorBumpTest(fa, BumpTestKind.AXIS_Z))
            elif item.text() == "X":
                todo.append(ForceActuatorBumpTest(fa, BumpTestKind.AXIS_X))
            elif item.text() == "Y":
                todo.append(ForceActuatorBumpTest(fa, BumpTestKind.AXIS_Y))
            else:
                todo.append(ForceActuatorBumpTest(fa, BumpTestKind.AXIS_Z))
                if fa.x_index is not None:
                    todo.append(ForceActuatorBumpTest(fa, BumpTestKind.AXIS_X))
                elif fa.y_index is not None:
                    todo.append(ForceActuatorBumpTest(fa, BumpTestKind.AXIS_Y))

        self._runner = BumpTestRunner(todo)

        try:
            while True:
                test = await self._runner.next(self.test_distance(), 20)
                if test is None:
                    break
                test_p = False
                test_s = False
                if test.kind in [BumpTestKind.AXIS_X, BumpTestKind.AXIS_Y]:
                    test_s = True
                else:
                    test_p = True

                (applied, measured) = self.progress_widget.add(test.actuator, test.kind)
                self.force_charts.add(test.actuator, test.kind, applied, measured)

                await command(
                    self,
                    self.m1m3.remote.cmd_forceActuatorBumpTest,
                    actuatorId=test.actuator.actuator_id,
                    testPrimary=test_p,
                    testSecondary=test_s,
                )

                self.kill_bump_test_button.setText(
                    f"Stop bump test FA ID {test.actuator.actuator_id}"
                )

            await self._runner.wait_finish(20)
            print("Passed:", self._runner.passed)
            print("Failed:", self._runner.failed)
            self._runner = None
        except TimeoutError as ex:
            print(ex)

    @asyncSlot()
    async def issue_command_kill_bump_test(self) -> None:
        """Kill bump test."""
        self.actuators_table.setRangeSelected(
            QTableWidgetSelectionRange(0, 0, self.actuators_table.rowCount() - 1, 11),
            False,
        )
        if self._runner is not None:
            self._runner.todo.clear()
        await command(self, self.m1m3.remote.cmd_killForceActuatorBumpTest)

    @Slot()
    def detailed_state_data(self, data: BaseMsgType) -> None:
        """Called when detailedState event is received. Intercept to
        enable/disable form buttons."""
        if data.detailedState == MTM1M3.DetailedStates.PARKEDENGINEERING:
            self.bump_test_all_button.setEnabled(True)
            self.bump_test_button.setEnabled(self._any_actuator())
            self.kill_bump_test_button.setEnabled(False)
        else:
            self.bump_test_all_button.setEnabled(False)
            self.bump_test_button.setEnabled(False)
            self.kill_bump_test_button.setEnabled(False)

    @asyncSlot()
    async def force_actuator_bump_test_status(self, data: BaseMsgType) -> None:
        """Received when an actuator finish/start running bump tests or the
        actuator reports progress of the bump test."""

        def remove_fa(actuator_id: int, primary: bool) -> None:
            self.progress_widget.model().remove(actuator_id, primary)
            # self.force_charts.remove(actuator_id)

        def try_remove(actuator_id: int, primary: bool) -> None:
            if self._runner is None or (
                not self._runner.running.contains(fa)
                and not self._runner.todo.contains(fa)
            ):
                asyncio.get_event_loop().call_later(
                    2, remove_fa, fa.actuator_id, primary
                )

        # list display
        for fa in FATable:
            actuator_id = fa.actuator_id

            row = (actuator_id % 100) - 1
            col_offset = 3 * (int(actuator_id / 100) - 1)

            def get_color(value: int) -> QColor:
                if value == MTM1M3.BumpTest.NOTTESTED:
                    if (
                        self._runner is not None
                        and self._runner.running.distance(fa) <= self.test_distance()
                    ):
                        return Qt.gray
                    return Qt.cyan
                elif value == MTM1M3.BumpTest.TRIGGERED:
                    return Colors.WARNING
                elif value == MTM1M3.BumpTest.PASSED:
                    return Colors.OK
                elif value >= MTM1M3.BumpTest.FAILED_TIMEOUT:
                    return Colors.ERROR
                elif not (value == 0):
                    return Qt.magenta
                return Qt.transparent

            stage = data.primaryTest[fa.z_index]
            self.progress_widget.progress(fa, True, stage)
            if not (is_tested(stage)):
                try_remove(fa.actuator_id, True)

            p_color = get_color(stage)
            self.actuators_table.item(row, col_offset + 1).setBackground(p_color)

            if fa.s_index is not None:
                stage = data.secondaryTest[fa.s_index]

                self.progress_widget.progress(fa, False, stage)

                if not (is_tested(stage)):
                    try_remove(fa.actuator_id, False)

                s_color = get_color(stage)
                self.actuators_table.item(row, col_offset + 2).setBackground(s_color)
                if p_color == s_color:
                    self.actuators_table.item(row, col_offset).setBackground(p_color)
            else:
                self.actuators_table.item(row, col_offset).setBackground(p_color)

        if self._runner is not None:
            self._runner.force_actuator_bump_test_status(data)

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

        if self._runner is not None:
            self.kill_bump_test_button.setEnabled(True)

        else:
            self.bump_test_all_button.setEnabled(True)
            self.bump_test_button.setEnabled(self._any_actuator())
            self.kill_bump_test_button.setEnabled(False)

    # helper functions. Helps correctly enable/disable Run bump test button.
    def _any_actuator(self) -> bool:
        return len(self.actuators_table.selectedItems()) > 0

    def test_distance(self) -> float:
        if not self.allow_parallel.isChecked():
            return 200
        data = self.m1m3.remote.evt_forceActuatorSettings.get()
        if data is None:
            return 10
        return data.bumpTestMinimalDistance
