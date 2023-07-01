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
    ArrayGrid,
    ArrayItem,
    ArraySignal,
    DegS2,
    MSec2,
    ValueGrid,
    Volt,
    WarningGrid,
)
from ..GUI.SAL import Axis, ChartWidget
from ..salcomm import MetaSAL


class DCAccelerometerPageWidget(QWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(
            ValueGrid(
                partial(DegS2, fmt=".04f"),
                {
                    "angularAccelerationX": "<b>X</b>",
                    "angularAccelerationY": "<b>Y</b>",
                    "angularAccelerationZ": "<b>Z</b>",
                },
                m1m3.accelerometerData,
                3,
            )
        )

        layout.addWidget(
            ArrayGrid(
                "<b>Accelerometer</b>",
                [
                    "<b>1X</b>",
                    "<b>1Y</b>",
                    "<b>2X</b>",
                    "<b>2Y</b>",
                    "<b>3X</b>",
                    "<b>3Y</b>",
                    "<b>4X</b>",
                    "<b>4Y</b>",
                ],
                [
                    ArraySignal(
                        m1m3.accelerometerData,
                        [
                            ArrayItem("rawAccelerometer", "<b>Raw</b>", Volt),
                            ArrayItem("accelerometer", "<b>Acceleration</b>", MSec2),
                        ],
                    )
                ],
                Qt.Horizontal,
            )
        )

        layout.addWidget(
            WarningGrid(
                {
                    "anyWarning": "Any Warnings",
                    "responseTimeout": "Response Timeout",
                },
                m1m3.accelerometerWarning,
                2,
            )
        )

        axis = Axis("Angular Acceleration (rad/s<sup>2</sup>)", m1m3.accelerometerData)
        axis.addValues(
            {
                "X": "angularAccelerationX",
                "Y": "angularAccelerationY",
                "Z": "angularAccelerationZ",
            }
        )

        layout.addWidget(ChartWidget(axis))

        self.setLayout(layout)
