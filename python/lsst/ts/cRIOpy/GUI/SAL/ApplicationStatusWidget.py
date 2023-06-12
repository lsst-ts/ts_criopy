# This file is part of cRIO/VMS GUI.
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

from lsst.ts.idl.enums import MTM1M3
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from .SALComm import warning
from .SummaryStateLabel import SummaryStateLabel


class ApplicationStatusWidget(QWidget):
    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3

        self.layout = QVBoxLayout()
        self.statusLayout = QGridLayout()
        self.layout.addLayout(self.statusLayout)
        self.setLayout(self.layout)

        self.modeStateLabel = QLabel("---")
        self.mirrorStateLabel = QLabel("---")

        row = 0
        col = 0
        self.statusLayout.addWidget(QLabel("State"), row, col)
        self.statusLayout.addWidget(
            SummaryStateLabel(self.m1m3.summaryState, "summaryState"), row, col + 1
        )
        row += 1
        self.statusLayout.addWidget(QLabel("Mode"), row, col)
        self.statusLayout.addWidget(self.modeStateLabel, row, col + 1)
        row += 1
        self.statusLayout.addWidget(QLabel("Mirror State"), row, col)
        self.statusLayout.addWidget(self.mirrorStateLabel, row, col + 1)

        self.m1m3.detailedState.connect(self.processEventDetailedState)

    @Slot()
    def raisingLoweringInfo(self, data: typing.Any) -> None:
        detailedData = self.m1m3.remote.evt_detailedState.get()
        if detailedData is None:
            return
        if (
            detailedData.detailedState == MTM1M3.DetailedState.RAISING
            or detailedData.detailedState == MTM1M3.DetailedState.RAISINGENGINEERING
        ):
            if data.weightSupportedPercent >= 100:
                self.mirrorStateLabel.setText("Raising - positioning hardpoints")
            else:
                self.mirrorStateLabel.setText(
                    f"Raising ({data.weightSupportedPercent:.02f}%)"
                )
        elif (
            detailedData.detailedState == MTM1M3.DetailedState.LOWERING
            or detailedData.detailedState == MTM1M3.DetailedState.LOWERINGENGINEERING
        ):
            if data.weightSupportedPercent <= 0:
                self.mirrorStateLabel.setText("Lowering - positioning hardpoints")
            else:
                self.mirrorStateLabel.setText(
                    f"Lowering ({data.weightSupportedPercent:.02f}%)"
                )
        elif detailedData.detailedState == MTM1M3.DetailedState.LOWERINGFAULT:
            self.mirrorStateLabel.setText(
                f"Lowering (fault, {data.weightSupportedPercent:.02f}%)"
            )
        else:
            self._disconnectRaiseLowering()

    def _connectRaiseLowering(self):
        self.m1m3.raisingLoweringInfo.connect(
            self.raisingLoweringInfo, Qt.UniqueConnection
        )

    def _disconnectRaiseLowering(self):
        try:
            self.m1m3.raisingLoweringInfo.disconnect(self.raisingLoweringInfo)
        except RuntimeError:
            # raised when disconnecting not connected slot - ignore it, as the
            # code might try to disconnect not connected slot
            pass

    @Slot()
    def processEventDetailedState(self, data: typing.Any) -> None:
        modeStateText = "Unknown"
        mirrorStateText = "Unknown"
        if data.detailedState == MTM1M3.DetailedState.DISABLED:
            modeStateText = "Automatic"
            mirrorStateText = "Parked"
        elif data.detailedState == MTM1M3.DetailedState.FAULT:
            modeStateText = "Automatic"
            mirrorStateText = "Fault"
        elif data.detailedState == MTM1M3.DetailedState.OFFLINE:
            modeStateText = "Offline"
            mirrorStateText = "Parked"
        elif data.detailedState == MTM1M3.DetailedState.STANDBY:
            modeStateText = "Automatic"
            mirrorStateText = "Parked"
        elif data.detailedState == MTM1M3.DetailedState.PARKED:
            modeStateText = "Automatic"
            mirrorStateText = "Parked"
            self._disconnectRaiseLowering()
        elif data.detailedState == MTM1M3.DetailedState.RAISING:
            modeStateText = "Automatic"
            percent = (
                self.m1m3.remote.evt_forceActuatorState.get().weightSupportedPercent
            )
            mirrorStateText = f"Raising ({percent:.03f}%)"
            self._connectRaiseLowering()
        elif data.detailedState == MTM1M3.DetailedState.ACTIVE:
            modeStateText = "Automatic"
            mirrorStateText = "Active"
            self._disconnectRaiseLowering()
        elif data.detailedState == MTM1M3.DetailedState.LOWERING:
            modeStateText = "Automatic"
            mirrorStateText = "Lowering"
            self._connectRaiseLowering()
        elif data.detailedState == MTM1M3.DetailedState.PARKEDENGINEERING:
            modeStateText = "Manual"
            mirrorStateText = "Parked"
            self._disconnectRaiseLowering()
        elif data.detailedState == MTM1M3.DetailedState.RAISINGENGINEERING:
            modeStateText = "Manual"
            mirrorStateText = "Raising"
            self._connectRaiseLowering()
        elif data.detailedState == MTM1M3.DetailedState.ACTIVEENGINEERING:
            modeStateText = "Manual"
            mirrorStateText = "Active"
            self._disconnectRaiseLowering()
        elif data.detailedState == MTM1M3.DetailedState.LOWERINGENGINEERING:
            modeStateText = "Manual"
            mirrorStateText = "Lowering"
            self._connectRaiseLowering()
        elif data.detailedState == MTM1M3.DetailedState.LOWERINGFAULT:
            modeStateText = "Automatic"
            mirrorStateText = "Lowering (fault)"
            self._connectRaiseLowering()
        elif data.detailedState == MTM1M3.DetailedState.PROFILEHARDPOINTCORRECTIONS:
            modeStateText = "Profile hardpoint corrections"
            mirrorStateText = "Active"
            self._disconnectRaiseLowering()
        else:
            warning(
                self, "Unknown state", f"Unknown state received - {data.detailedState}"
            )
            self._disconnectRaiseLowering()
            return

        self.modeStateLabel.setText(modeStateText)
        self.mirrorStateLabel.setText(mirrorStateText)
