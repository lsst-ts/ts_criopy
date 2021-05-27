from lsst.ts.cRIOpy.M1M3FATable import (
    FATABLE_XINDEX,
    FATABLE_YINDEX,
    FATABLE_ZINDEX,
    FATABLE_SINDEX,
)

__all__ = ["Topics", "TopicData"]


class TopicData:
    def __init__(self, name, fields, topic, isEvent=True):
        self.name = name
        self.fields = fields
        self.selectedField = 0
        self.topic = topic
        self.isEvent = isEvent

    def getTopic(self):
        if self.isEvent:
            return "evt_" + self.topic
        return "tel_" + self.topic


class Topics:
    """
    Class constructing list of all available topics.
    """

    def __init__(self):
        self.lastIndex = None

        self.topics = [
            TopicData(
                "Applied Aberration Forces",
                [["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX]],
                "appliedAberrationForces",
            ),
            TopicData(
                "Applied Acceleration Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "appliedAccelerationForces",
            ),
            TopicData(
                "Applied Active Optic Forces",
                [["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX]],
                "appliedActiveOpticForces",
            ),
            TopicData(
                "Applied Azimuth Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "appliedAzimuthForces",
            ),
            TopicData(
                "Applied Balance Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "appliedBalanceForces",
            ),
            TopicData(
                "Applied Cylinder Forces",
                [
                    [
                        "Primary Cylinder Forces",
                        lambda x: x.primaryCylinderForces,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Secondary Cylinder Forces",
                        lambda x: x.secondaryCylinderForces,
                        lambda: FATABLE_SINDEX,
                    ],
                ],
                "appliedCylinderForces",
            ),
            TopicData(
                "Applied Elevation Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "appliedElevationForces",
            ),
            TopicData(
                "Applied Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "appliedForces",
            ),
            TopicData(
                "Applied Offset Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "appliedOffsetForces",
            ),
            TopicData(
                "Applied Static Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "appliedStaticForces",
            ),
            TopicData(
                "Applied Thermal Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "appliedThermalForces",
            ),
            TopicData(
                "Applied Velocity Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "appliedVelocityForces",
            ),
            TopicData(
                "Pre-clipped Aberration Forces",
                [["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX]],
                "preclippedAberrationForces",
            ),
            TopicData(
                "Pre-clipped Acceleration Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "preclippedAccelerationForces",
            ),
            TopicData(
                "Pre-clipped Active Optic Forces",
                [["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX]],
                "preclippedActiveOpticForces",
            ),
            TopicData(
                "Pre-clipped Azimuth Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "preclippedAzimuthForces",
            ),
            TopicData(
                "Pre-clipped Balance Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "preclippedBalanceForces",
            ),
            TopicData(
                "Pre-clipped Cylinder Forces",
                [
                    [
                        "Primary Cylinder Forces",
                        lambda x: x.primaryCylinderForces,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Secondary Cylinder Forces",
                        lambda x: x.secondaryCylinderForces,
                        lambda: FATABLE_SINDEX,
                    ],
                ],
                "preclippedCylinderForces",
            ),
            TopicData(
                "Pre-clipped Elevation Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "preclippedElevationForces",
            ),
            TopicData(
                "Pre-clipped Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "preclippedForces",
            ),
            TopicData(
                "Pre-clipped Offset Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "preclippedOffsetForces",
            ),
            TopicData(
                "Pre-clipped Static Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "preclippedStaticForces",
            ),
            TopicData(
                "Pre-clipped Thermal Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "preclippedThermalForces",
            ),
            TopicData(
                "Pre-clipped Velocity Forces",
                [
                    ["Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX],
                    ["Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX],
                    ["X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX],
                ],
                "preclippedVelocityForces",
            ),
            TopicData(
                "Measured forces",
                [
                    [
                        "Primary Cylinder Forces",
                        lambda x: x.primaryCylinderForce,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Secondary Cylinder Forces",
                        lambda x: x.secondaryCylinderForce,
                        lambda: FATABLE_SINDEX,
                    ],
                    [
                        "Z Forces",
                        lambda x: x.zForce,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Y Forces",
                        lambda x: x.yForce,
                        lambda: FATABLE_YINDEX,
                    ],
                    [
                        "X Forces",
                        lambda x: x.xForce,
                        lambda: FATABLE_XINDEX,
                    ],
                ],
                "forceActuatorData",
                False,
            ),
            TopicData(
                "Force Actuator ILC Info",
                [
                    ["Subnet", lambda x: x.modbusSubnet, lambda: FATABLE_ZINDEX],
                    ["Address", lambda x: x.modbusAddress, lambda: FATABLE_ZINDEX],
                    ["Major Revision", lambda x: x.majorRevision],
                    ["Minor Revision", lambda x: x.minorRevision],
                    ["ADC Scan Rate", lambda x: x.adcScanRate, lambda: FATABLE_ZINDEX],
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "Force Actuator Id Info",
                [
                    [
                        "X Data Reference Id",
                        lambda x: x.xDataReferenceId,
                        lambda: FATABLE_XINDEX,
                    ],
                    [
                        "Y Data Reference Id",
                        lambda x: x.yDataReferenceId,
                        lambda: FATABLE_YINDEX,
                    ],
                    [
                        "Z Data Reference Id",
                        lambda x: x.zDataReferenceId,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "S Data Reference Id",
                        lambda x: x.sDataReferenceId,
                        lambda: FATABLE_SINDEX,
                    ],
                    ["ILC Unique Id", lambda x: x.ilcUniqueId, lambda: FATABLE_ZINDEX],
                    [
                        "Mezzanine Unique Id",
                        lambda x: x.xDataReferenceId,
                        lambda: FATABLE_ZINDEX,
                    ],
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "Force Actuator Main Calibration Info",
                [
                    [
                        "Primary Coefficient",
                        lambda x: x.mainPrimaryCylinderCoefficient,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Primary Offset",
                        lambda x: x.mainPrimaryCylinderLoadCellOffset,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Primary Sensitivity",
                        lambda x: x.mainPrimaryCylinderLoadCellSensitivity,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Secondary Coefficient",
                        lambda x: x.mainSecondaryCylinderCoefficient,
                        lambda: FATABLE_SINDEX,
                    ],
                    [
                        "Secondary Offset",
                        lambda x: x.mainSecondaryCylinderLoadCellOffset,
                        lambda: FATABLE_SINDEX,
                    ],
                    [
                        "Secondary Sensitivity",
                        lambda x: x.mainSecondaryLoadCellSensitivity,
                        lambda: FATABLE_SINDEX,
                    ],
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "Force Actuator Backup Calibration Info",
                [
                    [
                        "Primary Coefficient",
                        lambda x: x.backupPrimaryCylinderCoefficient,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Primary Offset",
                        lambda x: x.backupPrimaryCylinderLoadCellOffset,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Primary Sensitivity",
                        lambda x: x.backupPrimaryCylinderLoadCellSensitivity,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Secondary Coefficient",
                        lambda x: x.backupSecondaryCylinderCoefficient,
                        lambda: FATABLE_SINDEX,
                    ],
                    [
                        "Secondary Offset",
                        lambda x: x.backupSecondaryCylinderLoadCellOffset,
                        lambda: FATABLE_SINDEX,
                    ],
                    [
                        "Secondary Sensitivity",
                        lambda x: x.backupSecondaryLoadCellSensitivity,
                        lambda: FATABLE_SINDEX,
                    ],
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "Force Actuator Mezzanine Calibration Info",
                [
                    [
                        "Primary Cylinder Gain",
                        lambda x: x.mezzaninePrimaryCylinderGain,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Secondary Cylinder Gain",
                        lambda x: x.mezzanineSecondaryCylinderGain,
                        lambda: FATABLE_SINDEX,
                    ],
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "Force Actuator Position Info",
                [
                    ["Actuator Type", lambda x: x.actuatorType, lambda: FATABLE_ZINDEX],
                    [
                        "Actuator Orientation",
                        lambda x: x.actuatorOrientation,
                        lambda: FATABLE_ZINDEX,
                    ],
                    ["X Position", lambda x: x.xPosition, lambda: FATABLE_ZINDEX],
                    ["Y Position", lambda x: x.yPosition, lambda: FATABLE_ZINDEX],
                    ["Z Position", lambda x: x.zPosition, lambda: FATABLE_ZINDEX],
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "Force Actuator State",
                [["ILC State", lambda x: x.ilcState, lambda: FATABLE_ZINDEX]],
                "forceActuatorState",
            ),
            TopicData(
                "Force Actuator Warning",
                [
                    ["Major Fault", lambda x: x.majorFault, lambda: FATABLE_ZINDEX],
                    ["Minor Fault", lambda x: x.minorFault, lambda: FATABLE_ZINDEX],
                    [
                        "Fault Override",
                        lambda x: x.faultOverride,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Main Calibration Error",
                        lambda x: x.mainCalibrationError,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Backup Calibration Error",
                        lambda x: x.backupCalibrationError,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Mezzanine Error",
                        lambda x: x.mezzanineError,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Mezzanine Bootloader Active",
                        lambda x: x.mezzanineBootloaderActive,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Unique Id CRC Error",
                        lambda x: x.uniqueIdCRCError,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Application Type Mismatch",
                        lambda x: x.applicationTypeMismatch,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Application Missing",
                        lambda x: x.applicationMissing,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "OneWire Mismatch",
                        lambda x: x.oneWireMissing,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "OneWire1 Mismatch",
                        lambda x: x.oneWire1Mismatch,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "OnewWire2 Mismatch",
                        lambda x: x.oneWire2Mismatch,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Watchdog Reset",
                        lambda x: x.watchdogReset,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Brownout",
                        lambda x: x.brownOut,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Event Trap Reset",
                        lambda x: x.eventTrapReset,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "SSR Power Fault",
                        lambda x: x.ssrPowerFault,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "AUX Power Fault",
                        lambda x: x.auxPowerFault,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Mezzanine Power Fault",
                        lambda x: x.mezzaninePowerFault,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Mezzanine Current Ampl Fault",
                        lambda x: x.mezzanineCurrentAmp1Fault,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Mezzanine Current Amp2 Fault",
                        lambda x: x.mezzanineCurrentAmp2Fault,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Mezzanine Unique ID CRC Error",
                        lambda x: x.mezzanineUniqueIdCRCError,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Mezzanine Main Calibration Error",
                        lambda x: x.mezzanineMainCalibrationError,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Mezzanine Backup Calibration Error",
                        lambda x: x.mezzanineBackupCalibrationError,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Mezzanine Event Trap Reset",
                        lambda x: x.mezzanineEventTrapReset,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Mezzanine Application Missing",
                        lambda x: x.mezzanineApplicationMissing,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Mezzanine Application CRC Mismatch",
                        lambda x: x.mezzanineApplicationCRCMismatch,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "ILC Fault",
                        lambda x: x.ilcFault,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Broadcast Counter Warning",
                        lambda x: x.broadcastCounterWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                ],
                "forceActuatorWarning",
            ),
            TopicData(
                "Force Actuator Force Warning",
                [
                    [
                        "Primary Axis Measured Force Warning",
                        lambda x: x.primaryAxisMeasuredForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Secondary Axis Measured Force Warning",
                        lambda x: x.secondaryAxisMeasuredForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Primary Axis Following Error Warning",
                        lambda x: x.primaryAxisFollowingErrorWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Secondary Axis Following Error Warning",
                        lambda x: x.secondaryAxisFollowingErrorWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                ],
                "forceActuatorForceWarning",
            ),
            TopicData(
                "FA Setpoint Warning",
                [
                    [
                        "Safety limit",
                        lambda x: x.safetyLimitWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Near neighbor",
                        lambda x: x.nearNeighborWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Far neighbor",
                        lambda x: x.farNeighborWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Elevation force",
                        lambda x: x.elevationForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Azimuth force",
                        lambda x: x.azimuthForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Thermal force",
                        lambda x: x.thermalForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Balance force",
                        lambda x: x.balanceForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Acceleration force",
                        lambda x: x.accelerationForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Active optic",
                        lambda x: x.activeOpticForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Static force",
                        lambda x: x.staticForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Aberration force",
                        lambda x: x.aberrationForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Offset force",
                        lambda x: x.offsetForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Velocity force",
                        lambda x: x.velocityForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Force setpoint",
                        lambda x: x.forceWarning,
                        lambda: FATABLE_ZINDEX,
                    ],
                ],
                "forceSetpointWarning",
            ),
            TopicData(
                "FA Bump Test",
                [
                    ["Primary Test", lambda x: x.primaryTest, lambda: FATABLE_ZINDEX],
                    [
                        "Secondary Test",
                        lambda x: x.secondaryTest,
                        lambda: FATABLE_SINDEX,
                    ],
                    [
                        "Primary Timestamps",
                        lambda x: x.primaryTestTimestamps,
                        lambda: FATABLE_ZINDEX,
                    ],
                    [
                        "Secondary Timestamps",
                        lambda x: x.secondaryTestTimestamps,
                        lambda: FATABLE_SINDEX,
                    ],
                ],
                "forceActuatorBumpTestStatus",
            ),
        ]

    def changeTopic(self, index, slot, comm):
        if self.lastIndex is not None:
            getattr(comm, self.topics[self.lastIndex].topic).disconnect(slot)

        self.lastIndex = index
        if index is None:
            return

        getattr(comm, self.topics[index].topic).connect(slot)
