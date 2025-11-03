# This file is part of LSST EUI.
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


from lsst.ts import salobj
from lsst.ts.xml.enums import LaserTracker
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLabel

from .gui.sal import Application, EUIWindow, LogWidget, SALErrorCodeWidget, SALStatusBar
from .lasertracker import OverviewPageWidget
from .salcomm import MetaSAL


class LTEUI(EUIWindow):
    def __init__(self, laser_tracker: MetaSAL):
        super().__init__("LTGUI", [laser_tracker], (700, 400))

        self.add_page("Overview", OverviewPageWidget, laser_tracker)
        self.add_page("SAL Log", LogWidget, laser_tracker)
        self.add_page("SAL Errors", SALErrorCodeWidget, laser_tracker)

        self.status_label = QLabel("Unknown")
        self.t2sa_label = QLabel("---")
        self.laser_status_label = QLabel("---")
        self.setStatusBar(
            SALStatusBar(
                [laser_tracker],
                [self.status_label, self.t2sa_label, self.laser_status_label],
            )
        )

        laser_tracker.summaryState.connect(self.summary_state)
        laser_tracker.t2saStatus.connect(self.t2sa_status)
        laser_tracker.laserStatus.connect(self.laser_status)

    @Slot()
    def summary_state(self, data: salobj.BaseMsgType) -> None:
        self.status_label.setText(self.state_string(salobj.State(data.summaryState)))

    @Slot()
    def t2sa_status(self, data: salobj.BaseMsgType) -> None:
        self.t2sa_label.setText(self.state_string(LaserTracker.T2SAStatus(data.status)))

    @Slot()
    def laser_status(self, data: salobj.BaseMsgType) -> None:
        self.laser_status_label.setText(self.state_string(LaserTracker.LaserStatus(data.status)))


def run() -> None:
    # Create the Qt Application
    app = Application(LTEUI)
    app.add_comm("LaserTracker", index=1)

    app.run()
