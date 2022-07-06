import astropy.units as u

from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout
from PySide2.QtCore import Slot

from ..GUI import Mm, Arcsec, TimeChart, TimeChartView, WarningGrid


class IMSPageWidget(QWidget):
    def __init__(self, m1m3):
        super().__init__()

        dataLayout = QGridLayout()
        plotLayout = QHBoxLayout()

        self.rawPositiveXAxialLabel = Mm()
        self.rawPositiveXTangentLabel = Mm()
        self.rawNegativeYAxialLabel = Mm()
        self.rawNegativeYTangentLabel = Mm()
        self.rawNegativeXAxialLabel = Mm()
        self.rawNegativeXTangentLabel = Mm()
        self.rawPositiveYAxialLabel = Mm()
        self.rawPositiveYTangentLabel = Mm()
        self.xPositionLabel = Mm()
        self.yPositionLabel = Mm()
        self.zPositionLabel = Mm()
        self.xRotationLabel = Arcsec()
        self.yRotationLabel = Arcsec()
        self.zRotationLabel = Arcsec()

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

        row = 0
        col = 0
        dataLayout.addWidget(QLabel("X"), row, col + 1)
        dataLayout.addWidget(QLabel("Y"), row, col + 2)
        dataLayout.addWidget(QLabel("Z"), row, col + 3)
        row += 1
        dataLayout.addWidget(QLabel("Position"), row, col)
        dataLayout.addWidget(self.xPositionLabel, row, col + 1)
        dataLayout.addWidget(self.yPositionLabel, row, col + 2)
        dataLayout.addWidget(self.zPositionLabel, row, col + 3)
        row += 1
        dataLayout.addWidget(QLabel("Rotation"), row, col)
        dataLayout.addWidget(self.xRotationLabel, row, col + 1)
        dataLayout.addWidget(self.yRotationLabel, row, col + 2)
        dataLayout.addWidget(self.zRotationLabel, row, col + 3)
        row += 1
        dataLayout.addWidget(QLabel(" "), row, col)
        row += 1
        dataLayout.addWidget(QLabel("+X"), row, col + 1)
        dataLayout.addWidget(QLabel("-Y"), row, col + 2)
        dataLayout.addWidget(QLabel("-X"), row, col + 3)
        dataLayout.addWidget(QLabel("+Y"), row, col + 4)
        row += 1
        dataLayout.addWidget(QLabel("Axial (mm)"), row, col)
        dataLayout.addWidget(self.rawPositiveXAxialLabel, row, col + 1)
        dataLayout.addWidget(self.rawNegativeYAxialLabel, row, col + 2)
        dataLayout.addWidget(self.rawNegativeXAxialLabel, row, col + 3)
        dataLayout.addWidget(self.rawPositiveYAxialLabel, row, col + 4)
        row += 1
        dataLayout.addWidget(QLabel("Tangent (mm)"), row, col)
        dataLayout.addWidget(self.rawPositiveXTangentLabel, row, col + 1)
        dataLayout.addWidget(self.rawNegativeYTangentLabel, row, col + 2)
        dataLayout.addWidget(self.rawNegativeXTangentLabel, row, col + 3)
        dataLayout.addWidget(self.rawPositiveYTangentLabel, row, col + 4)

        plotLayout.addWidget(self.posChartView)
        plotLayout.addWidget(self.rawChartView)

        layout = QVBoxLayout()
        layout.addLayout(dataLayout)
        layout.addSpacing(20)
        layout.addWidget(
            WarningGrid(
                {
                    "anyWarning": "Any Warnings",
                    "sensorReportsInvalidCommand": "Sensor Invalid Command",
                    "sensorReportsCommunicationTimeoutError": "Sensor Communication Timeout",
                    "sensorReportsDataLengthError": "Sensor Data Length",
                    "sensorReportsNumberOfParametersError": "Sensor Number of Parameters",
                    "sensorReportsParameterError": "Sensor Parameter",
                    "sensorReportsCommunicationError": "Sensor Communication Error",
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

    @Slot(map)
    def imsData(self, data):
        self.rawPositiveXAxialLabel.setValue(data.rawSensorData[0])
        self.rawPositiveXTangentLabel.setValue(data.rawSensorData[1])
        self.rawNegativeYAxialLabel.setValue(data.rawSensorData[2])
        self.rawNegativeYTangentLabel.setValue(data.rawSensorData[3])
        self.rawNegativeXAxialLabel.setValue(data.rawSensorData[4])
        self.rawNegativeXTangentLabel.setValue(data.rawSensorData[5])
        self.rawPositiveYAxialLabel.setValue(data.rawSensorData[6])
        self.rawPositiveYTangentLabel.setValue(data.rawSensorData[7])
        self.xPositionLabel.setValue(data.xPosition)
        self.yPositionLabel.setValue(data.yPosition)
        self.zPositionLabel.setValue(data.zPosition)
        self.xRotationLabel.setValue(data.xRotation)
        self.yRotationLabel.setValue(data.yRotation)
        self.zRotationLabel.setValue(data.zRotation)

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
