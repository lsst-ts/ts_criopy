from .CustomLabels import OnOffLabel, WarningLabel
from .SALComm import SALCommand
from .StateEnabled import EngineeringButton

from PySide2.QtWidgets import QWidget, QVBoxLayout, QFormLayout
from PySide2.QtCore import Slot
from asyncqt import asyncSlot


class CellLightPageWidget(QWidget):
    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3

        layout = QVBoxLayout()

        self.turnLightsOnButton = EngineeringButton("Turn Lights On", m1m3)
        self.turnLightsOnButton.clicked.connect(self.issueCommandTurnLightsOn)
        self.turnLightsOnButton.setFixedWidth(256)
        self.turnLightsOffButton = EngineeringButton("Turn Lights Off", m1m3)
        self.turnLightsOffButton.clicked.connect(self.issueCommandTurnLightsOff)
        self.turnLightsOffButton.setFixedWidth(256)

        self.cellLightsCommandedOnLabel = OnOffLabel()
        self.cellLightsOnLabel = OnOffLabel()

        self.anyWarningLabel = WarningLabel()
        self.cellLightsOutputMismatchLabel = WarningLabel()
        self.cellLightsSensorMismatchLabel = WarningLabel()

        layout.addWidget(self.turnLightsOnButton)
        layout.addWidget(self.turnLightsOffButton)

        layout.addSpacing(20)

        dataLayout = QFormLayout()
        dataLayout.addRow("Command", self.cellLightsCommandedOnLabel)
        dataLayout.addRow("Sensor", self.cellLightsOnLabel)

        layout.addLayout(dataLayout)
        layout.addSpacing(20)

        warningLayout = QFormLayout()

        warningLayout.addRow("Any Warnings", self.anyWarningLabel)
        warningLayout.addRow("Output Mismatch", self.cellLightsOutputMismatchLabel)
        warningLayout.addRow("Sensor Mismatch", self.cellLightsSensorMismatchLabel)

        layout.addLayout(warningLayout)
        layout.addStretch()

        self.setLayout(layout)

        self.m1m3.cellLightWarning.connect(self.cellLightWarning)
        self.m1m3.cellLightStatus.connect(self.cellLightStatus)

    @Slot(map)
    def cellLightWarning(self, data):
        self.anyWarningLabel.setValue(data.anyWarning)
        self.cellLightsOutputMismatchLabel.setValue(data.cellLightsOutputMismatch)
        self.cellLightsSensorMismatchLabel.setValue(data.cellLightsSensorMismatch)

    @Slot(map)
    def cellLightStatus(self, data):
        self.cellLightsCommandedOnLabel.setValue(data.cellLightsCommandedOn)
        self.cellLightsOnLabel.setValue(data.cellLightsOn)

        self.turnLightsOnButton.setDisabled(data.cellLightsCommandedOn)
        self.turnLightsOffButton.setEnabled(data.cellLightsCommandedOn)

    @asyncSlot()
    async def issueCommandTurnLightsOn(self):
        await self._issueCommandTurnLightsOn()

    @SALCommand
    def _issueCommandTurnLightsOn(self, **kwargs):
        return self.m1m3.remote.cmd_turnLightsOn

    @asyncSlot()
    async def issueCommandTurnLightsOff(self):
        await self._issueCommandTurnLightsOff()

    @SALCommand
    def _issueCommandTurnLightsOff(self, **kwargs):
        return self.m1m3.remote.cmd_turnLightsOff
