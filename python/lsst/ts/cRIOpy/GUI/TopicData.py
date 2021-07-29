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


class TopicField:
    def __init__(self, name, value, index):
        self.name = name
        self.value = value
        self.index = index


class Topics:
    """
    Class constructing list of all available topics.
    """

    def __init__(self):
        self.lastIndex = None

        self.topics = [
            TopicData(
                "Applied Aberration Forces",
                [TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX)],
                "appliedAberrationForces",
            ),
            TopicData(
                "Applied Acceleration Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "appliedAccelerationForces",
            ),
            TopicData(
                "Applied Active Optic Forces",
                [TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX)],
                "appliedActiveOpticForces",
            ),
            TopicData(
                "Applied Azimuth Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "appliedAzimuthForces",
            ),
            TopicData(
                "Applied Balance Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "appliedBalanceForces",
            ),
            TopicData(
                "Applied Cylinder Forces",
                [
                    TopicField(
                        "Primary Cylinder Forces",
                        lambda x: x.primaryCylinderForces,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Cylinder Forces",
                        lambda x: x.secondaryCylinderForces,
                        lambda: FATABLE_SINDEX,
                    ),
                ],
                "appliedCylinderForces",
            ),
            TopicData(
                "Applied Elevation Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "appliedElevationForces",
            ),
            TopicData(
                "Applied Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "appliedForces",
            ),
            TopicData(
                "Applied Offset Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "appliedOffsetForces",
            ),
            TopicData(
                "Applied Static Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "appliedStaticForces",
            ),
            TopicData(
                "Applied Thermal Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "appliedThermalForces",
            ),
            TopicData(
                "Applied Velocity Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "appliedVelocityForces",
            ),
            TopicData(
                "Pre-clipped Aberration Forces",
                [TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX)],
                "preclippedAberrationForces",
            ),
            TopicData(
                "Pre-clipped Acceleration Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "preclippedAccelerationForces",
            ),
            TopicData(
                "Pre-clipped Active Optic Forces",
                [TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX)],
                "preclippedActiveOpticForces",
            ),
            TopicData(
                "Pre-clipped Azimuth Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "preclippedAzimuthForces",
            ),
            TopicData(
                "Pre-clipped Balance Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "preclippedBalanceForces",
            ),
            TopicData(
                "Pre-clipped Cylinder Forces",
                [
                    TopicField(
                        "Primary Cylinder Forces",
                        lambda x: x.primaryCylinderForces,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Cylinder Forces",
                        lambda x: x.secondaryCylinderForces,
                        lambda: FATABLE_SINDEX,
                    ),
                ],
                "preclippedCylinderForces",
            ),
            TopicData(
                "Pre-clipped Elevation Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "preclippedElevationForces",
            ),
            TopicData(
                "Pre-clipped Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "preclippedForces",
            ),
            TopicData(
                "Pre-clipped Offset Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "preclippedOffsetForces",
            ),
            TopicData(
                "Pre-clipped Static Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "preclippedStaticForces",
            ),
            TopicData(
                "Pre-clipped Thermal Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "preclippedThermalForces",
            ),
            TopicData(
                "Pre-clipped Velocity Forces",
                [
                    TopicField("Z Forces", lambda x: x.zForces, lambda: FATABLE_ZINDEX),
                    TopicField("Y Forces", lambda x: x.yForces, lambda: FATABLE_YINDEX),
                    TopicField("X Forces", lambda x: x.xForces, lambda: FATABLE_XINDEX),
                ],
                "preclippedVelocityForces",
            ),
            TopicData(
                "Measured forces",
                [
                    TopicField(
                        "Primary Cylinder Forces",
                        lambda x: x.primaryCylinderForce,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Cylinder Forces",
                        lambda x: x.secondaryCylinderForce,
                        lambda: FATABLE_SINDEX,
                    ),
                    TopicField(
                        "Z Forces",
                        lambda x: x.zForce,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Y Forces",
                        lambda x: x.yForce,
                        lambda: FATABLE_YINDEX,
                    ),
                    TopicField(
                        "X Forces",
                        lambda x: x.xForce,
                        lambda: FATABLE_XINDEX,
                    ),
                ],
                "forceActuatorData",
                False,
            ),
            TopicData(
                "Force Actuator ILC Info",
                [
                    TopicField(
                        "Subnet", lambda x: x.modbusSubnet, lambda: FATABLE_ZINDEX
                    ),
                    TopicField(
                        "Address", lambda x: x.modbusAddress, lambda: FATABLE_ZINDEX
                    ),
                    TopicField(
                        "Major Revision",
                        lambda x: x.majorRevision,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Minor Revision",
                        lambda x: x.minorRevision,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "ADC Scan Rate", lambda x: x.adcScanRate, lambda: FATABLE_ZINDEX
                    ),
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "Force Actuator Id Info",
                [
                    TopicField(
                        "X Data Reference Id",
                        lambda x: x.xDataReferenceId,
                        lambda: FATABLE_XINDEX,
                    ),
                    TopicField(
                        "Y Data Reference Id",
                        lambda x: x.yDataReferenceId,
                        lambda: FATABLE_YINDEX,
                    ),
                    TopicField(
                        "Z Data Reference Id",
                        lambda x: x.zDataReferenceId,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "S Data Reference Id",
                        lambda x: x.sDataReferenceId,
                        lambda: FATABLE_SINDEX,
                    ),
                    TopicField(
                        "ILC Unique Id", lambda x: x.ilcUniqueId, lambda: FATABLE_ZINDEX
                    ),
                    TopicField(
                        "Mezzanine Unique Id",
                        lambda x: x.xDataReferenceId,
                        lambda: FATABLE_ZINDEX,
                    ),
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "Force Actuator Main Calibration Info",
                [
                    TopicField(
                        "Primary Coefficient",
                        lambda x: x.mainPrimaryCylinderCoefficient,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Primary Offset",
                        lambda x: x.mainPrimaryCylinderLoadCellOffset,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Primary Sensitivity",
                        lambda x: x.mainPrimaryCylinderLoadCellSensitivity,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Coefficient",
                        lambda x: x.mainSecondaryCylinderCoefficient,
                        lambda: FATABLE_SINDEX,
                    ),
                    TopicField(
                        "Secondary Offset",
                        lambda x: x.mainSecondaryCylinderLoadCellOffset,
                        lambda: FATABLE_SINDEX,
                    ),
                    TopicField(
                        "Secondary Sensitivity",
                        lambda x: x.mainSecondaryLoadCellSensitivity,
                        lambda: FATABLE_SINDEX,
                    ),
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "Force Actuator Backup Calibration Info",
                [
                    TopicField(
                        "Primary Coefficient",
                        lambda x: x.backupPrimaryCylinderCoefficient,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Primary Offset",
                        lambda x: x.backupPrimaryCylinderLoadCellOffset,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Primary Sensitivity",
                        lambda x: x.backupPrimaryCylinderLoadCellSensitivity,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Coefficient",
                        lambda x: x.backupSecondaryCylinderCoefficient,
                        lambda: FATABLE_SINDEX,
                    ),
                    TopicField(
                        "Secondary Offset",
                        lambda x: x.backupSecondaryCylinderLoadCellOffset,
                        lambda: FATABLE_SINDEX,
                    ),
                    TopicField(
                        "Secondary Sensitivity",
                        lambda x: x.backupSecondaryLoadCellSensitivity,
                        lambda: FATABLE_SINDEX,
                    ),
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "Force Actuator Mezzanine Calibration Info",
                [
                    TopicField(
                        "Primary Cylinder Gain",
                        lambda x: x.mezzaninePrimaryCylinderGain,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Cylinder Gain",
                        lambda x: x.mezzanineSecondaryCylinderGain,
                        lambda: FATABLE_SINDEX,
                    ),
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "Force Actuator Position Info",
                [
                    TopicField(
                        "Actuator Type",
                        lambda x: x.actuatorType,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Actuator Orientation",
                        lambda x: x.actuatorOrientation,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "X Position", lambda x: x.xPosition, lambda: FATABLE_ZINDEX
                    ),
                    TopicField(
                        "Y Position", lambda x: x.yPosition, lambda: FATABLE_ZINDEX
                    ),
                    TopicField(
                        "Z Position", lambda x: x.zPosition, lambda: FATABLE_ZINDEX
                    ),
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "Force Actuator State",
                [TopicField("ILC State", lambda x: x.ilcState, lambda: FATABLE_ZINDEX)],
                "forceActuatorState",
            ),
            TopicData(
                "Force Actuator Warning",
                [
                    TopicField(
                        "Major Fault", lambda x: x.majorFault, lambda: FATABLE_ZINDEX
                    ),
                    TopicField(
                        "Minor Fault", lambda x: x.minorFault, lambda: FATABLE_ZINDEX
                    ),
                    TopicField(
                        "Fault Override",
                        lambda x: x.faultOverride,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Main Calibration Error",
                        lambda x: x.mainCalibrationError,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Backup Calibration Error",
                        lambda x: x.backupCalibrationError,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Mezzanine Error",
                        lambda x: x.mezzanineError,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Mezzanine Bootloader Active",
                        lambda x: x.mezzanineBootloaderActive,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Unique Id CRC Error",
                        lambda x: x.uniqueIdCRCError,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Application Type Mismatch",
                        lambda x: x.applicationTypeMismatch,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Application Missing",
                        lambda x: x.applicationMissing,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "OneWire Mismatch",
                        lambda x: x.oneWireMissing,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "OneWire1 Mismatch",
                        lambda x: x.oneWire1Mismatch,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "OnewWire2 Mismatch",
                        lambda x: x.oneWire2Mismatch,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Watchdog Reset",
                        lambda x: x.watchdogReset,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Brownout",
                        lambda x: x.brownOut,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Event Trap Reset",
                        lambda x: x.eventTrapReset,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "SSR Power Fault",
                        lambda x: x.ssrPowerFault,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "AUX Power Fault",
                        lambda x: x.auxPowerFault,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Mezzanine Power Fault",
                        lambda x: x.mezzaninePowerFault,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Mezzanine Current Ampl Fault",
                        lambda x: x.mezzanineCurrentAmp1Fault,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Mezzanine Current Amp2 Fault",
                        lambda x: x.mezzanineCurrentAmp2Fault,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Mezzanine Unique ID CRC Error",
                        lambda x: x.mezzanineUniqueIdCRCError,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Mezzanine Main Calibration Error",
                        lambda x: x.mezzanineMainCalibrationError,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Mezzanine Backup Calibration Error",
                        lambda x: x.mezzanineBackupCalibrationError,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Mezzanine Event Trap Reset",
                        lambda x: x.mezzanineEventTrapReset,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Mezzanine Application Missing",
                        lambda x: x.mezzanineApplicationMissing,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Mezzanine Application CRC Mismatch",
                        lambda x: x.mezzanineApplicationCRCMismatch,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "ILC Fault",
                        lambda x: x.ilcFault,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Broadcast Counter Warning",
                        lambda x: x.broadcastCounterWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                ],
                "forceActuatorWarning",
            ),
            TopicData(
                "Force Actuator Force Warning",
                [
                    TopicField(
                        "Primary Axis Measured Force Warning",
                        lambda x: x.primaryAxisMeasuredForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Axis Measured Force Warning",
                        lambda x: x.secondaryAxisMeasuredForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Primary Axis Following Error Warning",
                        lambda x: x.primaryAxisFollowingErrorWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Axis Following Error Warning",
                        lambda x: x.secondaryAxisFollowingErrorWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                ],
                "forceActuatorForceWarning",
            ),
            TopicData(
                "FA Setpoint Warning",
                [
                    TopicField(
                        "Safety limit",
                        lambda x: x.safetyLimitWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Near neighbor",
                        lambda x: x.nearNeighborWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Far neighbor",
                        lambda x: x.farNeighborWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Elevation force",
                        lambda x: x.elevationForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Azimuth force",
                        lambda x: x.azimuthForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Thermal force",
                        lambda x: x.thermalForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Balance force",
                        lambda x: x.balanceForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Acceleration force",
                        lambda x: x.accelerationForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Active optic",
                        lambda x: x.activeOpticForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Static force",
                        lambda x: x.staticForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Aberration force",
                        lambda x: x.aberrationForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Offset force",
                        lambda x: x.offsetForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Velocity force",
                        lambda x: x.velocityForceWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Force setpoint",
                        lambda x: x.forceWarning,
                        lambda: FATABLE_ZINDEX,
                    ),
                ],
                "forceSetpointWarning",
            ),
            TopicData(
                "FA Bump Test",
                [
                    TopicField(
                        "Primary Test", lambda x: x.primaryTest, lambda: FATABLE_ZINDEX
                    ),
                    TopicField(
                        "Secondary Test",
                        lambda x: x.secondaryTest,
                        lambda: FATABLE_SINDEX,
                    ),
                    TopicField(
                        "Primary Timestamps",
                        lambda x: x.primaryTestTimestamps,
                        lambda: FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Timestamps",
                        lambda x: x.secondaryTestTimestamps,
                        lambda: FATABLE_SINDEX,
                    ),
                ],
                "forceActuatorBumpTestStatus",
            ),
            TopicData(
                "FA enabled",
                [
                    TopicField(
                        "Enabled FAs",
                        lambda x: x.forceActuatorEnabled,
                        lambda: FATABLE_ZINDEX,
                    ),
                ],
                "enabledForceActuators",
            ),
        ]

    def changeTopic(self, index, slot, comm):
        if self.lastIndex is not None:
            getattr(comm, self.topics[self.lastIndex].topic).disconnect(slot)

        self.lastIndex = index
        if index is None:
            return

        getattr(comm, self.topics[index].topic).connect(slot)
