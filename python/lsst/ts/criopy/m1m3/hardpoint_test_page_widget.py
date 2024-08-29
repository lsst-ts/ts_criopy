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

from functools import partial

from lsst.ts.xml.enums.MTM1M3 import HardpointTest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..gui import (
    ArrayButton,
    ArrayGrid,
    ArrayItem,
    ArraySignal,
    EnumLabel,
    Force,
    Mm,
    TimeChartView,
    UserSelectedTimeChart,
)
from ..salcomm import MetaSAL


class HardpointTestPageWidget(QWidget):
    """
    User interface for hardpoint testing. Includes buttons to run the tests,
    Show test progress,

    Parameters
    ----------
    m1m3 : `MetaSAL`
        SALComm communication object.
    """

    def __init__(self, m1m3: MetaSAL):
        super().__init__()

        layout = QVBoxLayout()

        chart = UserSelectedTimeChart(
            {
                m1m3.remote.tel_hardpointActuatorData: m1m3.hardpointActuatorData,
                m1m3.remote.evt_hardpointTestStatus: m1m3.hardpointTestStatus,
            }
        )

        testLabel = partial(
            EnumLabel,
            {
                HardpointTest.NOTTESTED: "<font color='gray'>Not tested</font>",
                HardpointTest.MOVINGNEGATIVE: (
                    "<font color='blue'>Moving negative</font>"
                ),
                HardpointTest.TESTINGPOSITIVE: (
                    "<font color='orange'>Testing positive</font>"
                ),
                HardpointTest.TESTINGNEGATIVE: (
                    "<font color='lime'>Testing negative</font>"
                ),
                HardpointTest.MOVINGREFERENCE: (
                    "<font color='blue'>Moving to reference</font>"
                ),
                HardpointTest.PASSED: "<font color='green'>Passed</font>",
                HardpointTest.FAILED: "<font color='red'>Failed</font>",
            },
        )

        layout.addWidget(
            ArrayGrid(
                "<b>Hardpoint</b>",
                [f"<b>{x}</b>" for x in range(1, 7)],
                [
                    ArraySignal(
                        m1m3.hardpointActuatorData,
                        [
                            ArrayItem("stepsQueued", "Steps queued"),
                            ArrayItem(
                                "stepsCommanded",
                                "Steps commanded",
                            ),
                            ArrayItem("encoder", "Encoder"),
                            ArrayItem(
                                "measuredForce",
                                "Measured force",
                                partial(Force, fmt=".03f"),
                            ),
                            ArrayItem(
                                "displacement",
                                "Displacement",
                                Mm,
                            ),
                        ],
                    ),
                    ArrayItem(
                        "testState",
                        "Test state",
                        testLabel,
                        m1m3.hardpointTestStatus,
                    ),
                    ArrayButton(
                        lambda i: m1m3.remote.cmd_testHardpoint.set_start(
                            hardpointActuator=i + 1
                        ),
                        "Start test",
                    ),
                    ArrayButton(
                        lambda i: m1m3.remote.cmd_killHardpointTest.set_start(
                            hardpointActuator=i + 1
                        ),
                        "Abort",
                    ),
                ],
                Qt.Vertical,
                chart,
            )
        )

        layout.addWidget(TimeChartView(chart))

        self.setLayout(layout)
