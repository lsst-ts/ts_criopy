from .ForceActuatorWidget import ForceActuatorWidget
from .ActuatorsDisplay import MirrorWidget, ForceActuator
from PySide2.QtWidgets import QWidget


class EnabledForceActuators(QWidget):
    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3
