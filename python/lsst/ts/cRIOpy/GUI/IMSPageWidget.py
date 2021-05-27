from .QTHelpers import setWarningLabel
from .TimeChart import *
from .UnitsConversions import *
from .CustomLabels import Mm, Arcsec

from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout
from PySide2.QtCore import Slot


class IMSPageWidget(QWidget):
    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3

        self.layout = QVBoxLayout()
        self.dataLayout = QGridLayout()
        self.warningLayout = QGridLayout()
        self.plotLayout = QHBoxLayout()
        self.layout.addLayout(self.dataLayout)
        self.layout.addWidget(QLabel(" "))
        self.layout.addLayout(self.warningLayout)
        self.layout.addLayout(self.plotLayout)
        self.setLayout(self.layout)

        self.rawPositiveXAxialLabel = QLabel("UNKNOWN")
        self.rawPositiveXTangentLabel = QLabel("UNKNOWN")
        self.rawNegativeYAxialLabel = QLabel("UNKNOWN")
        self.rawNegativeYTangentLabel = QLabel("UNKNOWN")
        self.rawNegativeXAxialLabel = QLabel("UNKNOWN")
        self.rawNegativeXTangentLabel = QLabel("UNKNOWN")
        self.rawPositiveYAxialLabel = QLabel("UNKNOWN")
        self.rawPositiveYTangentLabel = QLabel("UNKNOWN")
        self.xPositionLabel = Mm()
        self.yPositionLabel = Mm()
        self.zPositionLabel = Mm()
        self.xRotationLabel = Arcsec()
        self.yRotationLabel = Arcsec()
        self.zRotationLabel = Arcsec()

        self.anyWarningLabel = QLabel("UNKNOWN")
        self.sensorReportsInvalidCommandLabel = QLabel("UNKNOWN")
        self.sensorReportsCommunicationTimeoutErrorLabel = QLabel("UNKNOWN")
        self.sensorReportsDataLengthErrorLabel = QLabel("UNKNOWN")
        self.sensorReportsNumberOfParametersErrorLabel = QLabel("UNKNOWN")
        self.sensorReportsParameterErrorLabel = QLabel("UNKNOWN")
        self.sensorReportsCommunicationErrorLabel = QLabel("UNKNOWN")
        self.sensorReportsIDNumberErrorLabel = QLabel("UNKNOWN")
        self.sensorReportsExpansionLineErrorLabel = QLabel("UNKNOWN")
        self.sensorReportsWriteControlErrorLabel = QLabel("UNKNOWN")
        self.responseTimeoutLabel = QLabel("UNKNOWN")
        self.invalidLengthLabel = QLabel("UNKNOWN")
        self.invalidResponseLabel = QLabel("UNKNOWN")
        self.unknownCommandLabel = QLabel("UNKNOWN")
        self.unknownProblemLabel = QLabel("UNKNOWN")

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
        self.dataLayout.addWidget(QLabel("X"), row, col + 1)
        self.dataLayout.addWidget(QLabel("Y"), row, col + 2)
        self.dataLayout.addWidget(QLabel("Z"), row, col + 3)
        row += 1
        self.dataLayout.addWidget(QLabel("Position"), row, col)
        self.dataLayout.addWidget(self.xPositionLabel, row, col + 1)
        self.dataLayout.addWidget(self.yPositionLabel, row, col + 2)
        self.dataLayout.addWidget(self.zPositionLabel, row, col + 3)
        row += 1
        self.dataLayout.addWidget(QLabel("Rotation"), row, col)
        self.dataLayout.addWidget(self.xRotationLabel, row, col + 1)
        self.dataLayout.addWidget(self.yRotationLabel, row, col + 2)
        self.dataLayout.addWidget(self.zRotationLabel, row, col + 3)
        row += 1
        self.dataLayout.addWidget(QLabel(" "), row, col)
        row += 1
        self.dataLayout.addWidget(QLabel("+X"), row, col + 1)
        self.dataLayout.addWidget(QLabel("-Y"), row, col + 2)
        self.dataLayout.addWidget(QLabel("-X"), row, col + 3)
        self.dataLayout.addWidget(QLabel("+Y"), row, col + 4)
        row += 1
        self.dataLayout.addWidget(QLabel("Axial (mm)"), row, col)
        self.dataLayout.addWidget(self.rawPositiveXAxialLabel, row, col + 1)
        self.dataLayout.addWidget(self.rawNegativeYAxialLabel, row, col + 2)
        self.dataLayout.addWidget(self.rawNegativeXAxialLabel, row, col + 3)
        self.dataLayout.addWidget(self.rawPositiveYAxialLabel, row, col + 4)
        row += 1
        self.dataLayout.addWidget(QLabel("Tangent (mm)"), row, col)
        self.dataLayout.addWidget(self.rawPositiveXTangentLabel, row, col + 1)
        self.dataLayout.addWidget(self.rawNegativeYTangentLabel, row, col + 2)
        self.dataLayout.addWidget(self.rawNegativeXTangentLabel, row, col + 3)
        self.dataLayout.addWidget(self.rawPositiveYTangentLabel, row, col + 4)

        row = 0
        col = 0
        self.warningLayout.addWidget(QLabel("Any Warnings"), row, col)
        self.warningLayout.addWidget(self.anyWarningLabel, row, col + 1)
        row += 1
        self.warningLayout.addWidget(QLabel("Sensor Invalid Command"), row, col)
        self.warningLayout.addWidget(
            self.sensorReportsInvalidCommandLabel, row, col + 1
        )
        row += 1
        self.warningLayout.addWidget(QLabel("Sensor Communication Timeout"), row, col)
        self.warningLayout.addWidget(
            self.sensorReportsCommunicationTimeoutErrorLabel, row, col + 1
        )
        row += 1
        self.warningLayout.addWidget(QLabel("Sensor Data Length Error"), row, col)
        self.warningLayout.addWidget(
            self.sensorReportsDataLengthErrorLabel, row, col + 1
        )
        row += 1
        self.warningLayout.addWidget(QLabel("Sensor Parameter Count Error"), row, col)
        self.warningLayout.addWidget(
            self.sensorReportsNumberOfParametersErrorLabel, row, col + 1
        )
        row += 1
        self.warningLayout.addWidget(QLabel("Sensor Parameter Error"), row, col)
        self.warningLayout.addWidget(
            self.sensorReportsParameterErrorLabel, row, col + 1
        )

        row = 1
        col = 2
        self.warningLayout.addWidget(QLabel("Sensor Communication Error"), row, col)
        self.warningLayout.addWidget(
            self.sensorReportsCommunicationErrorLabel, row, col + 1
        )
        row += 1
        self.warningLayout.addWidget(QLabel("Sensor ID Number Error"), row, col)
        self.warningLayout.addWidget(self.sensorReportsIDNumberErrorLabel, row, col + 1)
        row += 1
        self.warningLayout.addWidget(QLabel("Sensor Expansion Line Error"), row, col)
        self.warningLayout.addWidget(
            self.sensorReportsExpansionLineErrorLabel, row, col + 1
        )
        row += 1
        self.warningLayout.addWidget(QLabel("Sensor Write Control Error"), row, col)
        self.warningLayout.addWidget(
            self.sensorReportsWriteControlErrorLabel, row, col + 1
        )
        row += 1
        self.warningLayout.addWidget(QLabel("Response Timeout"), row, col)
        self.warningLayout.addWidget(self.responseTimeoutLabel, row, col + 1)

        row = 1
        col = 4
        self.warningLayout.addWidget(QLabel("Invalid Length"), row, col)
        self.warningLayout.addWidget(self.invalidLengthLabel, row, col + 1)
        row += 1
        self.warningLayout.addWidget(QLabel("Invalid Response"), row, col)
        self.warningLayout.addWidget(self.invalidResponseLabel, row, col + 1)
        row += 1
        self.warningLayout.addWidget(QLabel("Unknown Command"), row, col)
        self.warningLayout.addWidget(self.unknownCommandLabel, row, col + 1)
        row += 1
        self.warningLayout.addWidget(QLabel("Unknown Problem"), row, col)
        self.warningLayout.addWidget(self.unknownProblemLabel, row, col + 1)

        self.plotLayout.addWidget(self.posChartView)
        self.plotLayout.addWidget(self.rawChartView)

        self.m1m3.displacementSensorWarning.connect(self.displacementSensorWarning)
        self.m1m3.imsData.connect(self.imsData)

    @Slot(bool)
    def displacementSensorWarning(self, anyWarning):
        setWarningLabel(self.anyWarningLabel, anyWarning)
        # TODO setWarningLabel(self.sensorReportsInvalidCommandLabel, BitHelper.get(data.displacementSensorFlags, DisplacementSensorFlags.SensorReportsInvalidCommand))
        # TODO setWarningLabel(self.sensorReportsCommunicationTimeoutErrorLabel, BitHelper.get(data.displacementSensorFlags, DisplacementSensorFlags.SensorReportsCommunicationTimeoutError))
        # TODO setWarningLabel(self.sensorReportsDataLengthErrorLabel, BitHelper.get(data.displacementSensorFlags, DisplacementSensorFlags.SensorReportsDataLengthError))
        # TODO setWarningLabel(self.sensorReportsNumberOfParametersErrorLabel, BitHelper.get(data.displacementSensorFlags, DisplacementSensorFlags.SensorReportsNumberOfParametersError))
        # TODO setWarningLabel(self.sensorReportsParameterErrorLabel, BitHelper.get(data.displacementSensorFlags, DisplacementSensorFlags.SensorReportsCommunicationError))
        # TODO setWarningLabel(self.sensorReportsCommunicationErrorLabel, BitHelper.get(data.displacementSensorFlags, DisplacementSensorFlags.SensorReportsCommunicationError))
        # TODO setWarningLabel(self.sensorReportsIDNumberErrorLabel, BitHelper.get(data.displacementSensorFlags, DisplacementSensorFlags.SensorReportsIDNumberError))
        # TODO setWarningLabel(self.sensorReportsExpansionLineErrorLabel, BitHelper.get(data.displacementSensorFlags, DisplacementSensorFlags.SensorReportsExpansionLineError))
        # TODO setWarningLabel(self.sensorReportsWriteControlErrorLabel, BitHelper.get(data.displacementSensorFlags, DisplacementSensorFlags.SensorReportsWriteControlError))
        # TODO setWarningLabel(self.responseTimeoutLabel, BitHelper.get(data.displacementSensorFlags, DisplacementSensorFlags.ResponseTimeout))
        # TODO setWarningLabel(self.invalidLengthLabel, BitHelper.get(data.displacementSensorFlags, DisplacementSensorFlags.InvalidLength))
        # TODO setWarningLabel(self.invalidResponseLabel, BitHelper.get(data.displacementSensorFlags, DisplacementSensorFlags.InvalidResponse))
        # TODO setWarningLabel(self.unknownCommandLabel, BitHelper.get(data.displacementSensorFlags, DisplacementSensorFlags.UnknownCommand))
        # TODO setWarningLabel(self.unknownProblemLabel, BitHelper.get(data.displacementSensorFlags, DisplacementSensorFlags.UnknownProblem))

    @Slot(map)
    def imsData(self, data):
        self.rawPositiveXAxialLabel.setText("%0.3f" % (data.rawSensorData[0]))
        self.rawPositiveXTangentLabel.setText("%0.3f" % (data.rawSensorData[1]))
        self.rawNegativeYAxialLabel.setText("%0.3f" % (data.rawSensorData[2]))
        self.rawNegativeYTangentLabel.setText("%0.3f" % (data.rawSensorData[3]))
        self.rawNegativeXAxialLabel.setText("%0.3f" % (data.rawSensorData[4]))
        self.rawNegativeXTangentLabel.setText("%0.3f" % (data.rawSensorData[5]))
        self.rawPositiveYAxialLabel.setText("%0.3f" % (data.rawSensorData[6]))
        self.rawPositiveYTangentLabel.setText("%0.3f" % (data.rawSensorData[7]))
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
            [data.xPosition * M2MM, data.yPosition * M2MM, data.zPosition * M2MM],
            0,
        )

        self.posChart.append(
            data.timestamp,
            [
                data.xRotation * D2ARCSEC,
                data.yRotation * D2ARCSEC,
                data.zRotation * D2ARCSEC,
            ],
            1,
        )
