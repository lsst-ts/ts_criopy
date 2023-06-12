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

from ..GUI.ActuatorsDisplay import Scales
from ..GUI.SAL.TopicData import TopicData, TopicField, WarningField

__all__ = ["Thermals"]


class Thermals:
    """
    Class constructing list of all available topics.
    """

    def __init__(self):
        self.lastIndex = None

        self.topics = [
            TopicData(
                "Thermal Data",
                [
                    TopicField(
                        "Differential temperature", "differentialTemperature", None
                    ),
                    TopicField("Fan RPM", "fanRPM", None),
                    TopicField("Absolute temperature", "absoluteTemperature", None),
                ],
                "thermalData",
                False,
            ),
            TopicData(
                "Thermal Info",
                [
                    TopicField("Reference ID", "referenceId", None, Scales.INTEGER),
                    TopicField("Modbus Address", "modbusAddress", None, Scales.INTEGER),
                    TopicField("X Position", "xPosition", None),
                    TopicField("Y Position", "yPosition", None),
                    TopicField("Z Position", "zPosition", None),
                    TopicField("ILC Unique ID", "ilcUniqueId", None, Scales.INTEGER),
                    TopicField(
                        "ILC Application Type",
                        "ilcApplicationType",
                        None,
                        Scales.INTEGER,
                    ),
                    TopicField(
                        "Network Node Type", "networkNodeType", None, Scales.INTEGER
                    ),
                    TopicField("Major Revision", "majorRevision", None, Scales.INTEGER),
                    TopicField("Minor Revision", "minorRevision", None, Scales.INTEGER),
                ],
                "thermalInfo",
                True,
            ),
            TopicData(
                "Thermal Warning",
                [
                    WarningField("Major fault", "majorFault", None),
                    WarningField("Minor fault", "minorFault", None),
                    WarningField("Fault override", "faultOverride", None),
                    WarningField("Ref. Resistor Error", "refResistorError", None),
                    WarningField("RTD Error", "rtdError", None),
                    WarningField("Breaker Heater 1 Erorr", "breakerHeater1Error", None),
                    WarningField("Breaker Fan 2 Error", "breakerFan2Error", None),
                    WarningField("Unique ID CRC Error", "uniqueIdCRCError", None),
                    WarningField(
                        "Application Type Mismatch", "applicationTypeMismatch", None
                    ),
                    WarningField("Application Missing", "applicationMissing", None),
                    WarningField(
                        "Application CRC Mismatch", "applicationCRCMismatch", None
                    ),
                    WarningField("One Wire Missing", "oneWireMissing", None),
                    WarningField("One Wire 1 Mismatch", "oneWire1Mismatch", None),
                    WarningField("One Wire 2 Mismatch", "oneWire2Mismatch", None),
                    WarningField("Watchdog Reset", "watchdogReset", None),
                    WarningField("Brown Out", "brownOut", None),
                    WarningField("Event Trap Reset", "eventTrapReset", None),
                    WarningField("SSR Power Fault", "ssrPowerFault", None),
                    WarningField("AUX Power Fault", "auxPowerFault", None),
                    WarningField("ILC Fault", "ilcFault", None),
                    WarningField(
                        "Broadcast Counter Warnign", "broadcastCounterWarning", None
                    ),
                ],
                "thermalWarning",
                True,
            ),
        ]

    def changeTopic(self, index, slot, m1m3ts):
        if self.lastIndex is not None:
            getattr(m1m3ts, self.topics[self.lastIndex].topic).disconnect(slot)

        self.lastIndex = index
        if index is None:
            return

        getattr(m1m3ts, self.topics[index].topic).connect(slot)
