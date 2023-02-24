from PySide2.QtWidgets import QWidget, QVBoxLayout, QFormLayout
from PySide2.QtCore import Slot
from asyncqt import asyncSlot

from ..GUI.CustomLabels import OnOffLabel, WarningLabel
from ..GUI.SAL import SALCommand, EngineeringButton


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

        layout.addWidget(self.turnLightsOnButton)
        layout.addWidget(self.turnLightsOffButton)

        layout.addSpacing(20)

        dataLayout = QFormLayout()
        dataLayout.addRow("Command", self.cellLightsCommandedOnLabel)
        dataLayout.addRow("Sensor", self.cellLightsOnLabel)

        layout.addLayout(dataLayout)
        layout.addSpacing(20)

        warningLayout = QFormLayout()

        warningLayout.addRow(
            "Any Warnings", WarningLabel(m1m3.cellLightWarning, "anyWarning")
        )
        warningLayout.addRow(
            "Output Mismatch",
            WarningLabel(m1m3.cellLightWarning, "cellLightsOutputMismatch"),
        )
        warningLayout.addRow(
            "Sensor Mismatch",
            WarningLabel(m1m3.cellLightWarning, "cellLightsSensorMismatch"),
        )

        layout.addLayout(warningLayout)
        layout.addStretch()

        self.setLayout(layout)

        self.m1m3.cellLightStatus.connect(self.cellLightStatus)

    @Slot(map)
    def cellLightStatus(self, data):
        self.cellLightsCommandedOnLabel.setValue(data.cellLightsCommandedOn)
        self.cellLightsOnLabel.setValue(data.cellLightsOn)

        self.turnLightsOnButton.setDisabled(data.cellLightsCommandedOn)
        self.turnLightsOffButton.setEnabled(data.cellLightsCommandedOn)

    @asyncSlot()
    async def issueCommandTurnLightsOn(self):
        await SALCommand(self, self.m1m3.remote.cmd_turnLightsOn)

    @asyncSlot()
    async def issueCommandTurnLightsOff(self):
        await SALCommand(self, self.m1m3.remote.cmd_turnLightsOff)
