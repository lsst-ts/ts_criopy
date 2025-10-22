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


class LVDTPageWidget(QWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(
            ArrayGrid(
                "",
                [f"<b>{label}</b>" for label in range(6)],
                [
                    ArraySignal(
                        m1m3.hardpointMonitorData,
                        [
                            ArrayItem(
                                "breakawayLVDT",
                                "<b>Breakaway LVDT</b>",
                                partial(FormatLabel, fmt=".04"),
                            ),
                            ArrayItem(
                                "displacementLVDT",
                                "<b>Displacement LVDTt</b>",
                                partial(FormatLabel, fmt=".04"),
                            ),
                        ],
                    )
                ],
                Qt.Horizontal,
            )
        )

        breakawayAxis = Axis("Breakaway LVDT", m1m3.hardpointMonitorData)
        displacementAxis = Axis("Displacement LVDT", m1m3.hardpointMonitorData)
        for hp in range(6):
            breakawayAxis.addArrayValue(f"HP {hp + 1}", "breakawayLVDT", hp)
            displacementAxis.addArrayValue(f"HP {hp + 1}", "displacementLVDT", hp)

        layout.addWidget(ChartWidget(breakawayAxis))
        layout.addWidget(ChartWidget(displacementAxis))

        self.setLayout(layout)
