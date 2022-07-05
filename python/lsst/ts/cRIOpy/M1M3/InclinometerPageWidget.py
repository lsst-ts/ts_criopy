from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout
from PySide2.QtCore import Slot

from ..GUI import TimeChart, TimeChartView, WarningGrid


class InclinometerPageWidget(QWidget):
    def __init__(self, m1m3):
        super().__init__()

        dataLayout = QGridLayout()

        self.angleLabel = QLabel("UNKNOWN")

        self.chart = TimeChart({"Angle (deg)": ["Inclinometer Angle"]})

        row = 0
        col = 0
        dataLayout.addWidget(QLabel("Angle (deg)"), row, col)
        dataLayout.addWidget(self.angleLabel, row, col + 1)

        layout = QVBoxLayout()
        layout.addLayout(dataLayout)
        layout.addSpacing(20)
        layout.addWidget(
            WarningGrid(
                {
                    "anyWarning": "Any Warnings",
                    "sensorReportsIllegalFunctionLabel": "Sensor Illegal Function",
                    "sensorReportsIllegalAddressLabel": "Sensor Illegal Address",
                    "responseTimeout": "Reponse Timeout",
                    "invalidCRC": "Invalid CRC",
                    "invalidLength": "Invalid Length",
                    "unknownAddress": "Unknown Address",
                    "unknownFunction": "Unknown Function",
                    "unknownProblem": "Unknown Problem",
                },
                m1m3.inclinometerSensorWarning,
                2,
            )
        )

        layout.addWidget(TimeChartView(self.chart))

        self.setLayout(layout)

        m1m3.inclinometerData.connect(self.inclinometerData)

    @Slot(map)
    def inclinometerData(self, data):
        self.angleLabel.setText("%0.3f" % (data.inclinometerAngle))

        self.chart.append(data.timestamp, [data.inclinometerAngle])
