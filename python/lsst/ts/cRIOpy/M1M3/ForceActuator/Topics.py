# This file is part of the cRIO GUI.
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

import typing

from lsst.ts.cRIOpy.M1M3FATable import (
    FATABLE,
    FATABLE_INDEX,
    FATABLE_SINDEX,
    FATABLE_XINDEX,
    FATABLE_YINDEX,
    FATABLE_ZINDEX,
)
from PySide2.QtCore import Slot

from ...GUI.ActuatorsDisplay import Scales
from ...GUI.SAL.SALComm import MetaSAL
from ...GUI.SAL.TopicData import (
    EnabledDisabledField,
    TopicData,
    TopicField,
    WaitingField,
    WarningField,
)

__all__ = ["Topics"]


class BumpTestField(TopicField):
    def __init__(self, name, fieldName, valueIndex):
        super().__init__(name, fieldName, valueIndex, Scales.BUMP_TEST)


class FAIndicesData(TopicData):
    """Class for constant FA indices. Construct required fields, provides data.

    Parameters
    ----------
    name : `str`
        Topic name.
    """

    def __init__(self, name: str):
        super().__init__(
            name,
            [
                TopicField("Z Indices", "zIndices", FATABLE_ZINDEX, Scales.INTEGER),
                TopicField("Y Indices", "yIndices", FATABLE_YINDEX, Scales.INTEGER),
                TopicField("X Indices", "xIndices", FATABLE_XINDEX, Scales.INTEGER),
                TopicField(
                    "Primary Cylinder Indices",
                    "pIndices",
                    FATABLE_INDEX,
                    Scales.INTEGER,
                ),
                TopicField(
                    "Secondary Cylinder Indices",
                    "sIndices",
                    FATABLE_SINDEX,
                    Scales.INTEGER,
                ),
            ],
            None,
        )

        self.xIndices = [
            row[FATABLE_XINDEX] for row in FATABLE if row[FATABLE_XINDEX] is not None
        ]
        self.yIndices = [
            row[FATABLE_YINDEX] for row in FATABLE if row[FATABLE_YINDEX] is not None
        ]
        self.zIndices = [row[FATABLE_ZINDEX] for row in FATABLE]
        self.pIndices = [row[FATABLE_INDEX] for row in FATABLE]
        self.sIndices = [
            row[FATABLE_SINDEX] for row in FATABLE if row[FATABLE_SINDEX] is not None
        ]
        self.timestamp = None

    def getTopic(self) -> typing.Any:
        return self


class Topics:
    """
    Class constructing list of all available topics of the Force Actuators.

    Attributes
    ----------
    topics : `[TopicData]`
        Force Actuator topics. Holds topics and fields available for plotting.
    """

    def __init__(self) -> None:
        self.__lastIndex = None

        self.topics = [
            TopicData(
                "Applied Acceleration Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "appliedAccelerationForces",
                False,
            ),
            TopicData(
                "Applied Active Optic Forces",
                [TopicField("Z Forces", "zForces", FATABLE_ZINDEX)],
                "appliedActiveOpticForces",
                command="ActiveOpticForces",
            ),
            TopicData(
                "Applied Azimuth Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "appliedAzimuthForces",
                False,
            ),
            TopicData(
                "Applied Balance Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "appliedBalanceForces",
                False,
            ),
            TopicData(
                "Applied Cylinder Forces",
                [
                    TopicField(
                        "Primary Cylinder Forces",
                        "primaryCylinderForces",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Cylinder Forces",
                        "secondaryCylinderForces",
                        FATABLE_SINDEX,
                    ),
                ],
                "appliedCylinderForces",
                False,
            ),
            TopicData(
                "Applied Elevation Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "appliedElevationForces",
                False,
            ),
            TopicData(
                "Applied Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "appliedForces",
                False,
            ),
            TopicData(
                "Applied Offset Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "appliedOffsetForces",
                command="OffsetForces",
            ),
            TopicData(
                "Applied Static Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "appliedStaticForces",
            ),
            TopicData(
                "Applied Thermal Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "appliedThermalForces",
                False,
            ),
            TopicData(
                "Applied Velocity Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "appliedVelocityForces",
                False,
            ),
            TopicData(
                "Pre-clipped Acceleration Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "preclippedAccelerationForces",
            ),
            TopicData(
                "Pre-clipped Active Optic Forces",
                [TopicField("Z Forces", "zForces", FATABLE_ZINDEX)],
                "preclippedActiveOpticForces",
            ),
            TopicData(
                "Pre-clipped Azimuth Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "preclippedAzimuthForces",
            ),
            TopicData(
                "Pre-clipped Balance Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "preclippedBalanceForces",
            ),
            TopicData(
                "Pre-clipped Cylinder Forces",
                [
                    TopicField(
                        "Primary Cylinder Forces",
                        "primaryCylinderForces",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Cylinder Forces",
                        "secondaryCylinderForces",
                        FATABLE_SINDEX,
                    ),
                ],
                "preclippedCylinderForces",
            ),
            TopicData(
                "Pre-clipped Elevation Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "preclippedElevationForces",
            ),
            TopicData(
                "Pre-clipped Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "preclippedForces",
            ),
            TopicData(
                "Pre-clipped Offset Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "preclippedOffsetForces",
            ),
            TopicData(
                "Pre-clipped Static Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "preclippedStaticForces",
            ),
            TopicData(
                "Pre-clipped Thermal Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "preclippedThermalForces",
            ),
            TopicData(
                "Pre-clipped Velocity Forces",
                [
                    TopicField("Z Forces", "zForces", FATABLE_ZINDEX),
                    TopicField("Y Forces", "yForces", FATABLE_YINDEX),
                    TopicField("X Forces", "xForces", FATABLE_XINDEX),
                ],
                "preclippedVelocityForces",
            ),
            TopicData(
                "Measured forces",
                [
                    TopicField(
                        "Primary Cylinder Forces",
                        "primaryCylinderForce",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Cylinder Forces",
                        "secondaryCylinderForce",
                        FATABLE_SINDEX,
                    ),
                    TopicField(
                        "Z Forces",
                        "zForce",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Y Forces",
                        "yForce",
                        FATABLE_YINDEX,
                    ),
                    TopicField(
                        "X Forces",
                        "xForce",
                        FATABLE_XINDEX,
                    ),
                ],
                "forceActuatorData",
                False,
            ),
            TopicData(
                "FA Following Error",
                [
                    TopicField(
                        "Primary Cylinder FE",
                        "primaryCylinderFollowingError",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Cylinder FE",
                        "secondaryCylinderFollowingError",
                        FATABLE_SINDEX,
                    ),
                ],
                "forceActuatorData",
                False,
            ),
            TopicData(
                "FA Raising State",
                [
                    WaitingField(
                        "Waiting for Z FA", "waitZForceActuator", FATABLE_ZINDEX
                    ),
                    WaitingField(
                        "Waiting for Y FA", "waitYForceActuator", FATABLE_YINDEX
                    ),
                    WaitingField(
                        "Waiting for X FA", "waitXForceActuator", FATABLE_XINDEX
                    ),
                ],
                "raisingLoweringInfo",
            ),
            TopicData(
                "FA Info",
                [
                    TopicField(
                        "Actuator Type",
                        "actuatorType",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Actuator Orientation",
                        "actuatorOrientation",
                        FATABLE_ZINDEX,
                    ),
                    TopicField("Subnet", "modbusSubnet", FATABLE_ZINDEX),
                    TopicField("Address", "modbusAddress", FATABLE_ZINDEX),
                    TopicField("X Position", "xPosition", FATABLE_ZINDEX),
                    TopicField("Y Position", "yPosition", FATABLE_ZINDEX),
                    TopicField("Z Position", "zPosition", FATABLE_ZINDEX),
                    TopicField(
                        "Major Revision",
                        "majorRevision",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Minor Revision",
                        "minorRevision",
                        FATABLE_ZINDEX,
                    ),
                    TopicField("ADC Scan Rate", "adcScanRate", FATABLE_ZINDEX),
                    TopicField("Reference ID", "referenceId", FATABLE_ZINDEX),
                    TopicField(
                        "X Data Reference Id",
                        "xDataReferenceId",
                        FATABLE_XINDEX,
                    ),
                    TopicField(
                        "Y Data Reference Id",
                        "yDataReferenceId",
                        FATABLE_YINDEX,
                    ),
                    TopicField(
                        "Z Data Reference Id",
                        "zDataReferenceId",
                        FATABLE_ZINDEX,
                    ),
                    TopicField("ILC Unique Id", "ilcUniqueId", FATABLE_ZINDEX),
                    TopicField(
                        "ILC application type",
                        "ilcApplicationType",
                        FATABLE_ZINDEX,
                    ),
                    TopicField("Network Node Type", "networkNodeType", FATABLE_ZINDEX),
                    TopicField(
                        "ILC Selected Options", "ilcSelectedOptions", FATABLE_ZINDEX
                    ),
                    TopicField(
                        "Network Node Options", "networkNodeOptions", FATABLE_ZINDEX
                    ),
                    TopicField(
                        "Mezzanine Unique ID", "mezzanineUniqueId", FATABLE_ZINDEX
                    ),
                    TopicField(
                        "Mezzanine Firmware Type",
                        "mezzanineFirmwareType",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Mezzanine Major Revision",
                        "mezzanineMajorRevision",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Mezzanine Minor Revision",
                        "mezzanineMinorRevision",
                        FATABLE_ZINDEX,
                    ),
                ],
                "forceActuatorInfo",
            ),
            FAIndicesData("FA Indices"),
            TopicData(
                "FA Settings",
                [
                    EnabledDisabledField(
                        "Enabled/Disabled", "enabledActuators", FATABLE_ZINDEX
                    ),
                    TopicField(
                        "Z Applied Force Low Limit",
                        "appliedZForceLowLimit",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Z Applied Force High Limit",
                        "appliedZForceHighLimit",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Y Applied Force Low Limit",
                        "appliedYForceLowLimit",
                        FATABLE_YINDEX,
                    ),
                    TopicField(
                        "Y Applied Force High Limit",
                        "appliedYForceHighLimit",
                        FATABLE_YINDEX,
                    ),
                    TopicField(
                        "X Applied Force Low Limit",
                        "appliedXForceLowLimit",
                        FATABLE_XINDEX,
                    ),
                    TopicField(
                        "X Applied Force High Limit",
                        "appliedXForceHighLimit",
                        FATABLE_XINDEX,
                    ),
                    TopicField(
                        "Z Measured Force Low Limit",
                        "measuredZForceLowLimit",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Z Measured Force High Limit",
                        "measuredZForceHighLimit",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Y Measured Force Low Limit",
                        "measuredYForceLowLimit",
                        FATABLE_YINDEX,
                    ),
                    TopicField(
                        "Y Measured Force High Limit",
                        "measuredYForceHighLimit",
                        FATABLE_YINDEX,
                    ),
                    TopicField(
                        "X Measured Force Low Limit",
                        "measuredXForceLowLimit",
                        FATABLE_XINDEX,
                    ),
                    TopicField(
                        "X Measured Force High Limit",
                        "measuredXForceHighLimit",
                        FATABLE_XINDEX,
                    ),
                    TopicField(
                        "PC FE Warning",
                        "primaryFollowingErrorWarningThreshold",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "PC FE Counting",
                        "primaryFollowingErrorCountingFaultThreshold",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "PC FE Immediate",
                        "primaryFollowingErrorImmediateFaultThreshold",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "SC FE Warning",
                        "secondaryFollowingErrorWarningThreshold",
                        FATABLE_SINDEX,
                    ),
                    TopicField(
                        "SC FE Counting",
                        "secondaryFollowingErrorCountingFaultThreshold",
                        FATABLE_SINDEX,
                    ),
                    TopicField(
                        "SC FE Immediate",
                        "secondaryFollowingErrorImmediateFaultThreshold",
                        FATABLE_SINDEX,
                    ),
                ],
                "forceActuatorSettings",
            ),
            TopicData(
                "FA Main Calibration Info",
                [
                    TopicField(
                        "Primary Coefficient",
                        "mainPrimaryCylinderCoefficient",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Primary Offset",
                        "mainPrimaryCylinderLoadCellOffset",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Primary Sensitivity",
                        "mainPrimaryCylinderLoadCellSensitivity",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Coefficient",
                        "mainSecondaryCylinderCoefficient",
                        FATABLE_SINDEX,
                    ),
                    TopicField(
                        "Secondary Offset",
                        "mainSecondaryCylinderLoadCellOffset",
                        FATABLE_SINDEX,
                    ),
                    TopicField(
                        "Secondary Sensitivity",
                        "mainSecondaryLoadCellSensitivity",
                        FATABLE_SINDEX,
                    ),
                    TopicField(
                        "Primary Cylinder Gain",
                        "mezzaninePrimaryCylinderGain",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Cylinder Gain",
                        "mezzanineSecondaryCylinderGain",
                        FATABLE_SINDEX,
                    ),
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "FA Backup Calibration Info",
                [
                    TopicField(
                        "Primary Coefficient",
                        "backupPrimaryCylinderCoefficient",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Primary Offset",
                        "backupPrimaryCylinderLoadCellOffset",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Primary Sensitivity",
                        "backupPrimaryCylinderLoadCellSensitivity",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Coefficient",
                        "backupSecondaryCylinderCoefficient",
                        FATABLE_SINDEX,
                    ),
                    TopicField(
                        "Secondary Offset",
                        "backupSecondaryCylinderLoadCellOffset",
                        FATABLE_SINDEX,
                    ),
                    TopicField(
                        "Secondary Sensitivity",
                        "backupSecondaryLoadCellSensitivity",
                        FATABLE_SINDEX,
                    ),
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "FA State",
                [TopicField("ILC State", "ilcState", FATABLE_ZINDEX)],
                "forceActuatorState",
            ),
            TopicData(
                "FA Warning",
                [
                    WarningField("Major Fault", "majorFault", FATABLE_ZINDEX),
                    WarningField("Minor Fault", "minorFault", FATABLE_ZINDEX),
                    WarningField(
                        "Fault Override",
                        "faultOverride",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Main Calibration Error",
                        "mainCalibrationError",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Backup Calibration Error",
                        "backupCalibrationError",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Mezzanine Error",
                        "mezzanineError",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Mezzanine Bootloader Active",
                        "mezzanineBootloaderActive",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Unique Id CRC Error",
                        "uniqueIdCRCError",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Application Type Mismatch",
                        "applicationTypeMismatch",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Application Missing",
                        "applicationMissing",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "OneWire Mismatch",
                        "oneWireMissing",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "OneWire1 Mismatch",
                        "oneWire1Mismatch",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "OnewWire2 Mismatch",
                        "oneWire2Mismatch",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Watchdog Reset",
                        "watchdogReset",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Brownout",
                        "brownOut",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Event Trap Reset",
                        "eventTrapReset",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "SSR Power Fault",
                        "ssrPowerFault",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "AUX Power Fault",
                        "auxPowerFault",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Mezzanine Power Fault",
                        "mezzaninePowerFault",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Mezzanine Current Ampl Fault",
                        "mezzanineCurrentAmp1Fault",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Mezzanine Current Amp2 Fault",
                        "mezzanineCurrentAmp2Fault",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Mezzanine Unique ID CRC Error",
                        "mezzanineUniqueIdCRCError",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Mezzanine Main Calibration Error",
                        "mezzanineMainCalibrationError",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Mezzanine Backup Calibration Error",
                        "mezzanineBackupCalibrationError",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Mezzanine Event Trap Reset",
                        "mezzanineEventTrapReset",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Mezzanine Application Missing",
                        "mezzanineApplicationMissing",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Mezzanine Application CRC Mismatch",
                        "mezzanineApplicationCRCMismatch",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "ILC Fault",
                        "ilcFault",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Broadcast Counter Warning",
                        "broadcastCounterWarning",
                        FATABLE_ZINDEX,
                    ),
                ],
                "forceActuatorWarning",
            ),
            TopicData(
                "FA Force Warning",
                [
                    WarningField(
                        "Z Measured Force Warning",
                        "measuredZForceWarning",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Y Measured Force Warning",
                        "measuredYForceWarning",
                        FATABLE_YINDEX,
                    ),
                    WarningField(
                        "X Measured Force Warning",
                        "measuredXForceWarning",
                        FATABLE_XINDEX,
                    ),
                    WarningField(
                        "Primary Axis FE Warning",
                        "primaryAxisFollowingErrorWarning",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Secondary Axis FE Warning",
                        "secondaryAxisFollowingErrorWarning",
                        FATABLE_SINDEX,
                    ),
                    WarningField(
                        "Primary Axis FE Counting Fault",
                        "primaryAxisFollowingErrorCountingFault",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Secondary Axis FE Counting Fault",
                        "secondaryAxisFollowingErrorCountingFault",
                        FATABLE_SINDEX,
                    ),
                    WarningField(
                        "Primary Axis FE Immediate Fault",
                        "primaryAxisFollowingErrorImmediateFault",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Secondary Axis FE Immediate Fault",
                        "secondaryAxisFollowingErrorImmediateFault",
                        FATABLE_SINDEX,
                    ),
                ],
                "forceActuatorForceWarning",
            ),
            TopicData(
                "FA FE Counters",
                [
                    TopicField(
                        "Primary axis FE warning counter",
                        "primaryAxisFollowingErrorWarningCounter",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary axis FE warning counter",
                        "secondaryAxisFollowingErrorWarningCounter",
                        FATABLE_SINDEX,
                    ),
                    TopicField(
                        "Primary axis FE counting counter",
                        "primaryAxisFollowingErrorCountingCounter",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary axis FE counting counter",
                        "secondaryAxisFollowingErrorCountingCounter",
                        FATABLE_SINDEX,
                    ),
                ],
                "forceActuatorFollowingErrorCounter",
            ),
            TopicData(
                "FA Setpoint Warning",
                [
                    WarningField(
                        "Safety limit",
                        "safetyLimitWarning",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Near neighbor",
                        "nearNeighborWarning",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Far neighbor",
                        "farNeighborWarning",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Elevation force",
                        "elevationForceWarning",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Azimuth force",
                        "azimuthForceWarning",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Thermal force",
                        "thermalForceWarning",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Balance force",
                        "balanceForceWarning",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Acceleration force",
                        "accelerationForceWarning",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Active optic",
                        "activeOpticForceWarning",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Static force",
                        "staticForceWarning",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Offset force",
                        "offsetForceWarning",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Velocity force",
                        "velocityForceWarning",
                        FATABLE_ZINDEX,
                    ),
                    WarningField(
                        "Force setpoint",
                        "forceWarning",
                        FATABLE_ZINDEX,
                    ),
                ],
                "forceSetpointWarning",
            ),
            TopicData(
                "FA Bump Test",
                [
                    BumpTestField("Primary Test", "primaryTest", FATABLE_ZINDEX),
                    BumpTestField(
                        "Secondary Test",
                        "secondaryTest",
                        FATABLE_SINDEX,
                    ),
                    TopicField(
                        "Primary Timestamps",
                        "primaryTestTimestamps",
                        FATABLE_ZINDEX,
                    ),
                    TopicField(
                        "Secondary Timestamps",
                        "secondaryTestTimestamps",
                        FATABLE_SINDEX,
                    ),
                ],
                "forceActuatorBumpTestStatus",
            ),
            TopicData(
                "FA enabled",
                [
                    EnabledDisabledField(
                        "Enabled FAs",
                        "forceActuatorEnabled",
                        FATABLE_ZINDEX,
                    ),
                ],
                "enabledForceActuators",
            ),
        ]

    def changeTopic(self, index: int, slot: Slot, comm: MetaSAL) -> None:
        """Called when new topic is selected.

        Parameters
        ----------
        index: `int`
            New field index.
        slot: `Slot`
            Slot for data reception.
        comm: `MetaSAL`
            MetaSAL with data.
        """
        # disconnect/connect only for real M1M3 topics -  if topic is None,
        # don't connect/disconnect
        if self.__lastIndex is not None:
            topic = self.topics[self.__lastIndex].topic
            if topic is not None:
                getattr(comm, topic).disconnect(slot)

        self.__lastIndex = index
        if index is None:
            return

        topic = self.topics[index].topic
        if topic is not None:
            getattr(comm, topic).connect(slot)
