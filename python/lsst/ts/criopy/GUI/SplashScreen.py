# This file is part of criopy.
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

import asyncio
import binascii
import time
import traceback

from PySide2.QtCore import QTimer, Slot
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QApplication, QSplashScreen

from ..SALComm import MetaSAL


class SplashScreen(QSplashScreen):
    """Splash screen.

    Parameters
    ----------
    comms : `[SALComm]`
        List of SALComms to use for splash wait.
    show : `bool`
        Really show splash screen? If no, only messages will be printed.

    Subclasses must define three functions:

    started
    -------
    Called when all SALComms are running.

    """

    data = "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"  # noqa: E501

    def __init__(self, *comms: MetaSAL, show: bool = True):
        self.comms = comms
        self._show = show
        self.state = 0

        if self._show:
            pixmap = QPixmap()
            pixmap.loadFromData(binascii.a2b_base64(self.data))
            super().__init__(pixmap)
            self.showMessage("Starting ..")
        else:
            super().__init__()

        self._startTime = time.monotonic()

        self._checkTimer = QTimer()
        self._checkTimer.timeout.connect(self._checkStarted)
        self._checkTimer.start(100 if self._show else 1000)

    @Slot()
    def _checkStarted(self) -> None:
        for comm in self.comms:
            if not comm.remote.salinfo.started:
                if self._show:
                    state = "Starting .. " if self.state == 0 else "Stopping .. "
                    self.showMessage(
                        f"{state} {time.monotonic() - self._startTime:.1f}s"
                    )
                else:
                    print(
                        "Waiting for SAL .."
                        f" {time.monotonic() - self._startTime:.0f}s\r",
                        end="",
                    )
                return

        self._checkTimer.stop()
        self.state = 2

        try:
            self.started(*self.comms)
        except Exception:
            print(traceback.format_exc())
            QApplication.exit(1)

    def stop(self) -> None:
        if not (self.state == 0):
            return

        self.state = 1
        for comm in self.comms:
            comm.remote.start_task.cancel()
        self._checkTimer.stop()
        asyncio.get_event_loop().stop()
