# This file is part of M1M3 GUI.
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

__all__ = ["PowerPageWidget"]

from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..gui import StatusGrid
from ..salcomm import MetaSAL


class PowerPageWidget(QWidget):
    def __init__(self, m1m3ts: MetaSAL):
        super().__init__()
        self.m1m3ts = m1m3ts

        layout = QVBoxLayout()

        status_grid = StatusGrid(
            {
                "fanCoilsHeatersCommandedOn": "Heaters Commanded On",
                "fanCoilsHeatersOn": "Heaters On",
                "coolantPumpCommandedOn": "Pump Commanded On",
                "coolantPumpOn": "Pump On",
            },
            self.m1m3ts.powerStatus,
            2,
        )

        layout.addWidget(status_grid)

        self.setLayout(layout)
