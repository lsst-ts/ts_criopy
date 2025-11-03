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


from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.enums.MTM1M3 import DetailedStates
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from ...salcomm import MetaSAL, warning
from .summary_state_label import SummaryStateLabel


class ApplicationStatusWidget(QWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        self.m1m3 = m1m3

        layout = QVBoxLayout()
        status_layout = QGridLayout()
        layout.addLayout(status_layout)
        self.setLayout(layout)

        self.mode_state_label = QLabel("---")
        self.mirror_state_label = QLabel("---")

        row = 0
        col = 0
        status_layout.addWidget(QLabel("State"), row, col)
        status_layout.addWidget(
            SummaryStateLabel(self.m1m3.summaryState),
            row,
            col + 1,
        )
        row += 1
        status_layout.addWidget(QLabel("Mode"), row, col)
        status_layout.addWidget(self.mode_state_label, row, col + 1)
        row += 1
        status_layout.addWidget(QLabel("Mirror State"), row, col)
        status_layout.addWidget(self.mirror_state_label, row, col + 1)

        self.m1m3.detailedState.connect(self.process_event_detailed_state)

    @Slot()
    def raisingLoweringInfo(self, data: BaseMsgType) -> None:
        detailedData = self.m1m3.remote.evt_detailedState.get()
        if detailedData is None:
            return
        if (
            detailedData.detailedState == DetailedStates.RAISING
            or detailedData.detailedState == DetailedStates.RAISINGENGINEERING
        ):
            if data.weightSupportedPercent >= 100:
                self.mirror_state_label.setText("Raising - positioning hardpoints")
            else:
                self.mirror_state_label.setText(f"Raising ({data.weightSupportedPercent:.02f}%)")
        elif (
            detailedData.detailedState == DetailedStates.LOWERING
            or detailedData.detailedState == DetailedStates.LOWERINGENGINEERING
        ):
            if data.weightSupportedPercent <= 0:
                self.mirror_state_label.setText("Lowering - positioning hardpoints")
            else:
                self.mirror_state_label.setText(f"Lowering ({data.weightSupportedPercent:.02f}%)")
        elif detailedData.detailedState == DetailedStates.LOWERINGFAULT:
            self.mirror_state_label.setText(f"Lowering (fault, {data.weightSupportedPercent:.02f}%)")
        else:
            self._disconnect_raise_lowering()

    def _connect_raise_lowering(self) -> None:
        self.m1m3.raisingLoweringInfo.connect(self.raisingLoweringInfo, Qt.UniqueConnection)

    def _disconnect_raise_lowering(self) -> None:
        try:
            self.m1m3.raisingLoweringInfo.disconnect(self.raisingLoweringInfo)
        except RuntimeError:
            # raised when disconnecting not connected slot - ignore it, as the
            # code might try to disconnect not connected slot
            pass

    @Slot()
    def process_event_detailed_state(self, data: BaseMsgType) -> None:
        mode_state_text = "Unknown"
        mirror_state_text = "Unknown"
        if data.detailedState == DetailedStates.DISABLED:
            mode_state_text = "Automatic"
            mirror_state_text = "Parked"
        elif data.detailedState == DetailedStates.FAULT:
            mode_state_text = "Automatic"
            mirror_state_text = "Fault"
        elif data.detailedState == DetailedStates.OFFLINE:
            mode_state_text = "Offline"
            mirror_state_text = "Parked"
        elif data.detailedState == DetailedStates.STANDBY:
            mode_state_text = "Automatic"
            mirror_state_text = "Parked"
        elif data.detailedState == DetailedStates.PARKED:
            mode_state_text = "Automatic"
            mirror_state_text = "Parked"
            self._disconnect_raise_lowering()
        elif data.detailedState == DetailedStates.RAISING:
            mode_state_text = "Automatic"
            percent = self.m1m3.remote.evt_forceActuatorState.get().weightSupportedPercent
            mirror_state_text = f"Raising ({percent:.03f}%)"
            self._connect_raise_lowering()
        elif data.detailedState == DetailedStates.ACTIVE:
            mode_state_text = "Automatic"
            mirror_state_text = "Active"
            self._disconnect_raise_lowering()
        elif data.detailedState == DetailedStates.LOWERING:
            mode_state_text = "Automatic"
            mirror_state_text = "Lowering"
            self._connect_raise_lowering()
        elif data.detailedState == DetailedStates.PARKEDENGINEERING:
            mode_state_text = "Manual"
            mirror_state_text = "Parked"
            self._disconnect_raise_lowering()
        elif data.detailedState == DetailedStates.RAISINGENGINEERING:
            mode_state_text = "Manual"
            mirror_state_text = "Raising"
            self._connect_raise_lowering()
        elif data.detailedState == DetailedStates.ACTIVEENGINEERING:
            mode_state_text = "Manual"
            mirror_state_text = "Active"
            self._disconnect_raise_lowering()
        elif data.detailedState == DetailedStates.LOWERINGENGINEERING:
            mode_state_text = "Manual"
            mirror_state_text = "Lowering"
            self._connect_raise_lowering()
        elif data.detailedState == DetailedStates.LOWERINGFAULT:
            mode_state_text = "Automatic"
            mirror_state_text = "Lowering (fault)"
            self._connect_raise_lowering()
        elif data.detailedState == DetailedStates.PROFILEHARDPOINTCORRECTIONS:
            mode_state_text = "Profile hardpoint corrections"
            mirror_state_text = "Active"
            self._disconnect_raise_lowering()
        else:
            warning(
                self,
                "Unknown state",
                f"Unknown state received - {data.detailedState}",
            )
            self._disconnect_raise_lowering()
            return

        self.mode_state_label.setText(mode_state_text)
        self.mirror_state_label.setText(mirror_state_text)
