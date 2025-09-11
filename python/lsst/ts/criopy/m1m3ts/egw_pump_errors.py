# This file is part of ts_xml.
#
# Developed for the LSST Telescope & Site.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License

__all__ = ["EGWPumpErrors"]

from dataclasses import dataclass
from enum import IntEnum


class PumpFaultType(IntEnum):
    NO_ERROR = 0
    AUTO_RESET_RUN = 1
    NON_RESETTABLE = 2


@dataclass
class PumpError:
    fault: str
    fault_type: PumpFaultType
    description: str
    action: list[str]


"""
Details of EGW Glycol Pump VFD (PowerFlex 520, Allen-Bradley/Rockwell
Automation) 1 byte error code.

Datasheet listing the errors is availabe online at
https://literature.rockwellautomation.com/idc/groups/literature/documents/um/520-um001_-en-e.pdf
See table in Chapter 4, Troubleshooting, Fault Descriptions.
"""
EGWPumpErrors = {
    0: PumpError("No Fault", PumpFaultType.NO_ERROR, "No fault present.", []),
    2: PumpError(
        "Auxiliary Input",
        PumpFaultType.AUTO_RESET_RUN,
        "External trip (Auxiliary) input.",
        [
            "Check remote wiring.",
            "Verify communications programming for intentional fault.",
        ],
    ),
    3: PumpError(
        "Power Loss",
        PumpFaultType.NON_RESETTABLE,
        "Single-phase operation detected with excessive load.",
        [
            "Monitor the incoming AC line for low voltage or line power interruption.",
            "Check input fuses.",
            "Reduce load.",
        ],
    ),
    4: PumpError(
        "UnderVoltage",
        PumpFaultType.AUTO_RESET_RUN,
        "DC bus voltage fell below the min value.",
        ["Monitor the incoming AC line for low voltage or line power interruption."],
    ),
    5: PumpError(
        "OverVoltage",
        PumpFaultType.AUTO_RESET_RUN,
        "DC bus voltage exceeded max value.",
        [
            "Monitor the AC line for high line voltage or transient conditions. "
            "Bus overvoltage can also be caused by motor regeneration. "
            "Extend the decel time or install dynamic brake option."
        ],
    ),
    6: PumpError(
        "Motor Stalled",
        PumpFaultType.AUTO_RESET_RUN,
        "Drive is unable to accelerate or decelerate motor.",
        [
            "Increase P041, A442, A444, A446 [Accel Time x] or reduce load so drive output current does not "
            "exceed the current set by parameter A484, A485 [Current Limit x] for too long.",
            "Check for overhauling load.",
        ],
    ),
    7: PumpError(
        "Motor Overload",
        PumpFaultType.AUTO_RESET_RUN,
        "Internal electronic overload trip.",
        [
            "An excessive motor load exists. Reduce load so drive output current does not exceed the current "
            "set by parameter P033 [Motor OL Current].",
            "Verify A530 [Boost Select] setting.",
        ],
    ),
    8: PumpError(
        "Heatsink OvrTmp",
        PumpFaultType.AUTO_RESET_RUN,
        "Heatsink/Power Module temperature exceeds a predefined value.",
        [
            "Check for blocked or dirty heatsink fins. Verify that ambient temperature has not exceeded the "
            "rated ambient temperature.",
            "Check fan.",
        ],
    ),
    9: PumpError(
        "CC OvrTmp",
        PumpFaultType.AUTO_RESET_RUN,
        "Control module temperature exceeds a predefined value.",
        [
            "Check product ambient temperature.",
            "Check for airflow obstruction.",
            "Check for dirt or debris.",
            "Check fan.",
        ],
    ),
    12: PumpError(
        "HW OverCurrent",
        PumpFaultType.NON_RESETTABLE,
        "The drive output current has exceeded the hardware current limit.",
        [
            "Check programming.",
            "Check for excess load, improper A530 [Boost Select] setting, DC brake volts set too high or "
            "other causes of excess current.",
        ],
    ),
    13: PumpError(
        "Ground Fault",
        PumpFaultType.AUTO_RESET_RUN,
        "A current path to earth ground has been detected at one or more of the drive output terminals.",
        [
            "Check the motor and external wiring to the drive output terminals for a grounded condition."
        ],
    ),
    15: PumpError(
        "Load Loss",
        PumpFaultType.NON_RESETTABLE,
        "The output torque current is below the value that is programmed in A490 [Load Loss Level] for "
        "a time period greater than the time programmed in A491 [Load Loss Time].",
        [
            "Verify connections between motor and load.",
            "Verify level and time requirements.",
        ],
    ),
    21: PumpError(
        "Output Ph Loss",
        PumpFaultType.AUTO_RESET_RUN,
        "Output Phase Loss (if enabled). Configure with A557 [Out Phas Loss En].",
        ["Verify motor wiring.", "Verify motor."],
    ),
    29: PumpError(
        "Analog In Loss",
        PumpFaultType.AUTO_RESET_RUN,
        "An analog input is configured to fault on signal loss. A signal loss has occurred. "
        "Configure with t094 [Anlg In V Loss] or t097 [Anlg In mA Loss].",
        ["Check for broken/loose connections at inputs.", "Check parameters."],
    ),
    33: PumpError(
        "Auto Rstrt Tries",
        PumpFaultType.NON_RESETTABLE,
        "Drive unsuccessfully attempted to reset a fault and resume running for the programmed "
        "number of A541 [Auto Rstrt Tries].",
        ["Correct the cause of the fault and manually clear."],
    ),
    38: PumpError(
        "Phase U to Gnd",
        PumpFaultType.NON_RESETTABLE,
        "A phase to ground fault has been detected between the drive and motor in this phase.",
        [
            "Check the wiring between the drive and motor.",
            "Check motor for grounded phase.",
            "Replace drive if fault cannot be cleared.",
        ],
    ),
    39: PumpError(
        "Phase V to Gnd",
        PumpFaultType.NON_RESETTABLE,
        "A phase to ground fault has been detected between the drive and motor in this phase.",
        [
            "Check the wiring between the drive and motor.",
            "Check motor for grounded phase.",
            "Replace drive if fault cannot be cleared.",
        ],
    ),
    40: PumpError(
        "Phase W to Gnd",
        PumpFaultType.NON_RESETTABLE,
        "A phase to ground fault has been detected between the drive and motor in this phase.",
        [
            "Check the wiring between the drive and motor.",
            "Check motor for grounded phase.",
            "Replace drive if fault cannot be cleared.",
        ],
    ),
    41: PumpError(
        "Phase UV Short",
        PumpFaultType.NON_RESETTABLE,
        "Excessive current has been detected between these two output terminals.",
        [
            "Check the motor and drive output terminal wiring for a shorted condition.",
            "Replace drive if fault cannot be cleared.",
        ],
    ),
    42: PumpError(
        "Phase UW Short",
        PumpFaultType.NON_RESETTABLE,
        "Excessive current has been detected between these two output terminals.",
        [
            "Check the motor and drive output terminal wiring for a shorted condition.",
            "Replace drive if fault cannot be cleared.",
        ],
    ),
    43: PumpError(
        "Phase VW Short",
        PumpFaultType.NON_RESETTABLE,
        "Excessive current has been detected between these two output terminals.",
        [
            "Check the motor and drive output terminal wiring for a shorted condition.",
            "Replace drive if fault cannot be cleared.",
        ],
    ),
    48: PumpError(
        "Params Defaulted",
        PumpFaultType.AUTO_RESET_RUN,
        "The drive was commanded to write default values to EEPROM.",
        [
            "Clear the fault or cycle power to the drive.",
            "Program the drive parameters as needed.",
        ],
    ),
    59: PumpError(
        "Safety Open",
        PumpFaultType.AUTO_RESET_RUN,
        "Both of the safety inputs (Safety 1, Safety 2) are not enabled. "
        "Configure with t105 [Safety Open En].",
        [
            "Check safety input signals. "
            "If not using safety, verify and tighten jumper for I/ O terminals S1, S2, and S+."
        ],
    ),
    63: PumpError(
        "SW OverCurrent",
        PumpFaultType.AUTO_RESET_RUN,
        "Programmed A486, A488 [Shear Pinx Level] has been exceeded for a time period greater than the time "
        "programmed in A487, A489 [Shear Pin x Time].",
        [
            "Verify connections between motor and load.",
            "Verify level and time requirements.",
        ],
    ),
    64: PumpError(
        "Drive Overload",
        PumpFaultType.NON_RESETTABLE,
        "Drive overload rating has been exceeded.",
        ["Reduce load or extend Accel Time."],
    ),
    70: PumpError(
        "Power Unit",
        PumpFaultType.NON_RESETTABLE,
        "Failure has been detected in the drive power section.",
        [
            "Check that max ambient temperature has not been exceeded.",
            "Cycle power.",
            "Replace drive if fault cannot be cleared.",
        ],
    ),
    71: PumpError(
        "DSI Net Loss",
        PumpFaultType.NON_RESETTABLE,
        "Control over the Modbus or DSI communication link has been interrupted.",
        [
            "Cycle power.",
            "Check communications cabling.",
            "Check Modbus or DSI setting.",
            "Check Modbus or DSI status.",
        ],
    ),
    72: PumpError(
        "Opt Net Loss",
        PumpFaultType.NON_RESETTABLE,
        "Control over the network option card’s remote network has been interrupted.",
        [
            "Cycle power.",
            "Check communications cabling.",
            "Check network adapter setting.",
            "Check external network status.",
        ],
    ),
    73: PumpError(
        "EN Net Loss",
        PumpFaultType.NON_RESETTABLE,
        "Control through the embedded EtherNet/IP adapter has been interrupted.",
        [
            "Cycle power.",
            "Check communications cabling.",
            "Check EtherNet/IP setting.",
            "Check external network status.",
        ],
    ),
    80: PumpError(
        "Autotune Failure",
        PumpFaultType.NON_RESETTABLE,
        "The autotune function was either canceled by the user or failed.",
        ["Restart procedure."],
    ),
    81: PumpError(
        "DSI Comm Loss",
        PumpFaultType.NON_RESETTABLE,
        "Communications between the drive and the Modbus or DSI master device have been interrupted.",
        [
            "Cycle power.",
            "Check communications cabling.",
            "Check Modbus or DSI setting.",
            "Check Modbus or DSI status.",
            "Modify using C125 [Comm Loss Action].",
            "Connecting I/O terminals C1 and C2 to ground may improve noise immunity.",
            "Replace wiring, Modbus master device, or control module.",
        ],
    ),
    82: PumpError(
        "Opt Comm Loss",
        PumpFaultType.NON_RESETTABLE,
        "Communications between the drive and the network option card have been interrupted.",
        [
            "Cycle power.",
            "Reinstall option card in drive.",
            "Modify using C125 [Comm Loss Action].",
            "Replace wiring, port expander, option card, or control module.",
        ],
    ),
    83: PumpError(
        "EN Comm Loss",
        PumpFaultType.NON_RESETTABLE,
        "Internal communications between the drive and the embedded EtherNet/IP adapter have been "
        "interrupted.",
        [
            "Cycle power.",
            "Check EtherNet/IP setting.",
            "Check drive’s Ethernet settings and diagnostic parameters.",
            "Modify using C125 [Comm Loss Action].",
            "Replace wiring, Ethernet switch, or control module.",
        ],
    ),
    91: PumpError(
        "Encoder Loss",
        PumpFaultType.NON_RESETTABLE,
        "Requires differential encoder. One of the 2 encoder channel signals is missing.",
        [
            "Check Wiring.",
            r"If P047, P049, P051 [Speed Referencex] = 16 \“Positioning\” and A535 [Motor Fdbk Type] = 5 "
            r"\“Quad Check\”, swap the Encoder channel inputs or swap any two motor leads.",
            "Replace encoder.",
        ],
    ),
    94: PumpError(
        "Function Loss",
        PumpFaultType.NON_RESETTABLE,
        r"\“Freeze-Fire\” (Function Loss) input is inactive, input to the programmed terminal is open.",
        ["Close input to the terminal and cycle power."],
    ),
    100: PumpError(
        "Parameter Chksum",
        PumpFaultType.NON_RESETTABLE,
        "Drive parameter non-volatile storage is corrupted.",
        [r"Set P053 [Reset To Defalts] to 2 \“Factory Rset\”."],
    ),
    101: PumpError(
        "External Storage",
        PumpFaultType.NON_RESETTABLE,
        "External non-volatile storage has failed.",
        [r"Set P053 [Reset To Defalts] to 2 \“Factory Rset\”."],
    ),
    105: PumpError(
        "C Connect Err",
        PumpFaultType.NON_RESETTABLE,
        "Control module was disconnected while drive was powered.",
        [
            "Clear fault and verify all parameter settings. "
            "Do not remove or install the control module while power is applied."
        ],
    ),
    106: PumpError(
        "Incompat C-P",
        PumpFaultType.NON_RESETTABLE,
        "The PowerFlex 525 control module does not support power modules with 0.25 HP power rating.",
        [
            "Change to a different power module.",
            "Change to a PowerFlex 523 control module.",
        ],
    ),
    107: PumpError(
        "Replaced C-P",
        PumpFaultType.NON_RESETTABLE,
        "The control module could not recognize the power module. Hardware failure.",
        [
            "Change to a different power module.",
            "Replace control module if changing power module does not work.",
        ],
    ),
    109: PumpError(
        "Mismatch C-P",
        PumpFaultType.NON_RESETTABLE,
        "The control module was mounted to a different drive type power module.",
        [r"Set P053 [Reset To Defalts] to 3 \“Power Reset\”."],
    ),
    110: PumpError(
        " Keypad Membrane",
        PumpFaultType.NON_RESETTABLE,
        "Keypad membrane failure / disconnected.",
        ["Cycle power.", "Replace control module if fault cannot be cleared."],
    ),
    111: PumpError(
        "Safety Hardware",
        PumpFaultType.NON_RESETTABLE,
        "Safety input enable hardware malfunction. One of the safety inputs is not enabled.",
        [
            "Check safety input signals. "
            "If not using safety, verify and tighten jumper for I/ O terminals S1, S2, and S+.",
            "Replace control module if fault cannot be cleared.",
        ],
    ),
    114: PumpError(
        "uC Failure",
        PumpFaultType.NON_RESETTABLE,
        "Microprocessor failure.",
        [
            "Cycle power.",
            "Verify grounding requirements. "
            "See General Grounding Requirements on page 20 for more information.",
            "Replace control module if fault cannot be cleared.",
        ],
    ),
    122: PumpError(
        "I/O Board Fail",
        PumpFaultType.NON_RESETTABLE,
        "Failure has been detected in the drive control and I/O section.",
        ["Cycle power.", "Replace drive or control module if fault cannot be cleared."],
    ),
    125: PumpError(
        "Flash Update Req",
        PumpFaultType.NON_RESETTABLE,
        "The firmware in the drive is corrupt, mismatched, or incompatible with the hardware.",
        [
            "Perform a firmware flash update operation to attempt to load a valid set of firmware."
        ],
    ),
    126: PumpError(
        "NonRecoverablErr",
        PumpFaultType.NON_RESETTABLE,
        "A nonrecoverable firmware or hardware error was detected. "
        "The drive was automatically stopped and reset.",
        [
            "Clear fault or cycle power to the drive.",
            "Replace drive or control module if fault cannot be cleared.",
        ],
    ),
    127: PumpError(
        "DSIFlashUpdatReq",
        PumpFaultType.NON_RESETTABLE,
        "A critical problem with the firmware was detected and the drive is running using backup firmware "
        "that only supports DSI communications.",
        [
            "Perform a firmware flash update operation using DSI communications to attempt to load "
            "a valid set of firmware."
        ],
    ),
}
