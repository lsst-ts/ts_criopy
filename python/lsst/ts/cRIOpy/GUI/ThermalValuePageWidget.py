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

from PySide2.QtWidgets import QTableWidget, QTableWidgetItem
from .TopicWindow import TopicWindow
from .ThermalData import Thermals


class DataWidget(QTableWidget):
    def __init__(self):
        super().__init__(10, 10)
        for r in range(0, 10):
            for c in range(0, 10):
                item = QTableWidgetItem("")
                self.setItem(r, c, item)
        self.empty()

    def empty(self):
        for r in range(0, 10):
            for c in range(0, 10):
                self.item(r, c).setText(str(r * 10 + c))


class ThermalValuePageWidget(TopicWindow):
    def __init__(self, m1m3ts):
        self.dataWidget = DataWidget()

        super().__init__("Thermals values", m1m3ts, Thermals(), self.dataWidget)

    def updateValues(self, data):
        if data is None:
            self.dataWidget.empty()
            return

        values = self.field.getValue(data)

        for r in range(0, 10):
            for c in range(0, 10):
                index = r * 10 + c
                if index < 96:
                    self.dataWidget.item(r, c).setText(str(values[index]))
