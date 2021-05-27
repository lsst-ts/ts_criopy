from .QTHelpers import setWarningLabel, setBoolLabelOnOff
from .SALComm import SALCommand

from PySide2.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout
from PySide2.QtCore import Slot
from asyncqt import asyncSlot


class CellLightPageWidget(QWidget):
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

        self.turnLightsOnButton = QPushButton("Turn Lights On")
        self.turnLightsOnButton.clicked.connect(self.issueCommandTurnLightsOn)
        self.turnLightsOnButton.setFixedWidth(256)
        self.turnLightsOffButton = QPushButton("Turn Lights Off")
        self.turnLightsOffButton.clicked.connect(self.issueCommandTurnLightsOff)
        self.turnLightsOffButton.setFixedWidth(256)

        self.cellLightsCommandedOnLabel = QLabel("UNKNOWN")
        self.cellLightsOnLabel = QLabel("UNKNOWN")

        self.anyWarningLabel = QLabel("UNKNOWN")
        self.cellLightSensorMismatchLabel = QLabel("UNKNOWN")

        self.commandLayout.addWidget(self.turnLightsOnButton)
        self.commandLayout.addWidget(self.turnLightsOffButton)

        row = 0
        col = 0
        self.dataLayout.addWidget(QLabel("Command"), row, col)
        self.dataLayout.addWidget(self.cellLightsCommandedOnLabel, row, col + 1)
        row += 1
        self.dataLayout.addWidget(QLabel("Sensor"), row, col)
        self.dataLayout.addWidget(self.cellLightsOnLabel, row, col + 1)

        row = 0
        col = 0
        self.warningLayout.addWidget(QLabel("Any Warnings"), row, col)
        self.warningLayout.addWidget(self.anyWarningLabel, row, col + 1)
        row += 1
        self.warningLayout.addWidget(QLabel("Command / Sensor Mismatch"), row, col)
        self.warningLayout.addWidget(self.cellLightSensorMismatchLabel, row, col + 1)

        self.m1m3.cellLightWarning.connect(self.cellLightWarning)
        self.m1m3.cellLightStatus.connect(self.cellLightStatus)

    @Slot(map)
    def cellLightWarning(self, data):
        setWarningLabel(self.anyWarningLabel, data.anyWarning)
        # TODO setWarningLabel(self.cellLightSensorMismatchLabel, BitHelper.get(data.cellLightFlags, CellLightFlags.CellLightSensorMismatch))

    @Slot(map)
    def cellLightStatus(self, data):
        setBoolLabelOnOff(self.cellLightsCommandedOnLabel, data.cellLightsCommandedOn)
        setBoolLabelOnOff(self.cellLightsOnLabel, data.cellLightsOn)

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
