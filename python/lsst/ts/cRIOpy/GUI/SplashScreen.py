# This file is part of cRIOpy.
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

__all__ = ["SplashScreen"]

from PySide2.QtWidgets import QSplashScreen
from PySide2.QtCore import QTimer, Slot

import time


class SplashScreen(QSplashScreen):
    """Splash screen.

    Subclasses must define three functions:

    setup
    -----
    Called to setup SALComms. Must return comms in array.

    started
    -------
    Called when all SALComms are running.
    """

    def __init__(self):
        super().__init__()

        self.comms = self.setup()

        self._startTime = time.monotonic()

        self._checkTimer = QTimer()
        self._checkTimer.timeout.connect(self._checkStarted)
        self._checkTimer.start(100)

    @Slot()
    def _checkStarted(self):
        for comm in self.comms:
            if not comm.remote.salinfo.started:
                self.showMessage(
                    f"Starting .. {time.monotonic() - self._startTime:.1f}s"
                )
                return

        self._checkTimer.stop()

        self.started(*self.comms)
