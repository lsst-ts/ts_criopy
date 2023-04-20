# This file is part of M1M3 SS GUI.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["GlycolLoopTemperatureWidget"]

from PySide2.QtWidgets import QFormLayout, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget

from ..GUI import DataDegC, DockWindow


class GlycolLoopTemperatureWidget(DockWindow):
    """DockWindow showing M1M3 Thermal Values.

    Parameters
    ----------
    m1m3ts : `SALComm`
        SALComm object representing M1M3 Termal System.
    """

    def __init__(self, m1m3ts):
        super().__init__("Glycol Loop Temperature")

        outside = QFormLayout()
        outside.addRow(
            "Above mirror",
            DataDegC(m1m3ts.glycolLoopTemperature, "aboveMirrorTemperature"),
        )

        inside = QFormLayout()
        for i in range(1, 4):
            inside.addRow(
                str(i),
                DataDegC(
                    m1m3ts.glycolLoopTemperature, "insideCellTemperature" + str(i)
                ),
            )

        insideBox = QGroupBox("Inside cell")
        insideBox.setLayout(inside)

        left = QVBoxLayout()
        left.addLayout(outside)
        left.addWidget(insideBox)

        glycol = QFormLayout()
        glycol.addRow(
            "Telescope Supply",
            DataDegC(m1m3ts.glycolLoopTemperature, "telescopeCoolantSupplyTemperature"),
        )
        glycol.addRow(
            "Telescope Return",
            DataDegC(m1m3ts.glycolLoopTemperature, "telescopeCoolantReturnTemperature"),
        )
        glycol.addRow(
            "Mirror Supply",
            DataDegC(m1m3ts.glycolLoopTemperature, "mirrorCoolantSupplyTemperature"),
        )
        glycol.addRow(
            "Mirror Return",
            DataDegC(m1m3ts.glycolLoopTemperature, "mirrorCoolantReturnTemperature"),
        )

        right = QGroupBox("Glycol")
        right.setLayout(glycol)

        layout = QHBoxLayout()
        layout.addLayout(left)
        layout.addWidget(right)

        widget = QWidget()
        widget.setLayout(layout)

        self.setWidget(widget)
