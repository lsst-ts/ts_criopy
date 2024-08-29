# This file is part of cRIO UIs.
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


import astropy.units as u
from lsst.ts.salobj import BaseMsgType
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QWidget

from ..gui import (
    Arcsec,
    ArrayFields,
    ArrayGrid,
    ArrayItem,
    ArrayLabels,
    ArraySignal,
    Mm,
    TimeChart,
    TimeChartView,
    WarningGrid,
)
from ..salcomm import MetaSAL


class IMSPageWidget(QWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()

        layout = QVBoxLayout()

        dataLayout = QGridLayout()
        plotLayout = QHBoxLayout()

        layout.addWidget(
            ArrayGrid(
                "",
                [f"<b>{label}</b>" for label in "XYZ"],
                [
                    ArraySignal(
                        m1m3.imsData,
                        [
                            ArrayFields(
                                ["xPosition", "yPosition", "zPosition"],
                                "<b>Position</b>",
                                Mm,
                            ),
                            ArrayFields(
                                ["xRotation", "yRotation", "zRotation"],
                                "<b>Rotation</b>",
                                Arcsec,
                            ),
                            ArrayLabels(""),
                            ArrayLabels(
                                "<b>+X</b>",
                                "<b>-Y</b>",
                                "<b>-X</b>",
                                "<b>+Y</b>",
                            ),
                            ArrayItem(
                                "rawSensorData",
                                "<b>Axial</b>",
                                Mm,
                                indices=[0, 2, 4, 6],
                            ),
                            ArrayItem(
                                "rawSensorData",
                                "<b>Tangent</b>",
                                Mm,
                                indices=[1, 3, 5, 7],
                            ),
                        ],
                    )
                ],
                Qt.Horizontal,
            )
        )

        self.rawChart = TimeChart(
            {
                "Displacement (mm)": [
                    "+X Axial",
                    "+X Tangent",
                    "+Y Axial",
                    "+Y Tangent",
                    "-X Axial",
                    "-X Tangent",
                    "-Y Axial",
                    "-Y Tangent",
                ]
            },
            50 * 5,
        )
        self.rawChartView = TimeChartView(self.rawChart)

        self.posChart = TimeChart(
            {
                "Position (mm)": ["Pos X", "Pos Y", "Pos Z"],
                "Rotation (arcsec)": ["Rot X", "Rot Y", "Rot Z"],
            },
            50 * 5,
        )
        self.posChartView = TimeChartView(self.posChart)

        plotLayout.addWidget(self.posChartView)
        plotLayout.addWidget(self.rawChartView)

        layout.addLayout(dataLayout)
        layout.addSpacing(20)
        layout.addWidget(
            WarningGrid(
                {
                    "anyWarning": "Any Warnings",
                    "sensorReportsInvalidCommand": "Sensor Invalid Command",
                    "sensorReportsCommunicationTimeoutError": (
                        "Sensor Communication Timeout"
                    ),
                    "sensorReportsDataLengthError": "Sensor Data Length",
                    "sensorReportsNumberOfParametersError": (
                        "Sensor Number of Parameters"
                    ),
                    "sensorReportsParameterError": "Sensor Parameter",
                    "sensorReportsCommunicationError": ("Sensor Communication Error"),
                    "sensorReportsIDNumberErrorLabel": "Sensor ID Number",
                    "sensorReportsExpansionLineError": "Sensor Expansion Line",
                    "sensorReportsWriteControlError": "Sensor Write Control",
                    "responseTimeout": "Response Timeout",
                    "invalidLength": "Invalid Length",
                    "invalidResponse": "Invalid Response",
                    "unknownCommand": "Unknown Command",
                    "unknownProblem": "Unknown Problem",
                },
                m1m3.displacementSensorWarning,
                3,
            )
        )

        layout.addLayout(plotLayout)
        self.setLayout(layout)

        m1m3.imsData.connect(self.imsData)

    @Slot()
    def imsData(self, data: BaseMsgType) -> None:
        self.rawChart.append(
            data.timestamp,
            [
                data.rawSensorData[0],
                data.rawSensorData[1],
                data.rawSensorData[2],
                data.rawSensorData[3],
                data.rawSensorData[4],
                data.rawSensorData[5],
                data.rawSensorData[6],
                data.rawSensorData[7],
            ],
        )

        self.posChart.append(
            data.timestamp,
            [
                data.xPosition * u.m.to(u.mm),
                data.yPosition * u.m.to(u.mm),
                data.zPosition * u.m.to(u.mm),
            ],
            0,
        )

        self.posChart.append(
            data.timestamp,
            [
                data.xRotation * u.deg.to(u.arcsec),
                data.yRotation * u.deg.to(u.arcsec),
                data.zRotation * u.deg.to(u.arcsec),
            ],
            1,
        )
