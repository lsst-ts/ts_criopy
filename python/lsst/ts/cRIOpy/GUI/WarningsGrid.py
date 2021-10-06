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

from .CustomLabels import WarningLabel

from PySide2.QtWidgets import QGroupBox, QGridLayout, QLabel
from PySide2.QtCore import Slot


class WarningsGrid(QGroupBox):
    def __init__(self, warnings, event, cols):
        super().__init__("Any Warnings: ---")
        self.warnings = {}

        layout = QGridLayout()

        lw = len(warnings)
        rows = lw / cols
        i = 0
        for w in warnings.items():
            r = i % rows
            c = int(i / rows) * 2
            i += 1

            layout.addWidget(QLabel(w[1]), r, c)

            label = WarningLabel()
            layout.addWidget(label, r, c + 1)

            self.warnings[w[0]] = label

        self.setLayout(layout)

        event.connect(self.data)

    @Slot(map)
    def data(self, data):
        if data.anyWarning:
            self.setTitle("<font color='red'>Any Warning: yes</font>")
        else:
            self.setTitle("<font color='green'>Any Warning: no</font>")

        for w in self.warnings:
            w[1].setValue(getattr(data, w[0]))
