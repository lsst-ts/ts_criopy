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

    def __init__(
        self,
        fa: ForceActuatorData,
        cylinders: bool,
        test_primary: bool,
        test_secondary: bool,
    ):
        super().__init__(f"Actuator {fa.actuator_id}")

        def progress_bar() -> QProgressBar:
            bar = QProgressBar()
            bar.setMaximum(MTM1M3.BumpTest.FAILED_TIMEOUT)
            return bar

        self.primary: None | QProgressBar = None
        self.secondary: None | QProgressBar = None

        progress_layout = QGridLayout()

        if test_primary:
            primary_label = QLabel(
                f"Primary cylinder {fa.actuator_id} - {fa.z_index}"
                if cylinders
                else f"Z {fa.actuator_id} - {fa.z_index}"
            )
            progress_layout.addWidget(primary_label, 0, 0)

            self.primary = progress_bar()
            progress_layout.addWidget(self.primary, 0, 1)

        if test_secondary:
            if cylinders:
                secondary_label = QLabel(
                    f"Secondary cylinder {fa.actuator_id} - {fa.s_index} ({fa.z_index})"
                )
            else:
                if fa.x_index is not None:
                    secondary_label = QLabel(
                        f"X {fa.actuator_id} - {fa.x_index} ({fa.z_index})"
                    )
                else:
                    secondary_label = QLabel(
                        f"Y {fa.actuator_id} - {fa.y_index} ({fa.z_index})"
                    )

            progress_layout.addWidget(secondary_label, 1, 0)

            self.secondary = progress_bar()
            progress_layout.addWidget(self.secondary, 1, 1)

        self.setLayout(progress_layout)
        self.setMaximumWidth(410)

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

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.tests = {}

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
        progress = ActuatorBumpTestProgressBox(
            fa, cylinders, primary_test, secondary_test
        )
        layout = self.layout()
        layout.insertWidget(layout.count() - 1, progress)
        self.tests[fa.actuator_id] = progress

    def remove(self, fa: ForceActuatorData) -> None:
        if fa.actuator_id in self.tests:
            self.layout().removeWidget(self.tests[fa.actuator_id])
            self.tests[fa.actuator_id].hide()
            del self.tests[fa.actuator_id]

    def primary_progress(self, fa: ForceActuatorData, state: int) -> None:
        self.tests[fa.actuator_id].primary_progress(state)

    def secondary_progress(self, fa: ForceActuatorData, state: int) -> None:
        self.tests[fa.actuator_id].secondary_progress(state)
