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
#
# You should have received a copy of the GNU General Public License along with
# this program.If not, see <https://www.gnu.org/licenses/>.

import numpy as np
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QFormLayout, QGridLayout, QLabel, QVBoxLayout, QWidget

from ..GUI import DegS2, OnOffLabel, TimeChart, TimeChartView

__all__ = ["BoosterValveWidget"]

class FollowingErrorTrigger(QWidget):
    def __init__(self, m1m3):
        super().__init__()
        layout = QGridLayout()

        operationalLayout = QFormLayout()

        operationalLayout.addRow("Following Error Enabled", OnOffLabel(m1m3.boosterValveSettings, "followingErrorTriggerEnabled"))
        operationalLayout.addRow("Open", DegS2(m1m3.boosterValveSettings, "followingErrorTriggerOpen"))
        operationalLayout.addRow("Close", DegS2(m1m3.boosterValveSettings, "followingErrorTriggerClose"))
        operationalLayout.addRow("Slew Flag", OnOffLabel(m1m3.boosterValveStatus, "slewFlag"))
        operationalLayout.addRow("Following Error Triggered", OnOffLabel(m1m3.boosterValveStatus, "followingErrorTriggered"))

        layout.addLayout(operationalLayout, 0, 0)

        dataLayout = QFormLayout()

        self._pmax = DegS2()
        self._pmin = DegS2()
        self._smax = DegS2()
        self._smin = DegS2()

        dataLayout.addRow("Primary Max", self._pmax)
        dataLayout.addRow("Primary Min", self._pmin)
        dataLayout.addRow("Secondary Max", self._smax)
        dataLayout.addRow("Secondary Min", self._smin)

        layout.addLayout(dataLayout, 0, 1)

        self.__followingErrorChart = TimeChart(
            {
                "Following Error (N)": [
                    "Primary Max",
                    "Primary Min",
                    "Secondary Max",
                    "Secondary Min",
                ]
            }
        )

        layout.addWidget(TimeChartView(self.__followingErrorChart), 1, 0, 1, 2)

        self.setLayout(layout)

        m1m3.forceActuatorData.connect(self._forceActuatorData)

    @Slot(map)
    def _forceActuatorData(self, data):
        primaryFEMax = np.max(data.primaryCylinderFollowingError)
        primaryFEMin = np.min(data.primaryCylinderFollowingError)

        secondaryFEMax = np.max(data.secondaryCylinderFollowingError)
        secondaryFEMin = np.min(data.secondaryCylinderFollowingError)

        self.__followingErrorChart.append(
            data.timestamp, [primaryFEMax, primaryFEMin, secondaryFEMax, secondaryFEMin]
        )

        self._pmax.setValue(primaryFEMax)
        self._pmin.setValue(primaryFEMin)
        self._smax.setValue(secondaryFEMax)
        self._smin.setValue(secondaryFEMin)


class BoosterValveWidget(QWidget):
    """
    Widget showing values important for booster valve control.
    """

    def __init__(self, m1m3):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(FollowingErrorTrigger(m1m3))

        self.setLayout(layout)
