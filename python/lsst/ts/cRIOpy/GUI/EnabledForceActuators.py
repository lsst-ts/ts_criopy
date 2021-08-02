from lsst.ts.cRIOpy.M1M3FATable import (
    FATABLE,
    FATABLE_ID,
    FATABLE_ZINDEX,
    FATABLE_XPOSITION,
    FATABLE_YPOSITION,
    FATABLE_ORIENTATION,
    actuatorIDToIndex,
)
from .ActuatorsDisplay import MirrorWidget, ForceActuator, Scales
from .SALComm import SALCommand

from lsst.ts.idl.enums.MTM1M3 import DetailedState

from PySide2.QtCore import Slot
from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
)
from asyncqt import asyncSlot


class EnabledForceActuators(QWidget):
    def __init__(self, m1m3):
        self.mirrorWidget = MirrorWidget()
        self.mirrorWidget.setScaleType(Scales.ONOFF)
        super().__init__()
        self.m1m3 = m1m3

        self.m1m3.detailedState.connect(self.detailedState)
        self.m1m3.enabledForceActuators.connect(self.enabledForceActuators)

        self.mirrorWidget.mirrorView.selectionChanged.connect(self.selectionChanged)

        self.selectedActuatorIdLabel = QLabel()
        self.selectedActuatorValueLabel = QLabel()

        self.enableButton = QPushButton("&Enable")
        self.enableAll = QPushButton("Enable &all")
        self.enableAll.clicked.connect(self.issueCommandEnableAllForceActuators)
        self.disableButton = QPushButton("&Disable")

        fLayout = QFormLayout()
        fLayout.addRow("ID:", self.selectedActuatorIdLabel)
        fLayout.addRow("Value:", self.selectedActuatorValueLabel)

        vLayout = QVBoxLayout()
        vLayout.addLayout(fLayout)
        vLayout.addWidget(self.enableButton)
        vLayout.addWidget(self.enableAll)
        vLayout.addWidget(self.disableButton)

        layout = QHBoxLayout()
        layout.addWidget(self.mirrorWidget)
        layout.addLayout(vLayout)
        self.setLayout(layout)

        self.setEnabled(False)

        self.enabledForceActuators(None)

    def selectionChanged(self, s):
        """
        Called from childrens to update currently selected actuator display.

        Parameters
        ----------

        s : `map`
            Contains id (selected actuator ID), data (selected actuator current value) and warning (boolean, true if value is in warning).
        """
        if s is None:
            self.selectedActuatorIdLabel.setText("not selected")
            self.selectedActuatorValueLabel.setText("")
            self.enableButton.setEnabled(False)
            self.disableButton.setEnabled(False)
            return

        self.selectedActuatorIdLabel.setText(str(s.id))
        self.selectedActuatorValueLabel.setText(str(s.data))
        self.updateSelected()

    def updateSelected(self):
        index = actuatorIDToIndex(int(self.selectedActuatorIdLabel.text()))
        if index is not None:
            data = self.m1m3.enabledForceActuators.get()
            if data is not None:
                enabled = data.forceActuatorEnabled[index]
                self.enableButton.setEnabled(not enabled)
                self.disableButton.setEnabled(enabled)
                return

        self.enableButton.setEnabled(False)
        self.disableButton.setEnabled(False)

    @asyncSlot()
    async def issueCommandEnableAllForceActuators(self):
        await self._issueCommandEnableAllForceActuators()

    @SALCommand
    def _issueCommandEnableAllForceActuators(self, **kwargs):
        return self.m1m3.remote.cmd_enableAllForceActuators()

    @Slot(map)
    def detailedState(self, data):
        if data.detailedState in [
            DetailedState.PARKEDENGINEERING,
            DetailedState.RAISINGENGINEERING,
            DetailedState.ACTIVEENGINEERING,
            DetailedState.LOWERINGENGINEERING,
        ]:
            self.setEnabled(True)
        else:
            self.setEnabled(False)

    @Slot(map)
    def enabledForceActuators(self, data):
        self.mirrorWidget.mirrorView.clear()

        for row in FATABLE:
            index = row[FATABLE_ZINDEX]
            self.mirrorWidget.mirrorView.addForceActuator(
                row[FATABLE_ID],
                row[FATABLE_XPOSITION] * 1000,
                row[FATABLE_YPOSITION] * 1000,
                row[FATABLE_ORIENTATION],
                None if data is None else data.forceActuatorEnabled[index],
                index,
                ForceActuator.STATE_INACTIVE
                if data is None
                else ForceActuator.STATE_ACTIVE,
            )

        self.mirrorWidget.setColorScale()
        self.updateSelected()
