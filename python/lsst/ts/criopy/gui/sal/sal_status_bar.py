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

# You should have received a copy of the GNU General Public License along with
# this program.If not, see <https://www.gnu.org/licenses/>.

from datetime import datetime
from html import escape

from lsst.ts.salobj import BaseMsgType
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QLabel, QStatusBar, QWidget

from ...salcomm import MetaSAL
from ..custom_labels import Heartbeat, SimulationStatus, VLine
from .summary_state_label import SummaryStateLabel

__all__ = ["SALStatusBar"]


class SALStatusBar(QStatusBar):
    """Status bar. Shows heartbeats, errors. Can show detailed state.

    Parameters
    ----------
    comms : `[MetaSAL]`
        SALs for heartbeat displays. ErrorCode from the first SAL will
        be displayed as well.
    states_labels : `QLabel`, optional
        If provided, a label showing detailedState will be added to beginning
        of the StatusBar. If empty, label(s) showing summary state(s) of the
        CSC listed in comms will be added to the beginning of the StatusBar.
    """

    def __init__(self, comms: list[MetaSAL], state_labels: list[QLabel] = []):
        super().__init__()

        if len(state_labels) > 0:
            for state_label in state_labels:
                self.addWidget(state_label)
                self.addWidget(VLine())
        else:
            for c in comms:
                self.addWidget(SummaryStateLabel(c.summaryState))
                self.addWidget(VLine())

        self.settings_label = QLabel("--")
        self.addWidget(self.settings_label)
        self.addWidget(VLine())
        comms[0].configurationApplied.connect(self.configuration_applied)

        self.error_code_label = QLabel()
        self.addWidget(self.error_code_label)

        hb_widget = QWidget()
        hb_layout = QHBoxLayout()
        hb_layout.setContentsMargins(0, 0, 0, 0)
        hb_widget.setLayout(hb_layout)

        for comm in comms:
            hb_layout.addWidget(QLabel(comm.remote.salinfo.name))

            hb_layout.addWidget(VLine())
            hb_layout.addWidget(SimulationStatus(comm))
            hb_layout.addWidget(VLine())

            heart_beat_label = Heartbeat(indicator=False)
            hb_layout.addWidget(heart_beat_label)
            comm.heartbeat.connect(heart_beat_label.heartbeat)
            if not (comm == comms[-1]):
                hb_layout.addWidget(VLine())

        self.addPermanentWidget(VLine())
        self.addPermanentWidget(hb_widget)

        comms[0].errorCode.connect(self.error_code)

    @Slot()
    def detailedState(self, data: BaseMsgType) -> None:
        self.detailedStateLabel.setText(self.detailedStateFunction(data.detailedState))

    @Slot()
    def configuration_applied(self, data: BaseMsgType) -> None:
        self.settings_label.setText(data.version)

    @Slot()
    def error_code(self, data: BaseMsgType) -> None:
        date = datetime.fromtimestamp(data.private_sndStamp).isoformat(sep=" ", timespec="milliseconds")
        self.error_code_label.setText(
            f"{date} [<b>{data.errorCode:06X}</b>] <span style='color:"
            f"{'green' if data.errorCode == 0 else 'red'}"
            f"'>{escape(data.errorReport)}</span>"
        )
