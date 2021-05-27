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

        for r in range(0, 10):
            for c in range(0, 10):
                index = r * 10 + c
                if index < 96:
                    self.dataWidget.item(r, c).setText(
                        str(self.fieldGetter(data)[index])
                    )
