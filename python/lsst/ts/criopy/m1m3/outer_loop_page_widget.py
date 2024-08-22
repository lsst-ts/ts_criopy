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

import astropy.units as u
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from ..gui import DataFormWidget, MaxMilliSeconds, MilliSeconds, MinMilliSeconds
from ..gui.sal import Axis, ChartWidget
from ..salcomm import MetaSAL


class OuterLoopPageWidget(QWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()

        layout = QVBoxLayout()

        self.statistics = [
            MinMilliSeconds(field="executionTime"),
            MaxMilliSeconds(field="executionTime"),
        ]

        values = QHBoxLayout()
        values.addWidget(
            DataFormWidget(
                m1m3.outerLoopData,
                [
                    ("Execution time", MilliSeconds(field="executionTime")),
                    ("Min", self.statistics[0]),
                    ("Max", self.statistics[1]),
                ],
            )
        )

        reset_button = QPushButton("&Reset statistics")
        reset_button.clicked.connect(self.reset)

        values.addWidget(reset_button)

        layout.addLayout(values)

        layout.addSpacing(30)

        axis = Axis("Time (s)", m1m3.outerLoopData)
        axis.addValue("Execution time", "executionTime", u.s.to(u.ms))

        layout.addWidget(ChartWidget(axis))

        self.setLayout(layout)

    @Slot()
    def reset(self) -> None:
        [s.resetFormat.emit() for s in self.statistics]
