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

from lsst.ts.xml.tables.m1m3 import Scanner

from .gui.sal import Application, EUIWindow, LogWidget, SALErrorCodeWidget, SALStatusBar
from .m1m3ts import (
    CoolantCirculationWidget,
    M1M3TSCSCControlWidget,
    MixingValveWidget,
    PowerPageWidget,
    ThermalScannersWidget,
    ThermalValuePageWidget,
)
from .salcomm import MetaSAL


class EUI(EUIWindow):
    def __init__(
        self,
        m1m3ts: MetaSAL,
        ts_1: MetaSAL,
        ts_2: MetaSAL,
        ts_3: MetaSAL,
        ts_4: MetaSAL,
    ):
        super().__init__(
            "M1M3TSGUI",
            [m1m3ts, ts_1, ts_2, ts_3, ts_4],
            (700, 400),
            M1M3TSCSCControlWidget(m1m3ts),
        )

        self.add_page("Power status", PowerPageWidget, m1m3ts)
        self.add_page("Thermal values", ThermalValuePageWidget, m1m3ts)
        self.add_page("Mixing valve", MixingValveWidget, m1m3ts)
        self.add_page("Coolant circulations", CoolantCirculationWidget, m1m3ts)
        self.add_page(
            "Thermal Scanners",
            ThermalScannersWidget,
            ts_1,
            ts_2,
            ts_3,
            ts_4,
        )
        self.add_page("SAL Log", LogWidget, m1m3ts)
        self.add_page("SAL Errors", SALErrorCodeWidget, m1m3ts)

        self.setStatusBar(SALStatusBar([m1m3ts]))


def run() -> None:
    app = Application(EUI)
    app.add_comm("MTM1M3TS")
    app.add_comm("ESS", index=int(Scanner.TS_01), include=["temperature"])
    app.add_comm("ESS", index=int(Scanner.TS_02), include=["temperature"])
    app.add_comm("ESS", index=int(Scanner.TS_03), include=["temperature"])
    app.add_comm("ESS", index=int(Scanner.TS_04), include=["temperature"])
    app.run()
