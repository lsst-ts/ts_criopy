from .QTHelpers import setWarningLabel
from .CustomLabels import Force, Moment, Arcsec, Mm, LogEventWarning, Heartbeat

from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QGridLayout
from PySide2.QtCore import Slot


class OverviewPageWidget(QWidget):
    POSITIONS = [
        "xPosition",
        "yPosition",
        "zPosition",
        "xRotation",
        "yRotation",
        "zRotation",
    ]

    FORCES = ["fx", "fy", "fz", "mx", "my", "mz", "forceMagnitude"]

    def __init__(self, m1m3, mtmount):
        super().__init__()

        self.layout = QHBoxLayout()
        dataLayout = QGridLayout()
        self.layout.addLayout(dataLayout)
        self.setLayout(self.layout)

        self.summaryStateLabel = QLabel("UNKNOWN")
        self.mirrorStateLabel = QLabel("UNKNOWN")
        self.modeStateLabel = QLabel("UNKNOWN")
        self.errorCodeLabel = QLabel("---")
        self.interlockWarningLabel = QLabel("UNKNOWN")
        self.powerWarningLabel = QLabel("UNKNOWN")
        self.forceActuatorWarningLabel = LogEventWarning(m1m3.forceActuatorWarning)
        self.hardpointActuatorWarningLabel = QLabel("UNKNOWN")
        self.hardpointMonitorWarningLabel = QLabel("UNKNOWN")
        self.inclinometerWarningLabel = QLabel("UNKNOWN")
        self.accelerometerWarningLabel = QLabel("UNKNOWN")
        self.gyroWarningLabel = QLabel("UNKNOWN")
        self.airSupplyWarningLabel = QLabel("UNKNOWN")
        self.imsWarningLabel = QLabel("UNKNOWN")
        self.cellLightWarningLabel = QLabel("UNKNOWN")
        self.heartbeatLabel = Heartbeat()

        def createForcesAndMoments():
            return {
                "fx": Force(),
                "fy": Force(),
                "fz": Force(),
                "mx": Moment(),
                "my": Moment(),
                "mz": Moment(),
                "forceMagnitude": Force(),
            }

        def createXYR():
            return {
                "xPosition": Mm(),
                "yPosition": Mm(),
                "zPosition": Mm(),
                "xRotation": Arcsec(),
                "yRotation": Arcsec(),
                "zRotation": Arcsec(),
            }

        def addLabelRow(labels, row, col):
            for label in labels:
                dataLayout.addWidget(QLabel(f"<b>{label}</b>"), row, col)
                col += 1

        def addDataRow(variables, row, col):
            for k, v in variables.items():
                dataLayout.addWidget(v, row, col)
                col += 1

        self.faCommanded = createForcesAndMoments()
        self.faMeasured = createForcesAndMoments()
        self.hpMeasured = createForcesAndMoments()

        self.hpPosition = createXYR()
        self.imsPosition = createXYR()

        self.accelationXLabel = QLabel("UNKNOWN")
        self.accelationYLabel = QLabel("UNKNOWN")
        self.accelationZLabel = QLabel("UNKNOWN")
        self.velocityXLabel = QLabel("UNKNOWN")
        self.velocityYLabel = QLabel("UNKNOWN")
        self.velocityZLabel = QLabel("UNKNOWN")
        self.airCommandLabel = QLabel("UNKNOWN")
        self.airValveLabel = QLabel("UNKNOWN")
        self.inclinometerElevationLabel = QLabel("UNKNOWN")
        self.tmaAzimuthLabel = QLabel("UNKNOWN")
        self.tmaElevationLabel = QLabel("UNKNOWN")

        self.cscVersion = QLabel("---")
        self.salVersion = QLabel("---")
        self.xmlVersion = QLabel("---")
        self.osplVersion = QLabel("---")

        row = 0
        col = 0
        dataLayout.addWidget(QLabel("Summary State"), row, col)
        dataLayout.addWidget(self.summaryStateLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Mirror State"), row, col)
        dataLayout.addWidget(self.mirrorStateLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Mode State"), row, col)
        dataLayout.addWidget(self.modeStateLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("ErrorCode"), row, col)
        dataLayout.addWidget(self.errorCodeLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Interlocks"), row, col)
        dataLayout.addWidget(self.interlockWarningLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Power"), row, col)
        dataLayout.addWidget(self.powerWarningLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Force Actuators"), row, col)
        dataLayout.addWidget(self.forceActuatorWarningLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Hardpoint Actuators"), row, col)
        dataLayout.addWidget(self.hardpointActuatorWarningLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Hardpoint Monitors"), row, col)
        dataLayout.addWidget(self.hardpointMonitorWarningLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Inclinometer"), row, col)
        dataLayout.addWidget(self.inclinometerWarningLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Accelerometer"), row, col)
        dataLayout.addWidget(self.accelerometerWarningLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Gyro"), row, col)
        dataLayout.addWidget(self.gyroWarningLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Air Supply"), row, col)
        dataLayout.addWidget(self.airSupplyWarningLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("IMS"), row, col)
        dataLayout.addWidget(self.imsWarningLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Cell Light"), row, col)
        dataLayout.addWidget(self.cellLightWarningLabel, row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Heartbeat"), row, col)
        dataLayout.addWidget(self.heartbeatLabel, row, col + 1)

        row = 0
        col = 2
        dataLayout.addWidget(QLabel("<b>Forces</b>"), row, col)
        addLabelRow(["X", "Y", "Z", "Mx", "My", "Mz", "Magnitude"], row, col + 1)

        row += 1
        dataLayout.addWidget(QLabel("<b>Commanded</b>"), row, col)
        addDataRow(self.faCommanded, row, col + 1)
        row += 1

        dataLayout.addWidget(QLabel("<b>Measured</b>"), row, col)
        addDataRow(self.faMeasured, row, col + 1)

        row += 1
        dataLayout.addWidget(QLabel("<b>Hardpoints</b>"), row, col)
        addDataRow(self.hpMeasured, row, col + 1)

        row += 1
        dataLayout.addWidget(QLabel("<b>Mirror Position</b>"), row, col)
        addLabelRow(["X", "Y", "Z", "Rx", "Ry", "Rz"], row, col + 1)

        row += 1
        dataLayout.addWidget(QLabel("<b>Hardpoints</b>"), row, col)
        addDataRow(self.hpPosition, row, col + 1)

        row += 1
        dataLayout.addWidget(QLabel("<b>IMS</b>"), row, col)
        addDataRow(self.imsPosition, row, col + 1)

        row += 1
        dataLayout.addWidget(QLabel("Angular Acceleration"), row, col)
        dataLayout.addWidget(QLabel("X (?)"), row, col + 1)
        dataLayout.addWidget(QLabel("Y (?)"), row, col + 2)
        dataLayout.addWidget(QLabel("Z (?)"), row, col + 3)
        row += 1
        dataLayout.addWidget(self.accelationXLabel, row, col + 1)
        dataLayout.addWidget(self.accelationYLabel, row, col + 2)
        dataLayout.addWidget(self.accelationZLabel, row, col + 3)
        row += 1
        dataLayout.addWidget(QLabel("Angular Velocity"), row, col)
        dataLayout.addWidget(QLabel("X (?)"), row, col + 1)
        dataLayout.addWidget(QLabel("Y (?)"), row, col + 2)
        dataLayout.addWidget(QLabel("Z (?)"), row, col + 3)
        row += 1
        dataLayout.addWidget(self.velocityXLabel, row, col + 1)
        dataLayout.addWidget(self.velocityYLabel, row, col + 2)
        dataLayout.addWidget(self.velocityZLabel, row, col + 3)
        row += 1
        dataLayout.addWidget(QLabel("Air Supply"), row, col)
        dataLayout.addWidget(QLabel("Commanded"), row, col + 1)
        dataLayout.addWidget(QLabel("Valve State"), row, col + 2)
        row += 1
        dataLayout.addWidget(self.airCommandLabel, row, col + 1)
        dataLayout.addWidget(self.airValveLabel, row, col + 2)
        row += 1
        self.inclinometerTMALabel = QLabel("---")
        dataLayout.addWidget(self.inclinometerTMALabel, row, col)
        self.inclinometerLabel = QLabel("M1M3")
        self.tmaLabel = QLabel("TMA")
        dataLayout.addWidget(self.inclinometerLabel, row, col + 1)
        dataLayout.addWidget(self.tmaLabel, row, col + 2)
        row += 1
        dataLayout.addWidget(QLabel("Azimuth (deg)"), row, col)
        dataLayout.addWidget(QLabel("-"), row, col + 1)
        dataLayout.addWidget(self.tmaAzimuthLabel, row, col + 2)
        dataLayout.addWidget(QLabel("<b>CsC</b>"), row, col + 4)
        dataLayout.addWidget(QLabel("<b>SAL</b>"), row, col + 5)
        dataLayout.addWidget(QLabel("<b>XML</b>"), row, col + 6)
        dataLayout.addWidget(QLabel("<b>OSPL</b>"), row, col + 7)
        row += 1
        dataLayout.addWidget(QLabel("Elevation (deg)"), row, col)
        dataLayout.addWidget(self.inclinometerElevationLabel, row, col + 1)
        dataLayout.addWidget(self.tmaElevationLabel, row, col + 2)
        dataLayout.addWidget(QLabel("<b>Version</b>"), row, col + 3)
        dataLayout.addWidget(self.cscVersion, row, col + 4)
        dataLayout.addWidget(self.salVersion, row, col + 5)
        dataLayout.addWidget(self.xmlVersion, row, col + 6)
        dataLayout.addWidget(self.osplVersion, row, col + 7)

        m1m3.accelerometerWarning.connect(self.accelerometerWarning)
        m1m3.airSupplyWarning.connect(self.airSupplyWarning)
        m1m3.appliedForces.connect(self.appliedForces)
        m1m3.cellLightWarning.connect(self.cellLightWarning)
        m1m3.detailedState.connect(self.detailedState)
        m1m3.displacementSensorWarning.connect(self.displacementSensorWarning)
        m1m3.errorCode.connect(self.errorCode)
        m1m3.gyroWarning.connect(self.gyroWarning)
        m1m3.hardpointActuatorWarning.connect(self.hardpointActuatorWarning)
        m1m3.hardpointMonitorWarning.connect(self.hardpointMonitorWarning)
        m1m3.heartbeat.connect(self.heartbeatLabel.heartbeat)
        m1m3.inclinometerSensorWarning.connect(self.inclinometerSensorWarning)
        m1m3.interlockWarning.connect(self.interlockWarning)
        m1m3.powerWarning.connect(self.powerWarning)

        m1m3.accelerometerData.connect(self.accelerometerData)
        m1m3.forceActuatorData.connect(self.forceActuatorData)
        m1m3.gyroData.connect(self.gyroData)
        m1m3.hardpointActuatorData.connect(self.hardpointActuatorData)
        m1m3.imsData.connect(self.imsData)
        m1m3.inclinometerData.connect(self.inclinometerData)
        m1m3.softwareVersions.connect(self.softwareVersions)
        m1m3.forceActuatorSettings.connect(self.forceActuatorSettings)

        mtmount.azimuth.connect(self.azimuth)
        mtmount.elevation.connect(self.elevation)

    def accelerometerWarning(self, data):
        setWarningLabel(self.accelerometerWarningLabel, data.anyWarning)

    @Slot(map)
    def airSupplyWarning(self, data):
        setWarningLabel(self.airSupplyWarningLabel, data.anyWarning)

    def _setValues(self, variables, data):
        for k, v in variables.items():
            v.setValue(getattr(data, k))

    @Slot(map)
    def appliedForces(self, data):
        self._setValues(self.faCommanded, data)

    @Slot(map)
    def cellLightWarning(self, data):
        setWarningLabel(self.cellLightWarningLabel, data.anyWarning)

    @Slot(map)
    def detailedState(self, data):
        # summary state, mirror state, mode
        matrix = [
            ["---", "---", "---"],
            ["Disabled", "Parked", "Automatic"],
            ["Fault", "Parked", "Automatic"],
            ["Offline", "Unknown", "Unknown"],
            ["Standby", "Parked", "Automatic"],
            ["Enabled", "Parked", "Automatic"],
            ["Enabled", "Raising", "Automatic"],
            ["Enabled", "Active", "Automatic"],
            ["Enabled", "Lowering", "Automatic"],
            ["Enabled", "Parked", "Engineering"],
            ["Enabled", "Raising", "Engineering"],
            ["Enabled", "Active", "Engineering"],
            ["Enabled", "Lowering", "Engineering"],
            ["Fault", "Lowering", "Automatic"],
            ["Profile Hardpoint", "Parked", "Profile Hardpoint"],
        ]
        m = matrix[data.detailedState]
        self.summaryStateLabel.setText(m[0])
        self.mirrorStateLabel.setText(m[1])
        self.modeStateLabel.setText(m[2])

    @Slot(map)
    def displacementSensorWarning(self, data):
        setWarningLabel(self.imsWarningLabel, data.anyWarning)

    @Slot(map)
    def errorCode(self, data):
        self.errorCodeLabel.setText(hex(data.errorCode))

    @Slot(map)
    def gyroWarning(self, data):
        setWarningLabel(self.gyroWarningLabel, data.anyWarning)

    @Slot(map)
    def hardpointActuatorWarning(self, data):
        setWarningLabel(self.hardpointActuatorWarningLabel, data.anyWarning)

    @Slot(map)
    def hardpointMonitorWarning(self, data):
        setWarningLabel(self.hardpointMonitorWarningLabel, data.anyWarning)

    @Slot(map)
    def inclinometerSensorWarning(self, data):
        setWarningLabel(self.inclinometerWarningLabel, data.anyWarning)

    @Slot(map)
    def interlockWarning(self, data):
        setWarningLabel(self.interlockWarningLabel, data.anyWarning)

    @Slot(map)
    def powerWarning(self, data):
        setWarningLabel(self.powerWarningLabel, data.anyWarning)

    @Slot(map)
    def accelerometerData(self, data):
        self.accelationXLabel.setText("%0.3f" % (data.angularAccelerationX))
        self.accelationYLabel.setText("%0.3f" % (data.angularAccelerationY))
        self.accelationZLabel.setText("%0.3f" % (data.angularAccelerationZ))

    @Slot(map)
    def forceActuatorData(self, data):
        self._setValues(self.faMeasured, data)

    @Slot(map)
    def gyroData(self, data):
        self.velocityXLabel.setText("%0.3f" % (data.angularVelocityX))
        self.velocityYLabel.setText("%0.3f" % (data.angularVelocityY))
        self.velocityZLabel.setText("%0.3f" % (data.angularVelocityZ))

    @Slot(map)
    def hardpointActuatorData(self, data):
        self._setValues(self.hpMeasured, data)
        self._setValues(self.hpPosition, data)

    @Slot(map)
    def imsData(self, data):
        self._setValues(self.imsPosition, data)

    @Slot(map)
    def inclinometerData(self, data):
        self.inclinometerElevationLabel.setText("%0.3f" % (data.inclinometerAngle))

    @Slot(map)
    def softwareVersions(self, data):
        self.cscVersion.setText(data.cscVersion)
        self.salVersion.setText(data.salVersion)
        self.xmlVersion.setText(data.xmlVersion)
        self.osplVersion.setText(data.openSpliceVersion)

    @Slot(map)
    def forceActuatorSettings(self, data):
        self.inclinometerLabel.setEnabled(data.useInclinometer)
        self.inclinometerElevationLabel.setEnabled(data.useInclinometer)

        self.tmaLabel.setDisabled(data.useInclinometer)
        self.tmaAzimuthLabel.setDisabled(data.useInclinometer)
        self.tmaElevationLabel.setDisabled(data.useInclinometer)

        if data.useInclinometer:
            self.inclinometerTMALabel.setText("<b>Inclinometeri</b>")
        else:
            self.inclinometerTMALabel.setText("<b>TMA</b>")

    @Slot(map)
    def azimuth(self, data):
        self.tmaAzimuthLabel.setText("%0.3f" % (data.actualPosition))

    @Slot(map)
    def elevation(self, data):
        self.tmaElevationLabel.setText("%0.3f" % (data.actualPosition))
