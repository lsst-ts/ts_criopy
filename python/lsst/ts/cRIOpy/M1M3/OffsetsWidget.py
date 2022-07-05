# This file is part of M1M3 SS GUI.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org). See the COPYRIGHT file at the top - level directory
# of this distribution for details of code ownership.
#
# This program is free software : you can redistribute it and / or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.If not, see <https://www.gnu.org/licenses/>.

import astropy.units as u

from PySide2.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QDoubleSpinBox,
    QPushButton,
)
from PySide2.QtCore import Slot
from asyncqt import asyncSlot

from lsst.ts.idl.enums.MTM1M3 import DetailedState

from ..GUI import Force, Moment, Mm, MmWarning, Arcsec, ArcsecWarning
from ..GUI.SAL import SALCommand
from .DirectionPadWidget import DirectionPadWidget


class OffsetsWidget(QWidget):
    """Displays position data - measured and target position, allows to offset
    (jog) the mirror using position/rotation and force/moment offsets.

    POSITIONS
    ---------
        Array containing name of positions. Used to name variables and as
        arguments names for positionM1M3 command.

    FORCES
    ------
        Array containing forces and momements.

    Parameters
    ----------
    m1m3 : `SALComm`
        Proxy class for SAL/DDS communication. See SALComm.py for details.
    """

    POSITIONS = [
        "xPosition",
        "yPosition",
        "zPosition",
        "xRotation",
        "yRotation",
        "zRotation",
    ]

    FORCES = ["xForce", "yForce", "zForce", "xMoment", "yMoment", "zMoment"]

    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3

        self._hpData = None
        self._imsData = None

        self.layout = QVBoxLayout()

        dataLayout = QGridLayout()

        self.layout.addLayout(dataLayout)
        self.setLayout(self.layout)

        directions = ["X", "Y", "Z", "Rotation X", "Rotation Y", "Rotation Z"]

        row = 0

        for d in range(6):
            dataLayout.addWidget(QLabel(f"<b>{directions[d]}</b>"), row, d + 1)

        def createXYZR():
            return {
                "xPosition": Mm(),
                "yPosition": Mm(),
                "zPosition": Mm(),
                "xRotation": Arcsec(),
                "yRotation": Arcsec(),
                "zRotation": Arcsec(),
            }

        def createXYZRWarning():
            return {
                "xPosition": MmWarning(),
                "yPosition": MmWarning(),
                "zPosition": MmWarning(),
                "xRotation": ArcsecWarning(),
                "yRotation": ArcsecWarning(),
                "zRotation": ArcsecWarning(),
            }

        self.hpVariables = createXYZR()

        self.imsVariables = createXYZR()

        self.diffs = createXYZRWarning()

        def addDataRow(variables, row, col=1):
            for k, v in variables.items():
                dataLayout.addWidget(v, row, col)
                col += 1

        row += 1
        dataLayout.addWidget(QLabel("<b>HP</b>"), row, 0)
        addDataRow(self.hpVariables, row)

        row += 1
        dataLayout.addWidget(QLabel("<b>IMS</b>"), row, 0)
        addDataRow(self.imsVariables, row)

        row += 1
        dataLayout.addWidget(QLabel("<b>Diff</b>"), row, 0)
        addDataRow(self.diffs, row)

        row += 1
        dataLayout.addWidget(QLabel("<b>Target</b>"), row, 0)

        col = 1
        for p in self.POSITIONS:
            sb = QDoubleSpinBox()
            if p[1:] == "Position":
                sb.setRange(-10, 10)
                sb.setDecimals(3)
                sb.setSingleStep(0.001)
            else:
                sb.setRange(-300, 300)
                sb.setDecimals(2)
                sb.setSingleStep(0.01)

            dataLayout.addWidget(sb, row, col)
            setattr(self, "target_" + p, sb)
            col += 1

        row += 1

        self.moveMirrorButton = QPushButton("Move Mirror")
        self.moveMirrorButton.setEnabled(False)
        self.moveMirrorButton.clicked.connect(self._moveMirror)
        self.moveMirrorButton.setDefault(True)

        dataLayout.addWidget(self.moveMirrorButton, row, 1, 1, 3)

        self.copyCurrentButton = QPushButton("Copy Current")
        self.copyCurrentButton.setEnabled(False)
        self.copyCurrentButton.clicked.connect(self._copyCurrent)

        dataLayout.addWidget(self.copyCurrentButton, row, 4, 1, 3)

        row += 1
        self.dirPad = DirectionPadWidget()
        self.dirPad.setEnabled(False)
        self.dirPad.positionChanged.connect(self._positionChanged)
        dataLayout.addWidget(self.dirPad, row, 1, 3, 6)

        def createForces():
            return {
                "fx": Force(),
                "fy": Force(),
                "fz": Force(),
                "mx": Moment(),
                "my": Moment(),
                "mz": Moment(),
            }

        self.preclipped = createForces()
        self.applied = createForces()
        self.measured = createForces()

        row += 3
        dataLayout.addWidget(QLabel("<b>Preclipped</b>"), row, 0)
        addDataRow(self.preclipped, row)

        row += 1
        dataLayout.addWidget(QLabel("<b>Applied</b>"), row, 0)
        addDataRow(self.applied, row)

        row += 1
        dataLayout.addWidget(QLabel("<b>Measured</b>"), row, 0)
        addDataRow(self.measured, row)

        row += 1
        dataLayout.addWidget(QLabel("<b>Offset</b>"), row, 0)

        col = 1
        for p in self.FORCES:
            sb = QDoubleSpinBox()
            sb.setRange(-10000, 10000)
            sb.setDecimals(1)
            sb.setSingleStep(1)

            dataLayout.addWidget(sb, row, col)
            setattr(self, "forceOffsets_" + p, sb)
            col += 1

        row += 1
        self.offsetForces = QPushButton("Apply offset forces")
        self.offsetForces.setEnabled(False)
        self.offsetForces.clicked.connect(self._applyOffsetForces)
        dataLayout.addWidget(self.offsetForces, row, 1, 1, 3)

        self.clearOffsetForcesButton = QPushButton("Reset forces")
        self.clearOffsetForcesButton.setEnabled(False)
        self.clearOffsetForcesButton.clicked.connect(self._clearOffsetForces)
        dataLayout.addWidget(self.clearOffsetForcesButton, row, 4, 1, 3)

        self.layout.addStretch()

        self.m1m3.hardpointActuatorData.connect(self._hardpointActuatorDataCallback)
        self.m1m3.imsData.connect(self._imsDataCallback)
        self.m1m3.preclippedOffsetForces.connect(self._preclippedOffsetForces)
        self.m1m3.appliedOffsetForces.connect(self._appliedOffsetForces)
        self.m1m3.forceActuatorData.connect(self._forceActuatorCallback)
        self.m1m3.detailedState.connect(self._detailedStateCallback)

    @SALCommand
    def moveMirror(self, **kwargs):
        """Move mirror. Calls positionM1M3 command.

        Parameters
        ----------
        **kwargs : `dict`
            New target position. Needs to have POSITIONS keys. Passed to
            positionM1M3 command.
        """
        return self.m1m3.remote.cmd_positionM1M3

    @SALCommand
    def applyOffsetForcesByMirrorForce(self, **kwargs):
        """Apply mirror offset forces.

        Parameters
        ----------
        **kwargs : `dict`
            Offsets specified as forces and moments.
        """
        return self.m1m3.remote.cmd_applyOffsetForcesByMirrorForce

    @SALCommand
    def clearOffsetForces(self, **kwargs):
        return self.m1m3.remote.cmd_clearOffsetForces

    def _getScale(self, label):
        return u.mm.to(u.m) if label[1:] == "Position" else u.arcsec.to(u.deg)

    def getTargets(self):
        """Return current target values (from form target box).

        Returns
        -------
        args : `dict`
            Current target values. Contains POSITIONS keys. In default units
            (mm, degrees).
        """
        args = {}
        for p in self.POSITIONS:
            args[p] = getattr(self, "target_" + p).value() * self._getScale(p)
        return args

    def setTargets(self, targets):
        """Set current target values.

        Parameters
        ----------
        targets : `dict`
            Target values. Dictionary with POSITIONS keys.
        """
        for k, v in targets.items():
            getattr(self, "target_" + k).setValue(v / self._getScale(k))

    def getForceOffsets(self):
        """Return current offset forces (from forceOffsets_ box).

        Returns
        -------
        offsets : `dict`
             Current offset forces. Contains FORCES keys.
        """
        offsets = {}
        for f in self.FORCES:
            offsets[f] = getattr(self, "forceOffsets_" + f).value()
        return offsets

    @asyncSlot()
    async def _moveMirror(self):
        targets = self.getTargets()
        self.dirPad.setPosition(map(lambda p: targets[p], self.POSITIONS))
        await self.moveMirror(**self.getTargets())

    @Slot()
    def _copyCurrent(self):
        args = {k: getattr(self._hpData, k) for k in self.POSITIONS}
        self.setTargets(args)
        self.dirPad.setPosition(map(lambda p: args[p], self.POSITIONS))

    @asyncSlot()
    async def _applyOffsetForces(self):
        await self.applyOffsetForcesByMirrorForce(**self.getForceOffsets())

    @asyncSlot()
    async def _clearOffsetForces(self):
        await self.clearOffsetForces()
        for f in self.FORCES:
            getattr(self, "forceOffsets_" + f).setValue(0)

    @asyncSlot()
    async def _positionChanged(self, offsets):
        args = {}
        for i in range(6):
            args[self.POSITIONS[i]] = offsets[i]
        self.setTargets(args)
        await self.moveMirror(**args)

    def _fillRow(self, variables, data):
        for k, v in variables.items():
            v.setValue(getattr(data, k))

    def _updateDiffs(self):
        if self._hpData is None or self._imsData is None:
            return
        for k, v in self.diffs.items():
            v.setValue(getattr(self._hpData, k) - getattr(self._imsData, k))

    @Slot(map)
    def _hardpointActuatorDataCallback(self, data):
        self._fillRow(self.hpVariables, data)
        self._hpData = data
        self.copyCurrentButton.setEnabled(True)
        self._updateDiffs()

    @Slot(map)
    def _imsDataCallback(self, data):
        self._fillRow(self.imsVariables, data)
        self._imsData = data
        self._updateDiffs()

    @Slot(map)
    def _preclippedOffsetForces(self, data):
        self._fillRow(self.preclipped, data)

    @Slot(map)
    def _appliedOffsetForces(self, data):
        self._fillRow(self.applied, data)

    @Slot(map)
    def _forceActuatorCallback(self, data):
        self._fillRow(self.measured, data)

    @Slot(map)
    def _detailedStateCallback(self, data):
        enabled = data.detailedState == DetailedState.ACTIVEENGINEERING

        self.moveMirrorButton.setEnabled(enabled)
        self.dirPad.setEnabled(enabled)
        self.offsetForces.setEnabled(enabled)
        self.clearOffsetForcesButton.setEnabled(enabled)
