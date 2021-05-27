from PySide2.QtWidgets import QWidget, QGridLayout, QLabel

from lsst.ts.cRIOpy.M1M3FATable import *
from .ForceActuatorWidget import ForceActuatorWidget


class DataWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.forceActuatorLabels = []
        for i in range(156):
            self.forceActuatorLabels.append(QLabel("UNKNOWN"))

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


class ForceActuatorValuePageWidget(ForceActuatorWidget):
    def __init__(self, m1m3):
        self.dataWidget = DataWidget()

        super().__init__(m1m3, self.dataWidget)

    def updateValues(self, data):
        if data is None:
            for l in self.dataWidget.forceActuatorLabels:
                l.setText("UNKNOWN")
            return

        i = -1
        for row in FATABLE:
            i += 1
            index = row[self.fieldDataIndex]
            # warning = False
            # if self.actuatorWarningData is not None:
            #    warning = self.actuatorWarningData.forceActuatorFlags[row[FATABLE_INDEX]] != 0
            if index is None:
                self.dataWidget.forceActuatorLabels[i].setText("UNKNOWN")
            elif data is not None:
                self.dataWidget.forceActuatorLabels[i].setText(
                    "%0.1f" % self.fieldGetter(data)[index]
                )
            else:
                self.dataWidget.forceActuatorLabels[i].setText("")
