from .CustomLabels import OnOffLabel, WarningLabel
from .SALComm import SALCommand
from .StateEnabled import EngineeringButton
from PySide2.QtWidgets import QWidget, QVBoxLayout, QFormLayout
from PySide2.QtCore import Slot
from asyncqt import asyncSlot


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

        self.anyWarningLabel = WarningLabel()
        self.commandOutputMismatchLabel = WarningLabel()
        self.commandSensorMismatchLabel = WarningLabel()

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

        warningLayout.addRow("Any Warnings", self.anyWarningLabel)
        warningLayout.addRow("Output Mismatch", self.commandOutputMismatchLabel)
        warningLayout.addRow("Sensor Mismatch", self.commandSensorMismatchLabel)

        layout.addLayout(warningLayout)
        layout.addStretch()

        self.setLayout(layout)

        self.m1m3.airSupplyWarning.connect(self.airSupplyWarning)
        self.m1m3.airSupplyStatus.connect(self.airSupplyStatus)

    @Slot(map)
    def airSupplyWarning(self, data):
        self.anyWarningLabel.setValue(data.anyWarning)
        self.commandOutputMismatchLabel.setValue(data.commandOutputMismatch)
        self.commandSensorMismatchLabel.setValue(data.commandSensorMismatch)

    @Slot(map)
    def airSupplyStatus(self, data):
        self.airCommandedOnLabel.setValue(data.airCommandedOn)
        self.airValveOpenedLabel.setValue(data.airValveOpened)
        self.airValveClosedLabel.setValue(data.airValveClosed)

        self.turnAirOnButton.setDisabled(data.airCommandedOn)
        self.turnAirOffButton.setEnabled(data.airCommandedOn)

    @asyncSlot()
    async def issueCommandTurnAirOn(self):
        await self._issueCommandTurnAirOn()

    @SALCommand
    def _issueCommandTurnAirOn(self, **kwargs):
        return self.m1m3.remote.cmd_turnAirOn

    @asyncSlot()
    async def issueCommandTurnAirOff(self):
        await self._issueCommandTurnAirOff()

    @SALCommand
    def _issueCommandTurnAirOff(self, **kwargs):
        return self.m1m3.remote.cmd_turnAirOff
