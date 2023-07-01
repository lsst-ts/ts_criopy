# This file is part of cRIO/VMS GUI.
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

# You should have received a copy of the GNU General Public License along with
# this program.If not, see <https://www.gnu.org/licenses/>.

from PySide2.QtWidgets import QFormLayout, QWidget

from ..GUI.CustomLabels import DataDegC, DataLabel, DockWindow, OnOffLabel, WarningLabel
from ..salcomm import MetaSAL


class MiscellaneousWidget(DockWindow):
    """Display miscellaneous data."""

    def __init__(self, title: str, vms: MetaSAL):
        super().__init__(title)
        widget = QWidget()
        layout = QFormLayout()
        layout.addRow(
            "Chassis temperature",
            DataDegC(vms.miscellaneous, "chassisTemperature"),
        )
        layout.addRow("Ticks", DataLabel(vms.miscellaneous, "ticks"))
        layout.addRow("Ready", OnOffLabel(vms.fpgaState, "ready"))
        layout.addRow("Timeouted", WarningLabel(vms.fpgaState, "timeouted"))
        layout.addRow("Stopped", WarningLabel(vms.fpgaState, "stopped"))
        layout.addRow("FIFO full", WarningLabel(vms.fpgaState, "fifoFull"))
        widget.setLayout(layout)
        self.setWidget(widget)
