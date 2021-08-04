from .QTHelpers import setWarningLabel
from lsst.ts.cRIOpy.M1M3FATable import (
    FATABLE,
    FATABLE_ID,
    FATABLE_INDEX,
    FATABLE_XPOSITION,
    FATABLE_YPOSITION,
    FATABLE_ORIENTATION,
)
from .ForceActuatorWidget import ForceActuatorWidget
from .ActuatorsDisplay import MirrorWidget, ForceActuator


class ForceActuatorGraphPageWidget(ForceActuatorWidget):
    """
    Draw distribution of force actuators, and selected value. Intercept events callbacks to trigger updates.
    """

    def __init__(self, m1m3):
        self.mirrorWidget = MirrorWidget()
        super().__init__(m1m3, self.mirrorWidget)

        self.mirrorWidget.mirrorView.selectionChanged.connect(
            self.updateSelectedActuator
        )

    def updateValues(self, data):
        warningData = self.m1m3.remote.evt_forceActuatorWarning.get()

        if data is None:
            values = None
        else:
            values = self.field.getValue(data)

        self.mirrorWidget.mirrorView.clear()
        self.mirrorWidget.setScaleType(self.field.scale)

        def getWarning(index):
            return (
                ForceActuator.STATE_WARNING
                if warningData.minorFault[index] or warningData.majorFault[index]
                else ForceActuator.STATE_ACTIVE
            )

        for row in FATABLE:
            index = row[FATABLE_INDEX]
            dataIndex = row[self.field.index]
            if values is None or dataIndex is None:
                state = ForceActuator.STATE_INACTIVE
            elif warningData is not None or dataIndex is None:
                state = getWarning(index)
            else:
                state = ForceActuator.STATE_ACTIVE

            self.mirrorWidget.mirrorView.addForceActuator(
                row[FATABLE_ID],
                index,
                row[FATABLE_XPOSITION] * 1000,
                row[FATABLE_YPOSITION] * 1000,
                row[FATABLE_ORIENTATION],
                None if (values is None or dataIndex is None) else values[dataIndex],
                dataIndex,
                state,
            )

        if values is None:
            self.mirrorWidget.setRange(0, 0)
            return

        self.mirrorWidget.setRange(min(values), max(values))

        if self.mirrorWidget.mirrorView.selected is not None:
            self.selectedActuatorValueLabel.setText(
                str(values[self.mirrorWidget.mirrorView.selected.dataIndex])
            )
            if warningData is not None:
                setWarningLabel(
                    self.selectedActuatorWarningLabel,
                    getWarning(self.mirrorWidget.mirrorView.selected.index),
                )
