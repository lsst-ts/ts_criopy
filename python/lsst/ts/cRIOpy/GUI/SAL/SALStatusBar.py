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

import typing
from datetime import datetime
from html import escape

from PySide2.QtCore import Slot
from PySide2.QtWidgets import QHBoxLayout, QLabel, QStatusBar, QWidget

from ..CustomLabels import Heartbeat, SimulationStatus, VLine

__all__ = ["SALStatusBar"]


class SALStatusBar(QStatusBar):
    """Status bar. Shows heartbeats, errors. Can show detailed state.

    Parameters
    ----------
    comms : `[SALComm]`
        SALComms for heartbeat displays. ErrorCode from the first SALComm will
        be displayed as well.
    stateLabel : `QLabel`, optional
        If provided, aa label showing detailedState (result of
        detailedStateFunction call with detailedState as argument) will be
        added to beginning of the StatusBar.
    """

    def __init__(self, comms, stateLabels: list[QLabel] = []):
        super().__init__()

        for stateLabel in stateLabels:
            self.addWidget(stateLabel)
            self.addWidget(VLine())

        self.settingsLabel = QLabel("--")
        self.addWidget(self.settingsLabel)
        self.addWidget(VLine())
        comms[0].configurationApplied.connect(self.configurationApplied)

        self.errorCodeLabel = QLabel()
        self.addWidget(self.errorCodeLabel)

        hbWidget = QWidget()
        hbLayout = QHBoxLayout()
        hbLayout.setMargin(0)
        hbWidget.setLayout(hbLayout)

        for comm in comms:
            hbLayout.addWidget(QLabel(comm.remote.salinfo.name))

            hbLayout.addWidget(VLine())
            hbLayout.addWidget(SimulationStatus(comm))
            hbLayout.addWidget(VLine())

            heartBeatLabel = Heartbeat(indicator=False)
            hbLayout.addWidget(heartBeatLabel)
            comm.heartbeat.connect(heartBeatLabel.heartbeat)
            if not (comm == comms[-1]):
                hbLayout.addWidget(VLine())

        self.addPermanentWidget(VLine())
        self.addPermanentWidget(hbWidget)

        comms[0].errorCode.connect(self.errorCode)

    @Slot()
    def detailedState(self, data: typing.Any) -> None:
        self.detailedStateLabel.setText(self.detailedStateFunction(data.detailedState))

    @Slot()
    def configurationApplied(self, data: typing.Any) -> None:
        self.settingsLabel.setText(data.version)

    @Slot()
    def errorCode(self, data: typing.Any) -> None:
        date = datetime.fromtimestamp(data.private_sndStamp).isoformat(
            sep=" ", timespec="milliseconds"
        )
        self.errorCodeLabel.setText(
            f"{date} [<b>{data.errorCode:06X}</b>] <span style='color:"
            f"{'green' if data.errorCode==0 else 'red'}"
            f"'>{escape(data.errorReport)}</span>"
        )
