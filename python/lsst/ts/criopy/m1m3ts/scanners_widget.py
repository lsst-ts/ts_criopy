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

import re

from ..salcomm import MetaSAL

from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.tables.m1m3 import Scanner, find_thermocouple, ThermocoupleData
from PySide6.QtWidgets import QWidget, QVBoxLayout

from ..gui.actuatorsdisplay import MirrorWidget, DataItemState


class ScannersWidget(QWidget):
    def __init__(self, scanners: list[MetaSAL]):
        super().__init__()
        self.mirror_widget = MirrorWidget(scanners=True, fmt=".03f")

        layout = QVBoxLayout()
        layout.addWidget(self.mirror_widget)

        self.setLayout(layout)

        for scanner in scanners:
            scanner.temperature.connect(self._temperature)

    def _temperature(self, data: BaseMsgType) -> None:
        values: list[tuple[ThermocoupleData, float]] = []
        chunk = re.compile(r"m1m3-ts-0\d (\d+)/\d+").match(data.sensorName)
        assert chunk is not None, f"Invalid sensorName: {data.sensorName} index: {data.salIndex}."
        sensor_index = int(chunk[1]) - 1
        for i, v in enumerate(data.temperatureItem):
            tc = find_thermocouple(Scanner(data.salIndex), sensor_index * 16 + i)
            if tc is not None:
                values.append((tc, v))

        if len(values) > 0:
            self.mirror_widget.mirror_view.update_scanner(values, DataItemState.ACTIVE)

        self.mirror_widget.set_range(*self.mirror_widget.mirror_view.get_scanner_range())

        for scanner in self.mirror_widget.mirror_view._mirror.scanners:
            scanner.update()
