# This file is part of T&S cRIO Python library
#
# Developed for the LSST Telescope and Site Systems. This product includes
# software developed by the LSST Project (https://www.lsst.org). See the
# COPYRIGHT file at the top-level directory of this distribution for details of
# code ownership.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

from lsst.ts.cRIOpy.M1M3FATable import (
    FATABLE,
    FATABLE_ID,
    FATABLE_INDEX,
    FATABLE_ZINDEX,
    FATABLE_XPOSITION,
    FATABLE_YPOSITION,
    FATABLE_ORIENTATION,
    actuatorIDToIndex,
)
from .ActuatorComboBox import ActuatorComboBox
from .ActuatorsDisplay import MirrorWidget, ForceActuator, Scales
from .SALComm import SALCommand
from .StateEnabled import StateEnabledWidget

from lsst.ts.idl.enums.MTM1M3 import DetailedState

from PySide2.QtCore import Slot
from PySide2.QtWidgets import (
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
)
from asyncqt import asyncSlot


class EnabledForceActuators(StateEnabledWidget):
    """Widget displaying map of the Force Actuators (FA). Enables end users to
    select a FA and enable/disable it.

    Parameters
    ----------
    m1m3 : `SALcomm`
        SAL/DDS M1M3 communication.
    """

    def __init__(self, m1m3):
        self.mirrorWidget = MirrorWidget()
        self.mirrorWidget.setScaleType(Scales.ENABLED_DISABLED)
        super().__init__(
            m1m3,
            [
                DetailedState.PARKEDENGINEERING,
                DetailedState.RAISINGENGINEERING,
                DetailedState.ACTIVEENGINEERING,
                DetailedState.LOWERINGENGINEERING,
            ],
        )
        self.m1m3 = m1m3

        self.m1m3.enabledForceActuators.connect(self.enabledForceActuators)

        self.mirrorWidget.mirrorView.selectionChanged.connect(self.selectionChanged)

        self.selectedActuatorId = ActuatorComboBox()
        self.selectedActuatorId.editTextChanged.connect(self._actuatorChanged)
        self.selectedActuatorValueLabel = QLabel()

        self.enableButton = QPushButton("&Enable")
        self.enableButton.clicked.connect(self._enableFA)
        self.enableAll = QPushButton("Enable &all")
        self.enableAll.clicked.connect(self._enableAllForceActuators)
        self.disableButton = QPushButton("&Disable")
        self.disableButton.clicked.connect(self._disableFA)

        fLayout = QFormLayout()
        fLayout.addRow("ID:", self.selectedActuatorId)
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
            self.selectedActuatorId.setEditText("not selected")
            self.selectedActuatorValueLabel.setText("")
            self.enableButton.setEnabled(False)
            self.disableButton.setEnabled(False)
            return

        self.selectedActuatorId.setEditText(str(s.id))
        self.selectedActuatorValueLabel.setText(str(s.data))
        self._updateSelected()

    def getSelectedID(self):
        """Returns selected FA ID.

        Returns
        -------
        actuatorId : `int`
            Selected actuator ID.
        """
        if self.selectedActuatorId.currentText() > "":
            return int(self.selectedActuatorId.currentText())
        return None

    def _updateSelected(self):
        id = self.getSelectedID()
        if id is not None:
            index = actuatorIDToIndex(id)
            if index is not None:
                data = self.m1m3.remote.evt_enabledForceActuators.get()
                if data is not None:
                    enabled = data.forceActuatorEnabled[index]
                    self.enableButton.setEnabled(not enabled)
                    self.disableButton.setEnabled(enabled)
                    return

        self.enableButton.setEnabled(False)
        self.disableButton.setEnabled(False)

    @Slot(str)
    def _actuatorChanged(self, text):
        self.mirrorWidget.setSelected(int(text))

    @asyncSlot()
    async def _enableAllForceActuators(self):
        await self._issueCommandEnableAllForceActuators()

    @SALCommand
    def _issueCommandEnableAllForceActuators(self, **kwargs):
        return self.m1m3.remote.cmd_enableAllForceActuators

    @asyncSlot()
    async def _enableFA(self):
        id = self.getSelectedID()
        if id is not None:
            await self._issueCommandEnable(actuatorId=id)

    @SALCommand
    def _issueCommandEnable(self, **kwargs):
        return self.m1m3.remote.cmd_enableForceActuator

    @asyncSlot()
    async def _disableFA(self):
        id = self.getSelectedID()
        if id is not None:
            await self._issueCommandDisable(actuatorId=id)

    @SALCommand
    def _issueCommandDisable(self, **kwargs):
        return self.m1m3.remote.cmd_disableForceActuator

    @Slot(map)
    def enabledForceActuators(self, data):
        """Callback with enabled FA data. Triggers display update."""
        if len(self.mirrorWidget.mirrorView.items()) == 0:
            new = True  # need to add force actuators
            self.mirrorWidget.mirrorView.clear()
        else:
            new = False

        for row in FATABLE:
            index = row[FATABLE_ZINDEX]
            id = row[FATABLE_ID]
            value = None if data is None else data.forceActuatorEnabled[index]
            state = (
                ForceActuator.STATE_INACTIVE
                if data is None
                else ForceActuator.STATE_ACTIVE
            )
            if new:
                self.mirrorWidget.mirrorView.addForceActuator(
                    id,
                    row[FATABLE_INDEX],
                    row[FATABLE_XPOSITION] * 1000,
                    row[FATABLE_YPOSITION] * 1000,
                    row[FATABLE_ORIENTATION],
                    value,
                    index,
                    state,
                )
            else:
                self.mirrorWidget.mirrorView.updateForceActuator(id, value, state)

        self.mirrorWidget.setColorScale()
        self._updateSelected()
