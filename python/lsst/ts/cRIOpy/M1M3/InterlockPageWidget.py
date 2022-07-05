from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.QtCore import Slot

from ..GUI import InterlockOffGrid, PowerOnOffGrid, TimeChart, TimeChartView


class InterlockPageWidget(QWidget):
    def __init__(self, m1m3):
        super().__init__()

        layout = QVBoxLayout()
        layout.addWidget(
            PowerOnOffGrid(
                {
                    "heartbeatCommandedState": "Controller to Interlock Heartbeat",
                    "heartbeatOutputState": "Interlock heartbeat state",
                },
                m1m3.interlockStatus,
                1,
            )
        )
        layout.addSpacing(20)
        layout.addWidget(
            InterlockOffGrid(
                {
                    "auxPowerNetworksOff": "AUX Power Networks",
                    "thermalEquipmentOff": "Thermal Equipment",
                    "airSupplyOff": "Air Supply",
                    "tmaMotionStop": "TMA Motion Stop",
                    "gisHeartbeatLost": "GIS Heartbeat Lost",
                    "cabinetDoorOpen": "Cabinet Door Open",
                },
                m1m3.interlockWarning,
                2,
            )
        )

        self.chart = TimeChart({"Heartbeats": ["Commanded State", "Interlock State"]})
        layout.addWidget(TimeChartView(self.chart))

        self.setLayout(layout)

        m1m3.interlockStatus.connect(self.interlockStatus)

    @Slot(map)
    def interlockStatus(self, data):
        self.chart.append(
            data.timestamp,
            [
                data.heartbeatCommandedState,
                data.heartbeatOutputState,
            ],
        )
