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

from .CustomLabels import VLine, Heartbeat

from PySide2.QtCore import Slot
from PySide2.QtWidgets import QStatusBar, QLabel, QWidget, QHBoxLayout

from datetime import datetime

__all__ = ["SALStatusBar"]


class SALStatusBar(QStatusBar):
    """Status bar. Shows heartbeats, errors. Can show detailed state.

    Parameters
    ----------
    comms : `[SALComm]`
        SALComms for heartbeat displays. ErrorCode from the first SALComm will be displayed as well.
    detailedStateFunction : `def(int)`, optional
        If provided, a label showing detailedState (result of
        detailedStateFunction call with detailedState as argument) will be
        added to beginning of the StatusBar.
    """

    def __init__(self, comms, detailedStateFunction=None):
        super().__init__()

        if detailedStateFunction is not None:
            self.detailedStateLabel = QLabel("---")
            self.detailedStateFunction = detailedStateFunction
            self.addWidget(self.detailedStateLabel)
            comms[0].detailedState.connect(self.detailedState)
            self.addWidget(VLine())

        self.errorCodeLabel = QLabel()
        self.addWidget(self.errorCodeLabel)

        hbWidget = QWidget()
        hbLayout = QHBoxLayout()
        hbLayout.setMargin(0)
        hbWidget.setLayout(hbLayout)

        for comm in comms:
            hbLayout.addWidget(QLabel(comm.remote.salinfo.name))
            heartBeatLabel = Heartbeat(indicator=False)
            hbLayout.addWidget(heartBeatLabel)
            comm.heartbeat.connect(heartBeatLabel.heartbeat)
            if not (comm == comms[-1]):
                hbLayout.addWidget(VLine())

        self.addPermanentWidget(VLine())
        self.addPermanentWidget(hbWidget)

        comms[0].errorCode.connect(self.errorCode)

    @Slot(map)
    def detailedState(self, data):
        self.detailedStateLabel.setText(self.detailedStateFunction(data.detailedState))

    @Slot(map)
    def errorCode(self, data):
        date = datetime.fromtimestamp(data.private_sndStamp).isoformat(
            sep=" ", timespec="milliseconds"
        )
        self.errorCodeLabel.setText(
            f"{date} [<b>{data.errorCode:06X}</b>] <span style='color:{'green' if data.errorCode==0 else 'red'}'>{data.errorReport}</span>"
        )
