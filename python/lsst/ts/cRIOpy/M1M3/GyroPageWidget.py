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

from functools import partial

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QVBoxLayout, QWidget

from ..GUI import (
    ArrayFields,
    ArrayGrid,
    ArrayLabels,
    ArraySignal,
    DataDegC,
    UnitLabel,
    WarningGrid,
)
from ..GUI.SAL import Axis, ChartWidget


class GyroPageWidget(QWidget):
    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3

        layout = QVBoxLayout()
        layout.addWidget(
            ArrayGrid(
                "",
                [f"<b>{label}</b>" for label in "XYZ"],
                [
                    ArraySignal(
                        m1m3.gyroData,
                        [
                            ArrayFields(
                                [
                                    "angularVelocityX",
                                    "angularVelocityY",
                                    "angularVelocityZ",
                                ],
                                "<b>Angular Velocity (Deg/sec)</b>",
                                partial(UnitLabel, fmt=".03f"),
                            ),
                            ArrayLabels(""),
                            ArrayFields(
                                ["sequenceNumber", None, None], "<b>Sequence Number</b>"
                            ),
                            ArrayFields(
                                ["temperature", None, None],
                                "<b>Temperature</b>",
                                DataDegC,
                            ),
                        ],
                    ),
                ],
                Qt.Horizontal,
            )
        )

        self.maxPlotSize = 50 * 30  # 50Hz * 30s

        layout.addSpacing(20)

        layout.addWidget(
            WarningGrid(
                {
                    "anyWarning": "Any Warnings",
                    "gyroXStatusWarning": "X Status",
                    "gyroYStatusWarning": "Y Status",
                    "gyroZStatusWarning": "Z Status",
                    "sequenceNumberWarning": "Sequence number",
                    "crcMismatchWarning": "CRC mismatch",
                    "invalidLengthWarning": "Invalid length",
                    "invalidHeaderWarning": "Invalid header",
                    "incompleteFrameWarning": "Incomplete frame",
                    "v5StatusWarning": "5 V Status",
                    "v15StatusWarning": "15 V Status",
                    "gyroXSLDWarning": "X SLD",
                    "gyroXMODDACWarning": "X MOD DAC",
                    "gyroXPhaseWarning": "X Phase",
                    "gyroXFlashWarning": "X Flash",
                    "gyroXPZTTemperatureStatusWarning": "X PZT Temperature",
                    "gyroXSLDTemperatureStatusWarning": "X SLD Temperature",
                    "gyroXVoltsWarning": "X Volts",
                    "gyroAccelXStatusWarning": "Accel X",
                    "gyroAccelXTemperatureStatusWarning": "Accel X Temperature",
                    "gyroYSLDWarning": "Y SLD",
                    "gyroYMODDACWarning": "Y MOD DAC",
                    "gyroYPhaseWarning": "Y Phase",
                    "gyroYFlashWarning": "Y Flash",
                    "gyroYPZTTemperatureStatusWarning": "Y PZT Temperature",
                    "gyroYSLDTemperatureStatusWarning": "Y SLD Temperature",
                    "gyroYVoltsWarning": "Y Volts",
                    "gyroAccelYStatusWarning": "Accel Y",
                    "gyroAccelYTemperatureStatusWarning": "Accel Y Temperature",
                    "gyroZSLDWarning": "Z SLD",
                    "gyroZMODDACWarning": "Z MOD DAC",
                    "gyroZPhaseWarning": "Z Phase",
                    "gyroZFlashWarning": "Z Flash",
                    "gyroZPZTTemperatureStatusWarning": "Z PZT Temperature",
                    "gyroZSLDTemperatureStatusWarning": "Z SLD Temperature",
                    "gyroZVoltsWarning": "Z Volts",
                    "gyroAccelZStatusWarning": "Accel Z",
                    "gyroAccelZTemperatureStatusWarning": "Accel Z Temperature",
                },
                m1m3.gyroWarning,
                3,
            )
        )

        axis = Axis("Angular Velocity (rad/s)", m1m3.gyroData)
        for a in "XYZ":
            axis.addValue(f"{a}", f"angularVelocity{a}")
        layout.addWidget(ChartWidget(axis))

        self.setLayout(layout)
