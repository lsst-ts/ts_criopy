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

from asyncqt import asyncSlot
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QVBoxLayout, QWidget

from ..GUI import (
    Ampere,
    Hz,
    Volt,
    DockWindow,
    DataFormWidget,
)

from ..GUI.SAL import SALCommand


class PumpWidget(DockWindow):
    """Display Glycol re-circulation pump telemetry, allows motor commanding."""

    def __init__(self, m1m3ts):
        super().__init__("Glycol re-circulation pump")
        self.m1m3ts = m1m3ts

        tellayout = QVBoxLayout()
        tellayout.addWidget(
            DataFormWidget(
                m1m3ts.glycolPump,
                [
                    ("Commanded Frequency", Hz(field="commandedFrequency")),
                    ("Output Frequency", Hz(field="outputFrequency")),
                    ("Output Current", Ampere(field="outputCurrent")),
                    ("Bus Voltage", Volt(field="busVoltage")),
                    ("Output Voltage", Volt(field="outputVoltage")),
                ],
            )
        )

        widget = QWidget()
        widget.setLayout(tellayout)

        self.setWidget(widget)
