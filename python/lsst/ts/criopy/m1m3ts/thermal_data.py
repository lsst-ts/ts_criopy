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

from ..gui.actuatorsdisplay import Scales
from ..gui.sal import TopicCollection, TopicData, TopicField, WarningField

__all__ = ["Thermals"]


class Thermals(TopicCollection):
    """
    Class constructing list of all available topics.
    """

    THERMAL_INDEX = 1

    def __init__(self) -> None:
        super().__init__(
            TopicData(
                "FCU Targets",
                [
                    TopicField(
                        "Heater PWM", "heaterPWM", self.THERMAL_INDEX, fmt=".2f"
                    ),
                    TopicField("Fan RPM", "fanRPM", self.THERMAL_INDEX, fmt="d"),
                ],
                "fcuTargets",
                True,
            ),
            TopicData(
                "Thermal Data",
                [
                    TopicField(
                        "Differential temperature",
                        "differentialTemperature",
                        self.THERMAL_INDEX,
                        fmt=".3f",
                    ),
                    TopicField("Fan RPM", "fanRPM", self.THERMAL_INDEX),
                    TopicField(
                        "Absolute temperature",
                        "absoluteTemperature",
                        self.THERMAL_INDEX,
                        fmt=".3f",
                    ),
                ],
                "thermalData",
                False,
            ),
            TopicData(
                "Thermal Info",
                [
                    TopicField(
                        "Reference ID",
                        "referenceId",
                        self.THERMAL_INDEX,
                        Scales.INTEGER,
                    ),
                    TopicField(
                        "Modbus Address",
                        "modbusAddress",
                        self.THERMAL_INDEX,
                        Scales.INTEGER,
                    ),
                    TopicField("X Position", "xPosition", self.THERMAL_INDEX),
                    TopicField("Y Position", "yPosition", self.THERMAL_INDEX),
                    TopicField("Z Position", "zPosition", self.THERMAL_INDEX),
                    TopicField(
                        "ILC Unique ID",
                        "ilcUniqueId",
                        self.THERMAL_INDEX,
                        Scales.INTEGER,
                    ),
                    TopicField(
                        "ILC Application Type",
                        "ilcApplicationType",
                        self.THERMAL_INDEX,
                        Scales.INTEGER,
                    ),
                    TopicField(
                        "Network Node Type",
                        "networkNodeType",
                        self.THERMAL_INDEX,
                        Scales.INTEGER,
                    ),
                    TopicField(
                        "Major Revision",
                        "majorRevision",
                        self.THERMAL_INDEX,
                        Scales.INTEGER,
                    ),
                    TopicField(
                        "Minor Revision",
                        "minorRevision",
                        self.THERMAL_INDEX,
                        Scales.INTEGER,
                    ),
                ],
                "thermalInfo",
                True,
            ),
            TopicData(
                "Thermal Warning",
                [
                    WarningField("Major fault", "majorFault", self.THERMAL_INDEX),
                    WarningField("Minor fault", "minorFault", self.THERMAL_INDEX),
                    WarningField("Fault override", "faultOverride", self.THERMAL_INDEX),
                    WarningField(
                        "Ref. Resistor Error",
                        "refResistorError",
                        self.THERMAL_INDEX,
                    ),
                    WarningField("RTD Error", "rtdError", self.THERMAL_INDEX),
                    WarningField(
                        "Breaker Heater 1 Erorr",
                        "breakerHeater1Error",
                        self.THERMAL_INDEX,
                    ),
                    WarningField(
                        "Breaker Fan 2 Error",
                        "breakerFan2Error",
                        self.THERMAL_INDEX,
                    ),
                    WarningField(
                        "Unique ID CRC Error",
                        "uniqueIdCRCError",
                        self.THERMAL_INDEX,
                    ),
                    WarningField(
                        "Application Type Mismatch",
                        "applicationTypeMismatch",
                        self.THERMAL_INDEX,
                    ),
                    WarningField(
                        "Application Missing",
                        "applicationMissing",
                        self.THERMAL_INDEX,
                    ),
                    WarningField(
                        "Application CRC Mismatch",
                        "applicationCRCMismatch",
                        self.THERMAL_INDEX,
                    ),
                    WarningField(
                        "One Wire Missing", "oneWireMissing", self.THERMAL_INDEX
                    ),
                    WarningField(
                        "One Wire 1 Mismatch",
                        "oneWire1Mismatch",
                        self.THERMAL_INDEX,
                    ),
                    WarningField(
                        "One Wire 2 Mismatch",
                        "oneWire2Mismatch",
                        self.THERMAL_INDEX,
                    ),
                    WarningField("Watchdog Reset", "watchdogReset", self.THERMAL_INDEX),
                    WarningField("Brown Out", "brownOut", self.THERMAL_INDEX),
                    WarningField(
                        "Event Trap Reset", "eventTrapReset", self.THERMAL_INDEX
                    ),
                    WarningField(
                        "SSR Power Fault", "ssrPowerFault", self.THERMAL_INDEX
                    ),
                    WarningField(
                        "AUX Power Fault", "auxPowerFault", self.THERMAL_INDEX
                    ),
                    WarningField("ILC Fault", "ilcFault", self.THERMAL_INDEX),
                    WarningField(
                        "Broadcast Counter Warnign",
                        "broadcastCounterWarning",
                        self.THERMAL_INDEX,
                    ),
                ],
                "thermalWarning",
                True,
            ),
        )
