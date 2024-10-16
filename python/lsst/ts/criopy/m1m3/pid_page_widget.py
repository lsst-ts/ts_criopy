# This file is part of cRIO UIs.
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

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..gui import ArrayGrid, ArrayItem, ArraySignal, FormatLabel
from ..gui.sal import Axis, ChartWidget
from ..salcomm import MetaSAL


class PIDPageWidget(QWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(
            ArrayGrid(
                "",
                ["Fx", "Fy", "Fz", "Mx", "My", "Mz"],
                [
                    ArraySignal(
                        m1m3.pidData,
                        [
                            ArrayItem(
                                "setpoint",
                                "Setpoint",
                                partial(FormatLabel, fmt=".03f"),
                            ),
                            ArrayItem(
                                "measuredPID",
                                "Measured PID",
                                partial(FormatLabel, fmt=".03f"),
                            ),
                            ArrayItem(
                                "error", "Error", partial(FormatLabel, fmt=".03f")
                            ),
                            ArrayItem(
                                "errorT1",
                                "Error T1",
                                partial(FormatLabel, fmt=".03f"),
                            ),
                            ArrayItem(
                                "errorT2",
                                "Error T2",
                                partial(FormatLabel, fmt=".03f"),
                            ),
                            ArrayItem(
                                "control",
                                "Control",
                                partial(FormatLabel, fmt=".03f"),
                            ),
                            ArrayItem(
                                "controlT1",
                                "Control T1",
                                partial(FormatLabel, fmt=".03f"),
                            ),
                            ArrayItem(
                                "controlT2",
                                "Control T2",
                                partial(FormatLabel, fmt=".03f"),
                            ),
                        ],
                    ),
                ],
                Qt.Vertical,
            )
        )

        layout.addWidget(
            ArrayGrid(
                "",
                ["Fx", "Fy", "Fz", "Mx", "My", "Mz"],
                [
                    ArraySignal(
                        m1m3.pidInfo,
                        [
                            ArrayItem(
                                "timestep",
                                "Timestep",
                                partial(FormatLabel, fmt=".03f"),
                            ),
                            ArrayItem("p", "P", partial(FormatLabel, fmt=".03f")),
                            ArrayItem("i", "I", partial(FormatLabel, fmt=".03f")),
                            ArrayItem("d", "D", partial(FormatLabel, fmt=".03f")),
                            ArrayItem(
                                "calculatedA",
                                "Calculated A",
                                partial(FormatLabel, fmt=".03f"),
                            ),
                            ArrayItem(
                                "calculatedB",
                                "Calculated B",
                                partial(FormatLabel, fmt=".03f"),
                            ),
                            ArrayItem(
                                "calculatedC",
                                "Calculated C",
                                partial(FormatLabel, fmt=".03f"),
                            ),
                            ArrayItem(
                                "calculatedD",
                                "Calculated D",
                                partial(FormatLabel, fmt=".03f"),
                            ),
                            ArrayItem(
                                "calculatedE",
                                "Calculated E",
                                partial(FormatLabel, fmt=".03f"),
                            ),
                        ],
                    ),
                ],
                Qt.Vertical,
            )
        )

        axis = Axis("Commanded Force/Moment (N/Nm)", m1m3.pidData)

        for index in range(3):
            name = "XYZ"[index]
            axis.addArrayValue(f"Force {name}", "control", index)

        for index in range(3):
            name = "XYZ"[index]
            axis.addArrayValue(f"Moment {name}", "control", index + 3)

        layout.addWidget(ChartWidget(axis))

        self.setLayout(layout)
