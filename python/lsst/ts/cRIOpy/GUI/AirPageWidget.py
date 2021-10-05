from .QTHelpers import setWarningLabel, setBoolLabelHighLow, setBoolLabelOnOff
from .SALComm import SALCommand
from .StateEnabled import EngineeringButton
from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout
from PySide2.QtCore import Slot
from asyncqt import asyncSlot


class AirPageWidget(QWidget):
    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3

        self.layout = QVBoxLayout()
        self.dataLayout = QGridLayout()
        self.warningLayout = QGridLayout()
        self.commandLayout = QVBoxLayout()
        self.layout.addLayout(self.commandLayout)
        self.layout.addWidget(QLabel(" "))
        self.layout.addLayout(self.dataLayout)
        self.layout.addWidget(QLabel(" "))
        self.layout.addLayout(self.warningLayout)
        self.setLayout(self.layout)
        self.setFixedHeight(300)

        self.turnAirOnButton = EngineeringButton("Turn Air On", m1m3)
        self.turnAirOnButton.clicked.connect(self.issueCommandTurnAirOn)
        self.turnAirOnButton.setFixedWidth(256)
        self.turnAirOffButton = EngineeringButton("Turn Air Off", m1m3)
        self.turnAirOffButton.clicked.connect(self.issueCommandTurnAirOff)
        self.turnAirOffButton.setFixedWidth(256)

        self.airCommandedOnLabel = QLabel("UNKNOWN")
        self.airValveOpenedLabel = QLabel("UNKNOWN")
        self.airValveClosedLabel = QLabel("UNKNOWN")

        self.anyWarningLabel = QLabel("UNKNOWN")
        self.airValveSensorMismatch = QLabel("UNKNOWN")

        self.commandLayout.addWidget(self.turnAirOnButton)
        self.commandLayout.addWidget(self.turnAirOffButton)

        row = 0
        col = 0
        self.dataLayout.addWidget(QLabel("Commanded On"), row, col)
        self.dataLayout.addWidget(self.airCommandedOnLabel, row, col + 1)
        row += 1
        self.dataLayout.addWidget(QLabel("Valve Opened"), row, col)
        self.dataLayout.addWidget(self.airValveOpenedLabel, row, col + 1)
        row += 1
        self.dataLayout.addWidget(QLabel("Valve Closed"), row, col)
        self.dataLayout.addWidget(self.airValveClosedLabel, row, col + 1)

        row = 0
        col = 0
        self.warningLayout.addWidget(QLabel("Any Warnings"), row, col)
        self.warningLayout.addWidget(self.anyWarningLabel, row, col + 1)
        row += 1
        self.warningLayout.addWidget(QLabel("Command / Sensor Mismatch"), row, col)
        self.warningLayout.addWidget(self.airValveSensorMismatch, row, col + 1)

        self.m1m3.airSupplyWarning.connect(self.airSupplyWarning)
        self.m1m3.airSupplyStatus.connect(self.airSupplyStatus)

    @Slot(map)
    def airSupplyWarning(self, data):
        setWarningLabel(self.anyWarningLabel, data.anyWarning)
        # TODO setWarningLabel(self.airValveSensorMismatch, BitHelper.get(data.airSupplyFlags, AirSupplyFlags.AirValveSensorMismatch))

    @Slot(map)
    def airSupplyStatus(self, data):
        setBoolLabelOnOff(self.airCommandedOnLabel, data.airCommandedOn)
        setBoolLabelHighLow(self.airValveOpenedLabel, data.airValveOpened)
        setBoolLabelHighLow(self.airValveClosedLabel, data.airValveClosed)

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
