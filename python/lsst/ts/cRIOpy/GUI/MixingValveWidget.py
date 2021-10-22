# This file is part of M1M3 GUI.
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

from PySide2.QtCore import Slot
from PySide2.QtWidgets import QLabel, QFormLayout, QVBoxLayout, QWidget

from .CustomLabels import DockWindow


class MixingValveWidget(DockWindow):
    """Displays Mixing Valve data."""

    def __init__(self, m1m3ts):
        super().__init__("Mixing valve")

        dataLayout = QFormLayout()

        self.rawPosition = QLabel()
        self.position = QLabel()

        dataLayout.addRow("Raw Position", self.rawPosition)
        dataLayout.addRow("Position", self.position)

        layout = QVBoxLayout()
        layout.addLayout(dataLayout)
        layout.addStretch()

        widget = QWidget()
        widget.setLayout(layout)

        self.setWidget(widget)

        m1m3ts.mixingValve.connect(self.mixingValve)

    @Slot(map)
    def mixingValve(self, data):
        self.rawPosition.setText(str(data.rawValvePosition))
        self.position.setText(str(data.valvePosition))
