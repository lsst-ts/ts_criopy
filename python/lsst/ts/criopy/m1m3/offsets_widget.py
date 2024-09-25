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

import typing
from functools import partial

import astropy.units as u
from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.enums.MTM1M3 import DetailedStates
from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ..gui import (
    Arcsec,
    ArcsecWarning,
    Force,
    FormatLabel,
    Mm,
    MmWarning,
    Moment,
    UnitLabel,
)
from ..salcomm import MetaSAL, command
from .direction_pad_widget import DirectionPadWidget


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

    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        self.m1m3 = m1m3

        self.__hp_data = None
        self.__ims_data = None

        layout = QVBoxLayout()

        data_layout = QGridLayout()

        layout.addLayout(data_layout)
        self.setLayout(layout)

        directions = ["X", "Y", "Z", "Rotation X", "Rotation Y", "Rotation Z"]

        row = 0

        for d in range(6):
            data_layout.addWidget(QLabel(f"<b>{directions[d]}</b>"), row, d + 1)

        def createXYZR() -> dict[str, QLabel]:
            return {
                "xPosition": Mm(),
                "yPosition": Mm(),
                "zPosition": Mm(),
                "xRotation": Arcsec(),
                "yRotation": Arcsec(),
                "zRotation": Arcsec(),
            }

        def createXYZRWarning() -> dict[str, QLabel]:
            return {
                "xPosition": MmWarning(),
                "yPosition": MmWarning(),
                "zPosition": MmWarning(),
                "xRotation": ArcsecWarning(),
                "yRotation": ArcsecWarning(),
                "zRotation": ArcsecWarning(),
            }

        def createForces() -> dict[str, QLabel]:
            return {
                "fx": Force(),
                "fy": Force(),
                "fz": Force(),
                "mx": Moment(),
                "my": Moment(),
                "mz": Moment(),
            }

        def createArray(
            var: str, label: typing.Callable[[], UnitLabel]
        ) -> dict[str, QLabel]:
            ret = {}
            for i in range(6):
                ret[f"{var}[{i}]"] = label()
            return ret

        self.hp_position = createXYZR()

        self.ims_position = createXYZR()

        self.diffs = createXYZRWarning()

        self.hp_forces = createForces()
        self.hp_measured_forces = createArray("measuredForce", Force)
        self.hp_displacement = createArray("displacement", Mm)
        self.hp_encoder = createArray("encoder", partial(FormatLabel, ".0f"))

        def addDataRow(variables: dict[str, QLabel], row: int, col: int = 1) -> None:
            for k, v in variables.items():
                data_layout.addWidget(v, row, col)
                col += 1

        row += 1
        data_layout.addWidget(QLabel("<b>HP</b>"), row, 0)
        addDataRow(self.hp_position, row)

        row += 1
        data_layout.addWidget(QLabel("<b>IMS</b>"), row, 0)
        addDataRow(self.ims_position, row)

        row += 1
        data_layout.addWidget(QLabel("<b>Diff</b>"), row, 0)
        addDataRow(self.diffs, row)

        row += 1
        data_layout.addWidget(QLabel("<b>Target</b>"), row, 0)

        col = 1
        for p in self.POSITIONS:
            sb = QDoubleSpinBox()
            if p[1:] == "Position":
                sb.setRange(-10, 10)
                sb.setDecimals(3)
                sb.setSingleStep(0.1)
            else:
                sb.setRange(-300, 300)
                sb.setDecimals(2)
                sb.setSingleStep(0.1)

            data_layout.addWidget(sb, row, col)
            setattr(self, "target_" + p, sb)
            col += 1

        row += 1
        self.move_mirror_button = QPushButton("Move Mirror")
        self.move_mirror_button.setEnabled(False)
        self.move_mirror_button.clicked.connect(self._move_mirror)
        self.move_mirror_button.setDefault(True)

        data_layout.addWidget(self.move_mirror_button, row, 1, 1, 2)

        self.stop_mirror_button = QPushButton("&Stop")
        self.stop_mirror_button.setEnabled(False)
        self.stop_mirror_button.clicked.connect(self._stop_mirror)

        data_layout.addWidget(self.stop_mirror_button, row, 3, 1, 2)

        self.copy_current_button = QPushButton("Copy Current")
        self.copy_current_button.setEnabled(False)
        self.copy_current_button.clicked.connect(self._copy_current)

        data_layout.addWidget(self.copy_current_button, row, 5, 1, 1)

        zero_button = QPushButton("Zero target")
        zero_button.clicked.connect(self._zero_target)

        data_layout.addWidget(zero_button, row, 6, 1, 1)

        row += 1
        data_layout.addWidget(QLabel("<b>HP forces</b>"), row, 0)
        addDataRow(self.hp_forces, row)

        row += 1
        data_layout.addWidget(QLabel(), row, 0)  # empty row

        row += 1
        for hp_num in range(1, 7):
            data_layout.addWidget(QLabel(f"<b>{hp_num}</b>"), row, hp_num)

        row += 1
        data_layout.addWidget(QLabel("<b>HP measured forces</b>"), row, 0)
        addDataRow(self.hp_measured_forces, row)

        row += 1
        data_layout.addWidget(QLabel("HP displacement"), row, 0)
        addDataRow(self.hp_displacement, row)

        row += 1
        data_layout.addWidget(QLabel("HP encoder"), row, 0)
        addDataRow(self.hp_encoder, row)

        row += 1
        self.dir_pad = DirectionPadWidget()
        self.dir_pad.setEnabled(False)
        self.dir_pad.positionChanged.connect(self._positionChanged)
        data_layout.addWidget(self.dir_pad, row, 1, 3, 6)

        self.preclipped = createForces()
        self.applied = createForces()
        self.measured = createForces()

        row += 3
        for i in range(6):
            text = (
                f"Force {chr(ord('W') + i)}"
                if i < 3
                else f"Moment {chr(ord('W') + i - 3)}"
            )
            data_layout.addWidget(QLabel(f"<b>{text}</b>"))

        row += 1
        data_layout.addWidget(QLabel("<b>Preclipped</b>"), row, 0)
        addDataRow(self.preclipped, row)

        row += 1
        data_layout.addWidget(QLabel("<b>Applied</b>"), row, 0)
        addDataRow(self.applied, row)

        row += 1
        data_layout.addWidget(QLabel("<b>Measured</b>"), row, 0)
        addDataRow(self.measured, row)

        row += 1
        data_layout.addWidget(QLabel("<b>Offset</b>"), row, 0)

        col = 1
        for p in self.FORCES:
            sb = QDoubleSpinBox()
            sb.setRange(-10000, 10000)
            sb.setDecimals(1)
            sb.setSingleStep(1)

            data_layout.addWidget(sb, row, col)
            setattr(self, "forceOffsets_" + p, sb)
            col += 1

        row += 1
        self.offsetForces = QPushButton("Apply offset forces")
        self.offsetForces.setEnabled(False)
        self.offsetForces.clicked.connect(self._applyOffsetForces)
        data_layout.addWidget(self.offsetForces, row, 1, 1, 3)

        self.clearOffsetForcesButton = QPushButton("Reset forces")
        self.clearOffsetForcesButton.setEnabled(False)
        self.clearOffsetForcesButton.clicked.connect(self._clearOffsetForces)
        data_layout.addWidget(self.clearOffsetForcesButton, row, 4, 1, 3)

        layout.addStretch()

        self.m1m3.hardpointActuatorData.connect(self._hardpointActuatorDataCallback)
        self.m1m3.imsData.connect(self._imsDataCallback)
        self.m1m3.preclippedOffsetForces.connect(self._preclippedOffsetForces)
        self.m1m3.appliedOffsetForces.connect(self._appliedOffsetForces)
        self.m1m3.forceActuatorData.connect(self._forceActuatorCallback)
        self.m1m3.detailedState.connect(self._detailedStateCallback)

    async def moveMirror(self, **kwargs: typing.Any) -> None:
        """Move mirror. Calls positionM1M3 command.

        Parameters
        ----------
        **kwargs : `dict`
            New target position. Needs to have POSITIONS keys. Passed to
            positionM1M3 command.
        """
        await command(self, self.m1m3.remote.cmd_positionM1M3, **kwargs)

    def _getScale(self, label: str) -> float:
        return u.mm.to(u.m) if label[1:] == "Position" else u.arcsec.to(u.deg)

    def get_targets(self) -> dict[str, float]:
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

    def set_targets(self, targets: dict[str, float]) -> None:
        """Set current target values.

        Parameters
        ----------
        targets : `dict`
            Target values. Dictionary with POSITIONS keys.
        """
        for k, v in targets.items():
            getattr(self, "target_" + k).setValue(v / self._getScale(k))

    def getForceOffsets(self) -> dict[str, float]:
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
    async def _move_mirror(self) -> None:
        targets = self.get_targets()
        self.dir_pad.set_position(targets[p] for p in self.POSITIONS)
        await self.moveMirror(**self.get_targets())

    @asyncSlot()
    async def _stop_mirror(self) -> None:
        await command(self, self.m1m3.remote.cmd_stopHardpointMotion)

    @Slot()
    def _copy_current(self) -> None:
        args = {k: getattr(self.__hp_data, k) for k in self.POSITIONS}
        self.set_targets(args)
        self.dir_pad.set_position(args[p] for p in self.POSITIONS)

    @Slot()
    def _zero_target(self) -> None:
        args = {k: 0.0 for k in self.POSITIONS}
        self.set_targets(args)
        self.dir_pad.set_position(args[p] for p in self.POSITIONS)

    @asyncSlot()
    async def _applyOffsetForces(self) -> None:
        await command(
            self,
            self.m1m3.remote.cmd_applyOffsetForcesByMirrorForce,
            **self.getForceOffsets(),
        )

    @asyncSlot()
    async def _clearOffsetForces(self) -> None:
        await command(self, self.m1m3.remote.cmd_clearOffsetForces)
        for f in self.FORCES:
            getattr(self, "forceOffsets_" + f).setValue(0)

    @asyncSlot()
    async def _positionChanged(self, offsets: list[float]) -> None:
        args = {}
        for i in range(6):
            args[self.POSITIONS[i]] = offsets[i]
        self.set_targets(args)
        await self.moveMirror(**args)

    def __fill_array(self, variables: dict[str, QLabel], data: typing.Any) -> None:
        for k, v in variables.items():
            sep = k.index("[")
            v.setValue(getattr(data, k[:sep])[int(k[sep + 1])])

    def __fill_row(self, variables: dict[str, QLabel], data: typing.Any) -> None:
        for k, v in variables.items():
            v.setValue(getattr(data, k))

    def __update_diffs(self) -> None:
        if self.__hp_data is None or self.__ims_data is None:
            return
        for k, v in self.diffs.items():
            v.setValue(getattr(self.__hp_data, k) - getattr(self.__ims_data, k))

    @Slot()
    def _hardpointActuatorDataCallback(self, data: BaseMsgType) -> None:
        self.__fill_row(self.hp_position, data)
        self.__fill_row(self.hp_forces, data)
        self.__fill_array(self.hp_measured_forces, data)
        self.__fill_array(self.hp_displacement, data)
        self.__fill_array(self.hp_encoder, data)
        self.__hp_data = data
        self.copy_current_button.setEnabled(True)
        self.__update_diffs()

    @Slot()
    def _imsDataCallback(self, data: BaseMsgType) -> None:
        self.__fill_row(self.ims_position, data)
        self.__ims_data = data
        self.__update_diffs()

    @Slot()
    def _preclippedOffsetForces(self, data: typing.Any) -> None:
        self.__fill_row(self.preclipped, data)

    @Slot()
    def _appliedOffsetForces(self, data: typing.Any) -> None:
        self.__fill_row(self.applied, data)

    @Slot()
    def _forceActuatorCallback(self, data: typing.Any) -> None:
        self.__fill_row(self.measured, data)

    @Slot()
    def _detailedStateCallback(self, data: typing.Any) -> None:
        enabled = data.detailedState == DetailedStates.ACTIVEENGINEERING

        self.move_mirror_button.setEnabled(enabled)
        self.stop_mirror_button.setEnabled(enabled)
        self.dir_pad.setEnabled(enabled)
        self.offsetForces.setEnabled(enabled)
        self.clearOffsetForcesButton.setEnabled(enabled)
