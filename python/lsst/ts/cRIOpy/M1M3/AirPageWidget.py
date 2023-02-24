from PySide2.QtWidgets import QWidget, QVBoxLayout, QFormLayout
from PySide2.QtCore import Slot
from asyncqt import asyncSlot

from ..GUI.CustomLabels import OnOffLabel, WarningLabel
from ..GUI.SAL import SALCommand, EngineeringButton


class AirPageWidget(QWidget):
    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3

        layout = QVBoxLayout()

        self.turnAirOnButton = EngineeringButton("Turn Air On", m1m3)
        self.turnAirOnButton.clicked.connect(self.issueCommandTurnAirOn)
        self.turnAirOnButton.setFixedWidth(256)
        self.turnAirOffButton = EngineeringButton("Turn Air Off", m1m3)
        self.turnAirOffButton.clicked.connect(self.issueCommandTurnAirOff)
        self.turnAirOffButton.setFixedWidth(256)

        self.airCommandedOnLabel = OnOffLabel()
        self.airValveOpenedLabel = OnOffLabel()
        self.airValveClosedLabel = OnOffLabel()

        layout.addWidget(self.turnAirOnButton)
        layout.addWidget(self.turnAirOffButton)
        layout.addSpacing(20)

        dataLayout = QFormLayout()

        dataLayout.addRow("Commanded On", self.airCommandedOnLabel)
        dataLayout.addRow("Valve Opened", self.airValveOpenedLabel)
        dataLayout.addRow("Valve Closed", self.airValveClosedLabel)

        layout.addLayout(dataLayout)
        layout.addSpacing(20)

        warningLayout = QFormLayout()

        warningLayout.addRow(
            "Any Warnings", WarningLabel(m1m3.airSupplyWarning, "anyWarning")
        )
        warningLayout.addRow(
            "Output Mismatch",
            WarningLabel(m1m3.airSupplyWarning, "commandOutputMismatch"),
        )
        warningLayout.addRow(
            "Sensor Mismatch",
            WarningLabel(m1m3.airSupplyWarning, "commandSensorMismatch"),
        )

        layout.addLayout(warningLayout)
        layout.addStretch()

        self.setLayout(layout)

        self.m1m3.airSupplyStatus.connect(self.airSupplyStatus)

    @Slot(map)
    def airSupplyStatus(self, data):
        self.airCommandedOnLabel.setValue(data.airCommandedOn)
        self.airValveOpenedLabel.setValue(data.airValveOpened)
        self.airValveClosedLabel.setValue(data.airValveClosed)

        self.turnAirOnButton.setDisabled(data.airCommandedOn)
        self.turnAirOffButton.setEnabled(data.airCommandedOn)

    @asyncSlot()
    async def issueCommandTurnAirOn(self):
        await SALCommand(self, self.m1m3.remote.cmd_turnAirOn)

    @asyncSlot()
    async def issueCommandTurnAirOff(self):
        await SALCommand(self, self.m1m3.remote.cmd_turnAirOff)
