# This file is part of M1M3 TS GUI.
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

__all__ = ["FCUDisplayWidget"]

from lsst.ts.xml.tables.m1m3 import FCUTable
from PySide6.QtWidgets import QWidget

from ..gui.actuatorsdisplay import MirrorWidget
from ..salcomm import MetaSAL


class FCUDisplayWidget(QWidget):
    def __init__(self, m1m3ts: MetaSAL):
        super().__init__()
        self.mirror_widget = MirrorWidget()

        for row in FCUTable:
            self.mirror_widget.mirrorView.add_fcu(row)
