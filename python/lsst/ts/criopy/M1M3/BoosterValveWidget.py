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

import typing

import numpy as np
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QFormLayout, QGridLayout, QWidget

from ..GUI import DegS2, Force, OnOffLabel, TimeChart, TimeChartView
from ..GUI.SAL import Axis, ChartWidget
from ..SALComm import MetaSAL

__all__ = ["BoosterValveWidget"]


class FollowingErrorTrigger(QWidget):
    """
    Display FAs following errors parameters relevant for booster valve
    triggering.

    Parameters
    ----------
    m1m3 : `SALComm`
        M1M3 SAL remote.
    """

    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        layout = QGridLayout()

        operationalLayout = QFormLayout()

        operationalLayout.addRow(
            "Following Error Trigger Enabled",
            OnOffLabel(m1m3.boosterValveSettings, "followingErrorTriggerEnabled"),
        )
        operationalLayout.addRow(
            "Open",
            Force(m1m3.boosterValveSettings, "followingErrorTriggerOpen"),
        )
        operationalLayout.addRow(
            "Close",
            Force(m1m3.boosterValveSettings, "followingErrorTriggerClose"),
        )
        operationalLayout.addRow(
            "Slew Flag", OnOffLabel(m1m3.boosterValveStatus, "slewFlag")
        )
        operationalLayout.addRow(
            "Following Error Triggered",
            OnOffLabel(m1m3.boosterValveStatus, "followingErrorTriggered"),
        )

        layout.addLayout(operationalLayout, 0, 0)

        dataLayout = QFormLayout()

        self._pmax = Force()
        self._pmin = Force()
        self._smax = Force()
        self._smin = Force()

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

    @Slot()
    def _forceActuatorData(self, data: typing.Any) -> None:
        primaryFEMax = np.max(data.primaryCylinderFollowingError)
        primaryFEMin = np.min(data.primaryCylinderFollowingError)

        secondaryFEMax = np.max(data.secondaryCylinderFollowingError)
        secondaryFEMin = np.min(data.secondaryCylinderFollowingError)

        self.__followingErrorChart.append(
            data.timestamp,
            [primaryFEMax, primaryFEMin, secondaryFEMax, secondaryFEMin],
        )

        self._pmax.setValue(primaryFEMax)
        self._pmin.setValue(primaryFEMin)
        self._smax.setValue(secondaryFEMax)
        self._smin.setValue(secondaryFEMin)


class Accelerometer(QWidget):
    """
    Display DC accelerometer values relevant for booster valve triggering.

    Parameters
    ----------
    m1m3 : `SALComm`
        M1M3 SAL remote.
    """

    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        layout = QGridLayout()

        operationalLayout = QFormLayout()

        operationalLayout.addRow(
            "Accelerometer Trigger Enabled",
            OnOffLabel(m1m3.boosterValveSettings, "accelerometerTriggerEnabled"),
        )
        for axis in ["X", "Y", "Z"]:
            operationalLayout.addRow(
                f"Open {axis}",
                DegS2(m1m3.boosterValveSettings, f"accelerometer{axis}TriggerOpen"),
            )
            operationalLayout.addRow(
                f"Close {axis}",
                DegS2(
                    m1m3.boosterValveSettings,
                    f"accelerometer{axis}TriggerClose",
                ),
            )
        operationalLayout.addRow(
            "Accelerometer Triggered",
            OnOffLabel(m1m3.boosterValveStatus, "accelerometerTriggered"),
        )

        layout.addLayout(operationalLayout, 0, 0)

        plotAxis = Axis(
            "Angular Acceleration (deg/s<sup>2</sup>)", m1m3.accelerometerData
        )

        dataLayout = QFormLayout()

        for axis in ["X", "Y", "Z"]:
            dataLayout.addRow(
                f"Angular {axis}",
                DegS2(m1m3.accelerometerData, f"angularAcceleration{axis}"),
            )
            plotAxis.addValue(f"{axis}", f"angularAcceleration{axis}")

        layout.addLayout(dataLayout, 0, 1)

        layout.addWidget(ChartWidget(plotAxis), 1, 0, 1, 2)

        self.setLayout(layout)


class BoosterValveWidget(QWidget):
    """
    Widget showing values important for booster valve control.

    Parameters
    ----------
    m1m3 : `SALComm`
        M1M3 SAL remote.
    """

    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        layout = QGridLayout()

        layout.addWidget(FollowingErrorTrigger(m1m3), 0, 0)
        layout.addWidget(Accelerometer(m1m3), 1, 0)

        self.setLayout(layout)
