from PySide2.QtCore import Slot
from PySide2.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from ..GUI import TimeChart, TimeChartView, WarningGrid


class GyroPageWidget(QWidget):
    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3

        dataLayout = QGridLayout()
        plotLayout = QVBoxLayout()

        self.maxPlotSize = 50 * 30  # 50Hz * 30s

        self.velocityXLabel = QLabel("UNKNOWN")
        self.velocityYLabel = QLabel("UNKNOWN")
        self.velocityZLabel = QLabel("UNKNOWN")
        self.sequenceNumberLabel = QLabel("UNKNOWN")
        self.temperatureLabel = QLabel("UNKNOWN")

        self.chart = TimeChart({"Angular Velocity (rad/s)": ["X", "y", "Z"]})
        self.chart_view = TimeChartView(self.chart)

        row = 0
        col = 0
        dataLayout.addWidget(QLabel("X"), row, col + 1)
        dataLayout.addWidget(QLabel("Y"), row, col + 2)
        dataLayout.addWidget(QLabel("Z"), row, col + 3)
        row += 1
        dataLayout.addWidget(QLabel("Angular Velocity (rad/s)"), row, col)
        dataLayout.addWidget(self.velocityXLabel, row, col + 1)
        dataLayout.addWidget(self.velocityYLabel, row, col + 2)
        dataLayout.addWidget(self.velocityZLabel, row, col + 3)
        row += 1
        dataLayout.addWidget(QLabel(" "), row, col)
        row += 1
        dataLayout.addWidget(QLabel("Sequence Number"), row, col)
        dataLayout.addWidget(self.sequenceNumberLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Temperature (C)"), row, col)
        dataLayout.addWidget(self.temperatureLabel, row, col + 1)

        plotLayout.addWidget(self.chart_view)

        layout = QVBoxLayout()
        layout.addLayout(dataLayout)
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
        layout.addLayout(plotLayout)
        self.setLayout(layout)

        self.m1m3.gyroData.connect(self.gyroData)

    @Slot(map)
    def gyroData(self, data):
        self.velocityXLabel.setText("%0.3f" % (data.angularVelocityX))
        self.velocityYLabel.setText("%0.3f" % (data.angularVelocityY))
        self.velocityZLabel.setText("%0.3f" % (data.angularVelocityZ))
        self.sequenceNumberLabel.setText("%0.3f" % (data.sequenceNumber))
        self.temperatureLabel.setText("%0.3f" % (data.temperature))

        self.chart.append(
            data.timestamp,
            [data.angularVelocityX, data.angularVelocityY, data.angularVelocityZ],
        )
