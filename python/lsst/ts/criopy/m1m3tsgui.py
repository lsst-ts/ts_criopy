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

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QLabel

from lsst.ts.salobj import BaseMsgType

from .gui.sal import Application, EUIWindow, LogWidget, SALErrorCodeWidget, SALStatusBar, SummaryStateLabel
from .m1m3ts import (
    CoolantCirculationWidget,
    FCUDisplayWidget,
    M1M3TSCSCControlWidget,
    MixingValveWidget,
    PowerPageWidget,
    ScannersWidget,
    ThermalValuePageWidget,
)
from .salcomm import MetaSAL


class EngineeringMode(QLabel):
    def __init__(self, m1m3ts: MetaSAL):
        super().__init__()
        m1m3ts.engineeringMode.connect(self.engineering_mode)

    @Slot()
    def engineering_mode(self, data: BaseMsgType) -> None:
        self.setText(
            "<font color='red'>Engineering</font>"
            if data.engineeringMode
            else "<font color='green'>Non-Engineering</font>"
        )


class EUI(EUIWindow):
    def __init__(self, m1m3ts: MetaSAL, *scanners: MetaSAL):
        super().__init__("M1M3TSGUI", [m1m3ts] + list(scanners), (700, 400), M1M3TSCSCControlWidget(m1m3ts))

        self.m1m3ts = m1m3ts

        self.add_page("Power status", PowerPageWidget, self.m1m3ts)
        self.add_page("FCU display", FCUDisplayWidget, self.m1m3ts)
        self.add_page("Thermal values", ThermalValuePageWidget, self.m1m3ts)
        self.add_page("Mixing valve", MixingValveWidget, self.m1m3ts)
        self.add_page("Coolant circulations", CoolantCirculationWidget, self.m1m3ts)
        self.add_page("Glass Temperatures", ScannersWidget, scanners)
        self.add_page("SAL Log", LogWidget, self.m1m3ts)
        self.add_page("SAL Errors", SALErrorCodeWidget, self.m1m3ts)

        self.setStatusBar(
            SALStatusBar(
                [self.m1m3ts] + list(scanners),
                [SummaryStateLabel(self.m1m3ts.summaryState), EngineeringMode(self.m1m3ts)]
                + [SummaryStateLabel(sc.summaryState) for sc in scanners],
            )
        )


def run() -> None:
    app = Application(EUI)
    app.add_comm("MTM1M3TS")
    for index in range(114, 118):
        app.add_comm("ESS", index=index)
    app.run()
