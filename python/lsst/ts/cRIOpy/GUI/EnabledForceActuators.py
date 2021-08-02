from lsst.ts.cRIOpy.M1M3FATable import (
    FATABLE,
    FATABLE_ID,
    FATABLE_ZINDEX,
    FATABLE_XPOSITION,
    FATABLE_YPOSITION,
    FATABLE_ORIENTATION,
)
from .ForceActuatorWidget import ForceActuatorWidget
from .ActuatorsDisplay import MirrorWidget, ForceActuator, Scales
from PySide2.QtWidgets import QWidget, QHBoxLayout


class EnabledForceActuators(QWidget):
    def __init__(self, m1m3):
        self.mirrorWidget = MirrorWidget()
        self.mirrorWidget.setScaleType(Scales.ONOFF)
        super().__init__()
        self.m1m3 = m1m3

        layout = QHBoxLayout()
        layout.addWidget(self.mirrorWidget)
        self.setLayout(layout)

        self.m1m3.enabledForceActuators.connect(self.enabledForceActuators)

        self.enabledForceActuators(None)

    def enabledForceActuators(self, data):
        self.mirrorWidget.mirrorView.clear()

        for row in FATABLE:
            index = row[FATABLE_ZINDEX]
            self.mirrorWidget.mirrorView.addForceActuator(
                row[FATABLE_ID],
                row[FATABLE_XPOSITION] * 1000,
                row[FATABLE_YPOSITION] * 1000,
                row[FATABLE_ORIENTATION],
                None if data is None else data[index],
                index,
                ForceActuator.STATE_INACTIVE
                if data is None
                else ForceActuator.STATE_ACTIVE,
            )

        self.mirrorWidget.setColorScale()
