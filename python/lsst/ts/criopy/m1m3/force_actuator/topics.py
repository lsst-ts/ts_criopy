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

import numpy as np
from lsst.ts.m1m3.utils import ForceCalculator
from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.tables.m1m3 import FAIndex, FATable

from ...gui.actuatorsdisplay import Scales
from ...gui.sal import (
    EnabledDisabledField,
    TopicCollection,
    TopicData,
    TopicField,
    WaitingField,
    WarningField,
)

__all__ = ["Topics"]


class BumpTestField(TopicField):
    """Class displaying bump test status."""

    def __init__(self, name: str, fieldName: str, valueIndex: int):
        super().__init__(name, fieldName, valueIndex, Scales.BUMP_TEST)


class NearNeighborsDifferencesField(TopicField):
    """Class providing calculated near neighbors factors."""

    def __init__(self, name: str):
        super().__init__(name, None, FAIndex.Z)

    def get_value(self, data: BaseMsgType) -> typing.Any:
        near_diff = ForceCalculator.SALAppliedForces(data)
        near_diff.calculate_near_neighbors_forces()
        return np.array(near_diff.zForces) - np.array(near_diff.near_neighbors_forces)


class FarNeighborsFactorsField(TopicField):
    """Class providing calculated far neighbors factors."""

    def __init__(self, name: str):
        super().__init__(name, None, FAIndex.Z)

    def get_value(self, data: BaseMsgType) -> typing.Any:
        fn_factors = ForceCalculator.SALAppliedForces(data)
        fn_factors.calculate_far_neighbors_magnitudes()
        return (
            np.array(fn_factors.far_neighbors_magnitudes)
            - fn_factors.global_average_force
        ) / fn_factors.global_average_force


class XFEForces(TopicField):
    """Provides calculated X forces. Usefull for fields where only primary and
    secondary cylinder forces are provided."""

    def __init__(self, name: str):
        super().__init__(name, None, FAIndex.X)

    def get_value(self, data: BaseMsgType) -> typing.Any:
        forces = ForceCalculator.CylinderForces(
            data.primaryCylinderFollowingError, data.secondaryCylinderFollowingError
        )
        return forces.xForces


class YFEForces(TopicField):
    """Provides calculated Y forces. Usefull for fields where only primary and
    secondary cylinder forces are provided."""

    def __init__(self, name: str):
        super().__init__(name, None, FAIndex.Y)

    def get_value(self, data: BaseMsgType) -> typing.Any:
        forces = ForceCalculator.CylinderForces(
            data.primaryCylinderFollowingError, data.secondaryCylinderFollowingError
        )
        return forces.yForces


class ZFEForces(TopicField):
    """Provides calculated Z forces. Usefull for fields where only primary and
    secondary cylinder forces are provided."""

    def __init__(self, name: str):
        super().__init__(name, None, FAIndex.Z)

    def get_value(self, data: BaseMsgType) -> typing.Any:
        forces = ForceCalculator.CylinderForces(
            data.primaryCylinderFollowingError, data.secondaryCylinderFollowingError
        )
        return forces.zForces


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
                TopicField("Z Indices", "zIndices", FAIndex.Z, Scales.INTEGER),
                TopicField("Y Indices", "yIndices", FAIndex.Y, Scales.INTEGER),
                TopicField("X Indices", "xIndices", FAIndex.X, Scales.INTEGER),
                TopicField(
                    "Primary Cylinder Indices",
                    "pIndices",
                    FAIndex.PRIMARY,
                    Scales.INTEGER,
                ),
                TopicField(
                    "Secondary Cylinder Indices",
                    "sIndices",
                    FAIndex.SECONDARY,
                    Scales.INTEGER,
                ),
            ],
            None,
        )

        self.xIndices = [row.x_index for row in FATable if row.x_index is not None]
        self.yIndices = [row.y_index for row in FATable if row.y_index is not None]
        self.zIndices = [row.z_index for row in FATable]
        self.pIndices = [row.index for row in FATable]
        self.sIndices = [row.s_index for row in FATable if row.s_index is not None]
        self.timestamp = None

    def getTopic(self) -> typing.Any:
        return self


class Topics(TopicCollection):
    """
    Class constructing list of all available topics of the Force Actuators.
    """

    def __init__(self) -> None:
        super().__init__(
            TopicData(
                "Applied Acceleration Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "appliedAccelerationForces",
                False,
            ),
            TopicData(
                "Applied Active Optic Forces",
                [TopicField("Z Forces", "zForces", FAIndex.Z)],
                "appliedActiveOpticForces",
                command="ActiveOpticForces",
            ),
            TopicData(
                "Applied Azimuth Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "appliedAzimuthForces",
                False,
            ),
            TopicData(
                "Applied Balance Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
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
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Secondary Cylinder Forces",
                        "secondaryCylinderForces",
                        FAIndex.SECONDARY,
                    ),
                ],
                "appliedCylinderForces",
                False,
            ),
            TopicData(
                "Applied Elevation Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "appliedElevationForces",
                False,
            ),
            TopicData(
                "Applied Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                    NearNeighborsDifferencesField("Near neighbors factor"),
                    FarNeighborsFactorsField("Far neighbors factor"),
                ],
                "appliedForces",
                False,
            ),
            TopicData(
                "Applied Offset Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "appliedOffsetForces",
                command="OffsetForces",
            ),
            TopicData(
                "Applied Static Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "appliedStaticForces",
            ),
            TopicData(
                "Applied Thermal Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "appliedThermalForces",
                False,
            ),
            TopicData(
                "Applied Velocity Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "appliedVelocityForces",
                False,
            ),
            TopicData(
                "Pre-clipped Acceleration Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "preclippedAccelerationForces",
            ),
            TopicData(
                "Pre-clipped Active Optic Forces",
                [TopicField("Z Forces", "zForces", FAIndex.Z)],
                "preclippedActiveOpticForces",
            ),
            TopicData(
                "Pre-clipped Azimuth Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "preclippedAzimuthForces",
            ),
            TopicData(
                "Pre-clipped Balance Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "preclippedBalanceForces",
            ),
            TopicData(
                "Pre-clipped Cylinder Forces",
                [
                    TopicField(
                        "Primary Cylinder Forces",
                        "primaryCylinderForces",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Secondary Cylinder Forces",
                        "secondaryCylinderForces",
                        FAIndex.SECONDARY,
                    ),
                ],
                "preclippedCylinderForces",
            ),
            TopicData(
                "Pre-clipped Elevation Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "preclippedElevationForces",
            ),
            TopicData(
                "Pre-clipped Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "preclippedForces",
            ),
            TopicData(
                "Pre-clipped Offset Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "preclippedOffsetForces",
            ),
            TopicData(
                "Pre-clipped Static Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "preclippedStaticForces",
            ),
            TopicData(
                "Pre-clipped Thermal Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "preclippedThermalForces",
            ),
            TopicData(
                "Pre-clipped Velocity Forces",
                [
                    TopicField("Z Forces", "zForces", FAIndex.Z),
                    TopicField("Y Forces", "yForces", FAIndex.Y),
                    TopicField("X Forces", "xForces", FAIndex.X),
                ],
                "preclippedVelocityForces",
            ),
            TopicData(
                "Measured forces",
                [
                    TopicField(
                        "Primary Cylinder Forces",
                        "primaryCylinderForce",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Secondary Cylinder Forces",
                        "secondaryCylinderForce",
                        FAIndex.SECONDARY,
                    ),
                    TopicField(
                        "Z Forces",
                        "zForce",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Y Forces",
                        "yForce",
                        FAIndex.Y,
                    ),
                    TopicField(
                        "X Forces",
                        "xForce",
                        FAIndex.X,
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
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Secondary Cylinder FE",
                        "secondaryCylinderFollowingError",
                        FAIndex.SECONDARY,
                    ),
                    XFEForces("X Forces"),
                    YFEForces("Y Forces"),
                    ZFEForces("Z Forces"),
                ],
                "forceActuatorData",
                False,
            ),
            TopicData(
                "FA Raising State",
                [
                    WaitingField("Waiting for Z FA", "waitZForceActuator", FAIndex.Z),
                    WaitingField("Waiting for Y FA", "waitYForceActuator", FAIndex.Y),
                    WaitingField("Waiting for X FA", "waitXForceActuator", FAIndex.X),
                ],
                "raisingLoweringInfo",
            ),
            TopicData(
                "FA Info",
                [
                    TopicField(
                        "Actuator Type",
                        "actuatorType",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Actuator Orientation",
                        "actuatorOrientation",
                        FAIndex.Z,
                    ),
                    TopicField("Subnet", "modbusSubnet", FAIndex.Z),
                    TopicField("Address", "modbusAddress", FAIndex.Z),
                    TopicField("X Position", "xPosition", FAIndex.Z),
                    TopicField("Y Position", "yPosition", FAIndex.Z),
                    TopicField("Z Position", "zPosition", FAIndex.Z),
                    TopicField(
                        "Major Revision",
                        "majorRevision",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Minor Revision",
                        "minorRevision",
                        FAIndex.Z,
                    ),
                    TopicField("ADC Scan Rate", "adcScanRate", FAIndex.Z),
                    TopicField("Reference ID", "referenceId", FAIndex.Z),
                    TopicField(
                        "X Data Reference Id",
                        "xDataReferenceId",
                        FAIndex.X,
                    ),
                    TopicField(
                        "Y Data Reference Id",
                        "yDataReferenceId",
                        FAIndex.Y,
                    ),
                    TopicField(
                        "Z Data Reference Id",
                        "zDataReferenceId",
                        FAIndex.Z,
                    ),
                    TopicField("ILC Unique Id", "ilcUniqueId", FAIndex.Z),
                    TopicField(
                        "ILC application type",
                        "ilcApplicationType",
                        FAIndex.Z,
                    ),
                    TopicField("Network Node Type", "networkNodeType", FAIndex.Z),
                    TopicField(
                        "ILC Selected Options",
                        "ilcSelectedOptions",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Network Node Options",
                        "networkNodeOptions",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Mezzanine Unique ID",
                        "mezzanineUniqueId",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Mezzanine Firmware Type",
                        "mezzanineFirmwareType",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Mezzanine Major Revision",
                        "mezzanineMajorRevision",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Mezzanine Minor Revision",
                        "mezzanineMinorRevision",
                        FAIndex.Z,
                    ),
                ],
                "forceActuatorInfo",
            ),
            FAIndicesData("FA Indices"),
            TopicData(
                "FA Settings",
                [
                    EnabledDisabledField(
                        "Enabled/Disabled", "enabledActuators", FAIndex.Z
                    ),
                    TopicField(
                        "Z Applied Force Low Limit",
                        "appliedZForceLowLimit",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Z Applied Force High Limit",
                        "appliedZForceHighLimit",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Y Applied Force Low Limit",
                        "appliedYForceLowLimit",
                        FAIndex.Y,
                    ),
                    TopicField(
                        "Y Applied Force High Limit",
                        "appliedYForceHighLimit",
                        FAIndex.Y,
                    ),
                    TopicField(
                        "X Applied Force Low Limit",
                        "appliedXForceLowLimit",
                        FAIndex.X,
                    ),
                    TopicField(
                        "X Applied Force High Limit",
                        "appliedXForceHighLimit",
                        FAIndex.X,
                    ),
                    TopicField(
                        "Z Measured Force Low Limit",
                        "measuredZForceLowLimit",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Z Measured Force High Limit",
                        "measuredZForceHighLimit",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Y Measured Force Low Limit",
                        "measuredYForceLowLimit",
                        FAIndex.Y,
                    ),
                    TopicField(
                        "Y Measured Force High Limit",
                        "measuredYForceHighLimit",
                        FAIndex.Y,
                    ),
                    TopicField(
                        "X Measured Force Low Limit",
                        "measuredXForceLowLimit",
                        FAIndex.X,
                    ),
                    TopicField(
                        "X Measured Force High Limit",
                        "measuredXForceHighLimit",
                        FAIndex.X,
                    ),
                    TopicField(
                        "PC FE Warning",
                        "primaryFollowingErrorWarningThreshold",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "PC FE Counting",
                        "primaryFollowingErrorCountingFaultThreshold",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "PC FE Immediate",
                        "primaryFollowingErrorImmediateFaultThreshold",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "SC FE Warning",
                        "secondaryFollowingErrorWarningThreshold",
                        FAIndex.SECONDARY,
                    ),
                    TopicField(
                        "SC FE Counting",
                        "secondaryFollowingErrorCountingFaultThreshold",
                        FAIndex.SECONDARY,
                    ),
                    TopicField(
                        "SC FE Immediate",
                        "secondaryFollowingErrorImmediateFaultThreshold",
                        FAIndex.SECONDARY,
                    ),
                ],
                "forceActuatorSettings",
            ),
            # Calibration info is stored for all ILCs, including SAA - so the
            # index shall always be FAIndex.Z
            TopicData(
                "FA Main Calibration Info",
                [
                    TopicField(
                        "Primary Coefficient",
                        "mainPrimaryCylinderCoefficient",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Primary Offset",
                        "mainPrimaryCylinderLoadCellOffset",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Primary Sensitivity",
                        "mainPrimaryCylinderLoadCellSensitivity",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Secondary Coefficient",
                        "mainSecondaryCylinderCoefficient",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Secondary Offset",
                        "mainSecondaryCylinderLoadCellOffset",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Secondary Sensitivity",
                        "mainSecondaryCylinderLoadCellSensitivity",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Primary Cylinder DCA Gain",
                        "mezzaninePrimaryCylinderGain",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Secondary Cylinder DCA Gain",
                        "mezzanineSecondaryCylinderGain",
                        FAIndex.Z,
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
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Primary Offset",
                        "backupPrimaryCylinderLoadCellOffset",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Primary Sensitivity",
                        "backupPrimaryCylinderLoadCellSensitivity",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Secondary Coefficient",
                        "backupSecondaryCylinderCoefficient",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Secondary Offset",
                        "backupSecondaryCylinderLoadCellOffset",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Secondary Sensitivity",
                        "backupSecondaryCylinderLoadCellSensitivity",
                        FAIndex.Z,
                    ),
                ],
                "forceActuatorInfo",
            ),
            TopicData(
                "FA State",
                [TopicField("ILC State", "ilcState", FAIndex.Z)],
                "forceActuatorState",
            ),
            TopicData(
                "FA Warning",
                [
                    WarningField("Major Fault", "majorFault", FAIndex.Z),
                    WarningField("Minor Fault", "minorFault", FAIndex.Z),
                    WarningField(
                        "Fault Override",
                        "faultOverride",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Main Calibration Error",
                        "mainCalibrationError",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Backup Calibration Error",
                        "backupCalibrationError",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Mezzanine Error",
                        "mezzanineError",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Mezzanine Bootloader Active",
                        "mezzanineBootloaderActive",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Unique Id CRC Error",
                        "uniqueIdCRCError",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Application Type Mismatch",
                        "applicationTypeMismatch",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Application Missing",
                        "applicationMissing",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "OneWire Mismatch",
                        "oneWireMissing",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "OneWire1 Mismatch",
                        "oneWire1Mismatch",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "OnewWire2 Mismatch",
                        "oneWire2Mismatch",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Watchdog Reset",
                        "watchdogReset",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Brownout",
                        "brownOut",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Event Trap Reset",
                        "eventTrapReset",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "SSR Power Fault",
                        "ssrPowerFault",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "AUX Power Fault",
                        "auxPowerFault",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Mezzanine Power Fault",
                        "mezzaninePowerFault",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Mezzanine Current Ampl Fault",
                        "mezzanineCurrentAmp1Fault",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Mezzanine Current Amp2 Fault",
                        "mezzanineCurrentAmp2Fault",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Mezzanine Unique ID CRC Error",
                        "mezzanineUniqueIdCRCError",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Mezzanine Main Calibration Error",
                        "mezzanineMainCalibrationError",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Mezzanine Backup Calibration Error",
                        "mezzanineBackupCalibrationError",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Mezzanine Event Trap Reset",
                        "mezzanineEventTrapReset",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Mezzanine Application Missing",
                        "mezzanineApplicationMissing",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Mezzanine Application CRC Mismatch",
                        "mezzanineApplicationCRCMismatch",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "ILC Fault",
                        "ilcFault",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Broadcast Counter Warning",
                        "broadcastCounterWarning",
                        FAIndex.Z,
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
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Y Measured Force Warning",
                        "measuredYForceWarning",
                        FAIndex.Y,
                    ),
                    WarningField(
                        "X Measured Force Warning",
                        "measuredXForceWarning",
                        FAIndex.X,
                    ),
                    WarningField(
                        "Primary Axis FE Warning",
                        "primaryAxisFollowingErrorWarning",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Secondary Axis FE Warning",
                        "secondaryAxisFollowingErrorWarning",
                        FAIndex.SECONDARY,
                    ),
                    WarningField(
                        "Primary Axis FE Counting Fault",
                        "primaryAxisFollowingErrorCountingFault",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Secondary Axis FE Counting Fault",
                        "secondaryAxisFollowingErrorCountingFault",
                        FAIndex.SECONDARY,
                    ),
                    WarningField(
                        "Primary Axis FE Immediate Fault",
                        "primaryAxisFollowingErrorImmediateFault",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Secondary Axis FE Immediate Fault",
                        "secondaryAxisFollowingErrorImmediateFault",
                        FAIndex.SECONDARY,
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
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Secondary axis FE warning counter",
                        "secondaryAxisFollowingErrorWarningCounter",
                        FAIndex.SECONDARY,
                    ),
                    TopicField(
                        "Primary axis FE counting counter",
                        "primaryAxisFollowingErrorCountingCounter",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Secondary axis FE counting counter",
                        "secondaryAxisFollowingErrorCountingCounter",
                        FAIndex.SECONDARY,
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
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Near neighbor",
                        "nearNeighborWarning",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Far neighbor",
                        "farNeighborWarning",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Elevation force",
                        "elevationForceWarning",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Azimuth force",
                        "azimuthForceWarning",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Thermal force",
                        "thermalForceWarning",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Balance force",
                        "balanceForceWarning",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Acceleration force",
                        "accelerationForceWarning",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Active optic",
                        "activeOpticForceWarning",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Static force",
                        "staticForceWarning",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Offset force",
                        "offsetForceWarning",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Velocity force",
                        "velocityForceWarning",
                        FAIndex.Z,
                    ),
                    WarningField(
                        "Force setpoint",
                        "forceWarning",
                        FAIndex.Z,
                    ),
                ],
                "forceSetpointWarning",
            ),
            TopicData(
                "FA Bump Test",
                [
                    BumpTestField("Primary Test", "primaryTest", FAIndex.Z),
                    BumpTestField(
                        "Secondary Test",
                        "secondaryTest",
                        FAIndex.SECONDARY,
                    ),
                    TopicField(
                        "Primary Timestamps",
                        "primaryTestTimestamps",
                        FAIndex.Z,
                    ),
                    TopicField(
                        "Secondary Timestamps",
                        "secondaryTestTimestamps",
                        FAIndex.SECONDARY,
                    ),
                ],
                "forceActuatorBumpTestStatus",
            ),
            TopicData(
                "FA Enabled",
                [
                    EnabledDisabledField(
                        "Enabled FAs",
                        "forceActuatorEnabled",
                        FAIndex.Z,
                    ),
                ],
                "enabledForceActuators",
            ),
        )
