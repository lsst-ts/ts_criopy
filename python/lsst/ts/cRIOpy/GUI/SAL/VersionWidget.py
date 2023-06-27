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

from ...SALComm import MetaSAL
from ..CustomLabels import DataLabel
from ..DataFormWidget import DataFormWidget

__all__ = ["VersionWidget"]


class VersionWidget(DataFormWidget):
    """Shows widget with CSC data - versions, simulation mode, .."""

    def __init__(self, remote: MetaSAL, simulationMode: bool = True):
        """
        Parameters
        ----------
        showSimulationMode : `bool`, optional
            If true (the default), shows simulationMode.mode value.
        """
        super().__init__(
            remote.softwareVersions,
            [
                ("CSC Version", DataLabel(field="cscVersion")),
                ("XML Version", DataLabel(field="xmlVersion")),
                ("SAL Version", DataLabel(field="salVersion")),
                ("OpenSplice Version", DataLabel(field="openSpliceVersion")),
                ("Subsystem Versions", DataLabel(field="subsystemVersions")),
            ],
        )
        if simulationMode:
            self.layout().addRow(
                "Simulation mode",
                DataLabel(signal=remote.simulationMode, field="mode"),
            )
