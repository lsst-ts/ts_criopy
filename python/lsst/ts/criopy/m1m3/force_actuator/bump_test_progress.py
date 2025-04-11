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

from lsst.ts.xml.enums import MTM1M3
from lsst.ts.xml.tables.m1m3 import ForceActuatorData
from PySide6.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


class ActuatorBumpTestProgressBox(QGroupBox):
    TEST_PROGRESS = [
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

    test_count = 0

    def __init__(
        self,
        fa: ForceActuatorData,
        cylinders: bool,
        test_primary: bool,
        test_secondary: bool,
    ):
        super().__init__(f"Actuator {fa.actuator_id}")

        self.primary: None | QProgressBar = None
        self.secondary: None | QProgressBar = None

        self.setLayout(QGridLayout())

        self.append(fa, cylinders, test_primary, test_secondary)

        self.setMaximumWidth(410)

    def append(
        self,
        fa: ForceActuatorData,
        cylinders: bool,
        test_primary: bool,
        test_secondary: bool,
    ) -> None:
        layout = self.layout()

        def progress_bar(label: str) -> QProgressBar:
            layout.addWidget(QLabel(label), self.test_count, 0)
            bar = QProgressBar()
            bar.setMaximum(MTM1M3.BumpTest.FAILED_TIMEOUT)
            layout.addWidget(bar, self.test_count, 1)
            self.test_count += 1
            return bar

        if test_primary:
            primary_label = (
                f"Primary cylinder {fa.actuator_id} - {fa.z_index}"
                if cylinders
                else f"Z {fa.actuator_id} - {fa.z_index}"
            )
            self.primary = progress_bar(primary_label)

        if test_secondary:
            if cylinders:
                secondary_label = (
                    f"Secondary cylinder {fa.actuator_id} - {fa.s_index} ({fa.z_index})"
                )
            else:
                if fa.x_index is not None:
                    secondary_label = (
                        f"X {fa.actuator_id} - {fa.x_index} ({fa.z_index})"
                    )
                else:
                    secondary_label = (
                        f"Y {fa.actuator_id} - {fa.y_index} ({fa.z_index})"
                    )

            self.secondary = progress_bar(secondary_label)

    def primary_progress(self, state: int) -> None:
        assert self.primary is not None
        reported = min(state, MTM1M3.BumpTest.FAILED_TIMEOUT)
        self.primary.setValue(reported)
        self.primary.setFormat(f"{self.TEST_PROGRESS[reported]} - %v")

    def secondary_progress(self, state: int) -> None:
        assert self.secondary is not None
        reported = min(state, MTM1M3.BumpTest.FAILED_TIMEOUT)
        self.secondary.setValue(reported)
        self.secondary.setFormat(f"{self.TEST_PROGRESS[reported]} - %v")


class BumpTestProgressWidget(QWidget):
    """Holds all tests currenlly in progress."""

    tests: dict[int, ActuatorBumpTestProgressBox] = {}

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.setMinimumWidth(200)
        self.setMaximumWidth(420)

        layout.addStretch(1)
        self.setLayout(layout)

    def add(
        self,
        fa: ForceActuatorData,
        cylinders: bool,
        primary_test: bool,
        secondary_test: bool,
    ) -> None:
        if fa.actuator_id in self.tests:
            self.tests[fa.actuator_id].append(
                fa, cylinders, primary_test, secondary_test
            )
            return

        progress = ActuatorBumpTestProgressBox(
            fa, cylinders, primary_test, secondary_test
        )
        layout = self.layout()
        layout.insertWidget(layout.count() - 1, progress)
        self.tests[fa.actuator_id] = progress

    def _remove(self, actuator_id: int) -> None:
        pb = self.tests[actuator_id]
        self.layout().removeWidget(pb)
        pb.hide()
        del self.tests[actuator_id]

    def remove(self, actuator_id: int) -> None:
        if actuator_id in self.tests.keys():
            if self.tests[actuator_id].test_count > 1:
                self.tests[actuator_id].test_count -= 1
                return
            self._remove(actuator_id)

    def clear(self) -> None:
        """Remove all actuators progress boxes."""
        map(self._remove, self.tests.keys())

    def primary_progress(self, fa: ForceActuatorData, state: int) -> None:
        self.tests[fa.actuator_id].primary_progress(state)

    def secondary_progress(self, fa: ForceActuatorData, state: int) -> None:
        self.tests[fa.actuator_id].secondary_progress(state)
