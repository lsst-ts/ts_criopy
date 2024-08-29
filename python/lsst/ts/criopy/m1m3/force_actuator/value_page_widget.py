# This file is part of criopy package.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https: //www.lsst.org).
# See the COPYRIGHT file at the top - level directory of this distribution
# for details of code ownership.
#
# This program is free software : you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.If not, see < https:  // www.gnu.org/licenses/>.


from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.tables.m1m3 import FATABLE_ZFA, FATable
from PySide6.QtWidgets import QGridLayout, QLabel, QWidget

from ...salcomm import MetaSAL
from .widget import Widget


class DataWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.forceActuatorLabels = []
        for i in range(FATABLE_ZFA):
            self.forceActuatorLabels.append(QLabel("---"))

        self.layout = QGridLayout()

        row = 0
        col = 0
        self.layout.addWidget(QLabel("0"), row, col + 1)
        self.layout.addWidget(QLabel("1"), row, col + 2)
        self.layout.addWidget(QLabel("2"), row, col + 3)
        self.layout.addWidget(QLabel("3"), row, col + 4)
        self.layout.addWidget(QLabel("4"), row, col + 5)
        self.layout.addWidget(QLabel("5"), row, col + 6)
        self.layout.addWidget(QLabel("6"), row, col + 7)
        self.layout.addWidget(QLabel("7"), row, col + 8)
        self.layout.addWidget(QLabel("8"), row, col + 9)
        self.layout.addWidget(QLabel("9"), row, col + 10)
        row += 1

        self.layout.addWidget(QLabel("100"), row, col)
        for i in range(9):
            self.layout.addWidget(self.forceActuatorLabels[i], row, col + 2 + i)

        row += 1
        self.layout.addWidget(QLabel("110"), row, col)
        for i in range(10):
            self.layout.addWidget(self.forceActuatorLabels[9 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel("120"), row, col)
        for i in range(10):
            self.layout.addWidget(self.forceActuatorLabels[19 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel("130"), row, col)
        for i in range(10):
            self.layout.addWidget(self.forceActuatorLabels[29 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel("140"), row, col)
        for i in range(4):
            self.layout.addWidget(self.forceActuatorLabels[39 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel(" "), row, col)
        row += 1
        self.layout.addWidget(QLabel("200"), row, col)
        for i in range(3):
            self.layout.addWidget(self.forceActuatorLabels[43 + i], row, col + 8 + i)

        row += 1
        self.layout.addWidget(QLabel("210"), row, col)
        for i in range(9):
            self.layout.addWidget(self.forceActuatorLabels[46 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel("220"), row, col)
        for i in range(9):
            self.layout.addWidget(self.forceActuatorLabels[55 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel("230"), row, col)
        for i in range(10):
            self.layout.addWidget(self.forceActuatorLabels[64 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel("240"), row, col)
        for i in range(4):
            self.layout.addWidget(self.forceActuatorLabels[74 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel(" "), row, col)
        row += 1
        self.layout.addWidget(QLabel("300"), row, col)
        for i in range(9):
            self.layout.addWidget(self.forceActuatorLabels[78 + i], row, col + 2 + i)

        row += 1
        self.layout.addWidget(QLabel("310"), row, col)
        for i in range(10):
            self.layout.addWidget(self.forceActuatorLabels[87 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel("320"), row, col)
        for i in range(10):
            self.layout.addWidget(self.forceActuatorLabels[97 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel("330"), row, col)
        for i in range(10):
            self.layout.addWidget(self.forceActuatorLabels[107 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel("340"), row, col)
        for i in range(4):
            self.layout.addWidget(self.forceActuatorLabels[117 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel(" "), row, col)
        row += 1
        self.layout.addWidget(QLabel("400"), row, col)
        for i in range(3):
            self.layout.addWidget(self.forceActuatorLabels[121 + i], row, col + 8 + i)

        row += 1
        self.layout.addWidget(QLabel("410"), row, col)
        for i in range(9):
            self.layout.addWidget(self.forceActuatorLabels[124 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel("420"), row, col)
        for i in range(9):
            self.layout.addWidget(self.forceActuatorLabels[133 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel("430"), row, col)
        for i in range(10):
            self.layout.addWidget(self.forceActuatorLabels[142 + i], row, col + 1 + i)

        row += 1
        self.layout.addWidget(QLabel("440"), row, col)
        for i in range(4):
            self.layout.addWidget(self.forceActuatorLabels[152 + i], row, col + 1 + i)

        self.setLayout(self.layout)


class ValuePageWidget(Widget):
    def __init__(self, m1m3: MetaSAL):
        self.dataWidget = DataWidget()

        super().__init__(m1m3, self.dataWidget)

    def changeValues(self) -> None:
        pass

    def updateValues(self, data: BaseMsgType) -> None:
        if data is None or self.field is None:
            for label in self.dataWidget.forceActuatorLabels:
                label.setText("---")
            return

        i = -1
        values = self.field.getValue(data)
        for row in FATable:
            i += 1
            index = row.get_index(self.field.valueIndex)
            if index is None:
                self.dataWidget.forceActuatorLabels[i].setText("---")
            elif data is not None:
                self.dataWidget.forceActuatorLabels[i].setText(f"{values[index]:.1f}")
            else:
                self.dataWidget.forceActuatorLabels[i].setText("")
