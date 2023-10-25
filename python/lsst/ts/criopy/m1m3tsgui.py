#!/usr/bin/env python

# This file is part of M1M3 TS GUI.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from .gui.sal import Application, EUIWindow, LogWidget, SALErrorCodeWidget, SALStatusBar
from .m1m3ts import (
    CoolantCirculationWidget,
    M1M3TSCSCControlWidget,
    MixingValveWidget,
    ThermalValuePageWidget,
)
from .salcomm import MetaSAL


class EUI(EUIWindow):
    def __init__(self, m1m3ts: MetaSAL):
        super().__init__(
            "M1M3TSGUI", [m1m3ts], (700, 400), M1M3TSCSCControlWidget(m1m3ts)
        )

        self.m1m3ts = m1m3ts

        self.add_page("Thermal values", ThermalValuePageWidget, self.m1m3ts)
        self.add_page("Mixing valve", MixingValveWidget, self.m1m3ts)
        self.add_page("Coolant circulations", CoolantCirculationWidget, self.m1m3ts)
        self.add_page("SAL Log", LogWidget, self.m1m3ts)
        self.add_page("SAL Errors", SALErrorCodeWidget, self.m1m3ts)

        self.setStatusBar(SALStatusBar([self.m1m3ts]))


def run() -> None:
    app = Application(EUI)
    app.addComm("MTM1M3TS")
    app.run()
