# This file is part of M1M3 SS GUI.
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

from PySide2.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout
from PySide2.QtCore import Slot
import astropy.units as u

from ..GUI import (
    Force,
    Moment,
    Arcsec,
    Mm,
    Heartbeat,
    WarningButton,
)


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

        layout = QVBoxLayout()
        dataLayout = QGridLayout()
        layout.addLayout(dataLayout)
        layout.addStretch()
        self.setLayout(layout)

        self.summaryStateLabel = QLabel("UNKNOWN")
        self.mirrorStateLabel = QLabel("UNKNOWN")
        self.modeStateLabel = QLabel("UNKNOWN")
        self.errorCodeLabel = QLabel("---")
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

        self.broadcastCounter = QLabel("---")
        self.slewFlag = QLabel("---")
        self.executionTime = QLabel("---")

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
        dataLayout.addWidget(WarningButton(m1m3, "interlockWarning"), row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Power"), row, col)
        dataLayout.addWidget(WarningButton(m1m3, "powerWarning"), row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Force Actuators"), row, col)
        dataLayout.addWidget(WarningButton(m1m3, "forceActuatorWarning"), row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Hardpoint Actuators"), row, col)
        dataLayout.addWidget(
            WarningButton(m1m3, "hardpointActuatorWarning"), row, col + 1
        )
        row += 1
        dataLayout.addWidget(QLabel("Hardpoint Monitors"), row, col)
        dataLayout.addWidget(
            WarningButton(m1m3, "hardpointMonitorWarning"), row, col + 1
        )
        row += 1
        dataLayout.addWidget(QLabel("Inclinometer"), row, col)
        dataLayout.addWidget(
            WarningButton(m1m3, "inclinometerSensorWarning"), row, col + 1
        )
        row += 1
        dataLayout.addWidget(QLabel("Accelerometer"), row, col)
        dataLayout.addWidget(WarningButton(m1m3, "accelerometerWarning"), row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Gyro"), row, col)
        dataLayout.addWidget(WarningButton(m1m3, "gyroWarning"), row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("Air Supply"), row, col)
        dataLayout.addWidget(WarningButton(m1m3, "airSupplyWarning"), row, col + 1)
        row += 1
        dataLayout.addWidget(QLabel("IMS"), row, col)
        dataLayout.addWidget(
            WarningButton(m1m3, "displacementSensorWarning"), row, col + 1
        )
        row += 1
        dataLayout.addWidget(QLabel("Cell Light"), row, col)
        dataLayout.addWidget(WarningButton(m1m3, "cellLightWarning"), row, col + 1)
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
        dataLayout.addWidget(QLabel("X"), row, col + 1)
        dataLayout.addWidget(QLabel("Y"), row, col + 2)
        dataLayout.addWidget(QLabel("Z"), row, col + 3)
        dataLayout.addWidget(QLabel("<b>Outer Loop</b>"), row, col + 4)
        dataLayout.addWidget(self.broadcastCounter, row, col + 5)
        dataLayout.addWidget(self.slewFlag, row, col + 6)
        dataLayout.addWidget(self.executionTime, row, col + 7)
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

        m1m3.appliedForces.connect(self.appliedForces)
        m1m3.detailedState.connect(self.detailedState)
        m1m3.errorCode.connect(self.errorCode)
        m1m3.heartbeat.connect(self.heartbeatLabel.heartbeat)

        m1m3.accelerometerData.connect(self.accelerometerData)
        m1m3.forceActuatorData.connect(self.forceActuatorData)
        m1m3.gyroData.connect(self.gyroData)
        m1m3.hardpointActuatorData.connect(self.hardpointActuatorData)
        m1m3.imsData.connect(self.imsData)
        m1m3.inclinometerData.connect(self.inclinometerData)
        m1m3.softwareVersions.connect(self.softwareVersions)
        m1m3.forceActuatorSettings.connect(self.forceActuatorSettings)
        m1m3.outerLoopData.connect(self.outerLoopData)

        mtmount.azimuth.connect(self.azimuth)
        mtmount.elevation.connect(self.elevation)

    def _setValues(self, variables, data):
        for k, v in variables.items():
            v.setValue(getattr(data, k))

    @Slot(map)
    def appliedForces(self, data):
        self._setValues(self.faCommanded, data)

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
    def errorCode(self, data):
        self.errorCodeLabel.setText(hex(data.errorCode))

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
        self.inclinometerElevationLabel.setText(f"{data.inclinometerAngle:.3f}")

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
            self.inclinometerTMALabel.setText("<b>Inclinometer</b>")
        else:
            self.inclinometerTMALabel.setText("<b>TMA</b>")

    @Slot(map)
    def outerLoopData(self, data):
        self.broadcastCounter.setText(str(data.broadcastCounter))
        self.slewFlag.setText("True" if data.slewFlag else "False")
        self.executionTime.setText(f"{(data.executionTime * u.s.to(u.ms)):.2f}")

    @Slot(map)
    def azimuth(self, data):
        self.tmaAzimuthLabel.setText("%0.3f" % (data.actualPosition))

    @Slot(map)
    def elevation(self, data):
        self.tmaElevationLabel.setText("%0.3f" % (data.actualPosition))
