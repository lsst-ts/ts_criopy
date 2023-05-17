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

import typing

from asyncqt import asyncSlot
from lsst.ts.cRIOpy.M1M3FATable import (
    FATABLE,
    FATABLE_ID,
    FATABLE_INDEX,
    FATABLE_ORIENTATION,
    FATABLE_XPOSITION,
    FATABLE_YPOSITION,
    FATABLE_ZINDEX,
    actuatorIDToIndex,
)
from lsst.ts.idl.enums.MTM1M3 import DetailedState
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QFormLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ...GUI.ActuatorsDisplay import ForceActuator, MirrorWidget, Scales
from ...GUI.SAL import SALCommand, StateEnabledWidget
from ...GUI.SAL.SALComm import MetaSAL
from .ComboBox import ComboBox


class Enabled(StateEnabledWidget):
    """Widget displaying map of the Force Actuators (FA). Enables end users to
    select a FA and enable/disable it.

    Parameters
    ----------
    m1m3 : `MetaSAL`
        SAL/DDS M1M3 communication.
    """

    def __init__(self, m1m3: MetaSAL):
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

        self.mirrorWidget.mirrorView.selectionChanged.connect(self.selectionChanged)  # type: ignore

        self.selectedActuatorId = ComboBox()
        self.selectedActuatorId.editTextChanged.connect(self._actuatorChanged)
        self.selectedActuatorValueLabel = QLabel()

        self.enableButton = QPushButton("&Enable")
        self.enableButton.clicked.connect(self._enableFA)
        self.enableAll = QPushButton("Enable &all")
        self.enableAll.clicked.connect(self._enable_all_force_actuators)
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

    def selectionChanged(self, s: typing.Any) -> None:
        """
        Called from childrens to update currently selected actuator display.

        Parameters
        ----------

        s : `map`
            Contains id (selected actuator ID), data (selected actuator current
            value) and warning (boolean, true if value is in warning).
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

    def getSelectedID(self) -> int | None:
        """Returns selected FA ID.

        Returns
        -------
        actuatorId : `int`
            Selected actuator ID.
        """
        if self.selectedActuatorId.currentText() > "":
            return int(self.selectedActuatorId.currentText())
        return None

    def _updateSelected(self) -> None:
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

    @Slot()
    def _actuatorChanged(self, text: str) -> None:
        self.mirrorWidget.setSelected(int(text))

    @asyncSlot()
    async def _enable_all_force_actuators(self) -> None:
        await SALCommand(self, self.m1m3.remote.cmd_enableAllForceActuators)

    @asyncSlot()
    async def _enableFA(self) -> None:
        id = self.getSelectedID()
        if id is not None:
            await SALCommand(
                self, self.m1m3.remote.cmd_enableForceActuator, actuatorId=id
            )

    @asyncSlot()
    async def _disableFA(self) -> None:
        id = self.getSelectedID()
        if id is not None:
            await SALCommand(
                self, self.m1m3.remote.cmd_disableForceActuator, actuatorId=id
            )

    @Slot()
    def enabledForceActuators(self, data: typing.Any) -> None:
        """Callback with enabled FA data. Triggers display update."""
        if len(self.mirrorWidget.mirrorView.items()) == 0:  # type: ignore
            new = True  # need to add force actuators
            self.mirrorWidget.mirrorView.clear()  # type: ignore
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
                self.mirrorWidget.mirrorView.addForceActuator(  # type: ignore
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
                self.mirrorWidget.mirrorView.updateForceActuator(id, value, state)  # type: ignore

        self.mirrorWidget.setColorScale()
        self._updateSelected()
