# This file is part of cRIO GUI library.
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

from lsst.ts import salobj
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ..gui import (
    RPM,
    Ampere,
    ConnectedLabel,
    DataDegC,
    DataFormButton,
    DataFormWidget,
    DataLabel,
    DataUnitLabel,
    ErrorLabel,
    Heartbeat,
    Hours,
    KiloWatt,
    OnOffLabel,
    Percent,
    PowerOnOffLabel,
    PressureInmBar,
    TimeChartView,
    UserSelectedTimeChart,
    Volt,
    WarningLabel,
)
from ..gui.sal import CSCControlWidget, LogWidget, SummaryStateLabel, VersionWidget
from ..salcomm import MetaSAL

__all__ = ["CompressorPageWidget"]

# Constants for button titles. Titles are used to select command send to
# SAL.

TEXT_POWER_ON = "Power &On"
TEXT_POWER_OFF = "Power O&ff"
TEXT_RESET = "&Reset"


class CompressorCSC(CSCControlWidget):
    """Air compressor's control widget."""

    def __init__(self, comm: MetaSAL):
        super().__init__(comm)

    def get_state_buttons_map(self, state: int) -> list[str | None]:
        default_buttons = super().get_state_buttons_map(state)
        status = self.comm.remote.evt_status.get()

        if status is None or state != salobj.State.ENABLED:
            return default_buttons + ([None] * 3)

        return default_buttons + [
            TEXT_POWER_ON if status.startByRemote is True else None,
            (
                TEXT_POWER_OFF
                if status.startByRemote is False and status.operating is True
                else None
            ),
            TEXT_RESET,
        ]


class CompressorPageWidget(QWidget):
    def __init__(self, compressor: MetaSAL):
        super().__init__()
        self.compressor = compressor

        master_layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        user_time_chart = UserSelectedTimeChart(
            {compressor.remote.tel_analogData: compressor.analogData}
        )

        errors_widget = DataFormButton(
            "Errors",
            compressor.errors,
            [
                (
                    "Power supply failure",
                    ErrorLabel(field="powerSupplyFailureE400"),
                ),
                (
                    "Emergency stop activated",
                    ErrorLabel(field="emergencyStopActivatedE401"),
                ),
                (
                    "High motor temperature",
                    ErrorLabel(field="highMotorTemperatureM1E402"),
                ),
                (
                    "Compressor discharge temperature",
                    ErrorLabel(field="compressorDischargeTemperatureE403"),
                ),
                (
                    "Start Temperature low",
                    ErrorLabel(field="startTemperatureLowE404"),
                ),
                (
                    "Discharge over pressure",
                    ErrorLabel(field="dischargeOverPressureE405"),
                ),
                (
                    "Line pressure sensor",
                    ErrorLabel(field="linePressureSensorB1E406"),
                ),
                (
                    "Discharge Temperature Sensor B2",
                    ErrorLabel(field="dischargePressureSensorB2E407"),
                ),
                (
                    "Discharge Temperature Sensor R2",
                    ErrorLabel(field="dischargeTemperatureSensorR2E408"),
                ),
                (
                    "Controller Hardware",
                    ErrorLabel(field="controllerHardwareE409"),
                ),
                ("Cooling", ErrorLabel(field="coolingE410")),
                ("Oil Pressure Low", ErrorLabel(field="oilPressureLowE411")),
                ("External Fault", ErrorLabel(field="externalFaultE412")),
                ("Dryer", ErrorLabel(field="dryerE413")),
                ("Condensate Drain", ErrorLabel(field="condensateDrainE414")),
                (
                    "No Pressure Build Up",
                    ErrorLabel(field="noPressureBuildUpE415"),
                ),
                ("Heavy Startup", ErrorLabel(field="heavyStartupE416")),
                (
                    "Pre Adjustment VSD",
                    ErrorLabel(field="preAdjustmentVSDE500"),
                ),
                ("Pre Adjustment", ErrorLabel(field="preAdjustmentE501")),
                ("Locked VSD", ErrorLabel(field="lockedVSDE502")),
                ("Write Fault VSD", ErrorLabel(field="writeFaultVSDE503")),
                ("Communication VSD", ErrorLabel(field="communicationVSDE504")),
                ("Stop Pressed VSD", ErrorLabel(field="stopPressedVSDE505")),
                ("Stop Input EMV", ErrorLabel(field="stopInputEMVSDE506")),
                ("Read Fault VSD", ErrorLabel(field="readFaultVSDE507")),
                ("Stop Input VSD", ErrorLabel(field="stopInputVSDEME508")),
                ("See VSD", ErrorLabel(field="seeVSDDisplayE509")),
                (
                    "Speed Below Minimal Limit",
                    ErrorLabel(field="speedBelowMinLimitE510"),
                ),
            ],
        )

        warnings_widget = DataFormButton(
            "Warnings",
            compressor.warnings,
            [
                ("Service Due", WarningLabel(field="serviceDueA600")),
                (
                    "Discharge Over Pressure",
                    WarningLabel(field="dischargeOverPressureA601"),
                ),
                (
                    "Compressor Discharge Temperature",
                    WarningLabel(field="compressorDischargeTemperatureA602"),
                ),
                (
                    "Line Pressure High",
                    WarningLabel(field="linePressureHighA606"),
                ),
                (
                    "Controller Battery Empty",
                    WarningLabel(field="controllerBatteryEmptyA607"),
                ),
                ("Drier", WarningLabel(field="dryerA608")),
                ("Condensate Drain", WarningLabel(field="condensateDrainA609")),
                ("Fine Separator", WarningLabel(field="fineSeparatorA610")),
                ("Air Filter", WarningLabel(field="airFilterA611")),
                ("Oil Filter", WarningLabel(field="oilFilterA612")),
                ("Oil Level Low", WarningLabel(field="oilLevelLowA613")),
                (
                    "Oil Temperature High",
                    WarningLabel(field="oilTemperatureHighA614"),
                ),
                ("External Warning", WarningLabel(field="externalWarningA615")),
                (
                    "Motor Lubrication System",
                    WarningLabel(field="motorLuricationSystemA616"),
                ),
                ("Input 1", WarningLabel(field="input1A617")),
                ("Input 2", WarningLabel(field="input2A618")),
                ("Input 3", WarningLabel(field="input3A619")),
                ("Input 4", WarningLabel(field="input4A620")),
                ("Input 5", WarningLabel(field="input5A621")),
                ("Input 6", WarningLabel(field="input6A622")),
                ("Full SD Card", WarningLabel(field="fullSDCardA623")),
                (
                    "Temperature High VSD",
                    WarningLabel(field="temperatureHighVSDA700"),
                ),
            ],
        )

        data_layout = QVBoxLayout()
        data_layout.addWidget(
            DataFormWidget(
                self.compressor.compressorInfo,
                [
                    (
                        "Compressor Software Version",
                        DataLabel(field="softwareVersion"),
                    ),
                    ("Serial Number", DataLabel(field="serialNumber")),
                ],
            )
        )

        data_layout.addWidget(
            DataFormWidget(
                self.compressor.analogData,
                [
                    ("Water level", Percent(field="waterLevel", fmt=".0f")),
                    ("Target speed", RPM(field="targetSpeed")),
                    ("Motor current", Ampere(field="motorCurrent")),
                    (
                        "Heatsink temperature",
                        DataDegC(field="heatsinkTemperature", fmt=".0f"),
                    ),
                    ("DC link voltage", Volt(field="dclinkVoltage", fmt=".0f")),
                    (
                        "Motor speed percentage",
                        Percent(field="motorSpeedPercentage", fmt=".0f"),
                    ),
                    ("Motor speed RPM", RPM(field="motorSpeedRPM")),
                    ("Motor input", KiloWatt(field="motorInput")),
                    (
                        "Volume percentage",
                        Percent(field="compressorVolumePercentage", fmt=".0f"),
                    ),
                    (
                        "Volume",
                        DataUnitLabel(
                            field="compressorVolume", unit="m3/min", fmt=".01f"
                        ),
                    ),
                    (
                        "Stage 1 output pressure",
                        PressureInmBar(field="stage1OutputPressure"),
                    ),
                    ("Line pressure", PressureInmBar(field="linePressure")),
                    (
                        "Stage 1 output temperature",
                        DataDegC(field="stage1OutputTemperature", fmt=".0f"),
                    ),
                ],
                user_time_chart,
            )
        )

        data_layout.addWidget(
            DataFormWidget(
                self.compressor.timerInfo,
                [
                    ("Running hours", Hours("runningHours")),
                    (
                        "Loaded hours",
                        Hours("loadedHours"),
                    ),
                    ("Lowest service counter", Hours("lowestServiceCounter")),
                    ("Run-On timer", Hours("runOnTimer")),
                ],
            )
        )

        startInhibitDetail = DataFormButton(
            "Inhibit status",
            compressor.status,
            [
                ("Start by remote", OnOffLabel(field="startByRemote")),
                (
                    "Start with timer control",
                    OnOffLabel(field="startWithTimerControl"),
                ),
                (
                    "Start with pressure requirement",
                    OnOffLabel(field="startWithPressureRequirement"),
                ),
                (
                    "Start after de-pressurise",
                    OnOffLabel(field="startAfterDePressurise"),
                ),
                (
                    "Start after power-loss",
                    OnOffLabel(field="startAfterPowerLoss"),
                ),
                (
                    "Start after dryer pre-run",
                    OnOffLabel(field="startAfterDryerPreRun"),
                ),
            ],
        )

        status_layout = QVBoxLayout()
        status_layout.addWidget(
            DataFormWidget(
                self.compressor.status,
                [
                    ("Ready to start", OnOffLabel(field="readyToStart")),
                    ("Operating", PowerOnOffLabel(field="operating")),
                    ("Start inhibit", OnOffLabel(field="startInhibit")),
                    (None, startInhibitDetail),
                    ("Motor start phase", OnOffLabel(field="motorStartPhase")),
                    ("Off load", OnOffLabel(field="offLoad")),
                    ("Soft stop", OnOffLabel(field="softStop")),
                    ("Run on timer", OnOffLabel(field="runOnTimer")),
                    ("Fault", WarningLabel(field="fault")),
                    ("Warning", WarningLabel(field="warning")),
                    ("Service required", WarningLabel(field="serviceRequired")),
                    (
                        "Min. allowed speed",
                        WarningLabel(field="minAllowedSpeedAchieved"),
                    ),
                    (
                        "Max. allowed speed",
                        WarningLabel(field="maxAllowedSpeedAchieved"),
                    ),
                ],
            )
        )

        status_layout.addWidget(VersionWidget(self.compressor))

        self.__control_widget = CompressorCSC(self.compressor)

        self.__control_widget.layout().addWidget(
            SummaryStateLabel(self.compressor.summaryState, "summaryState")
        )

        self.__control_widget.layout().addSpacing(15)
        self.__control_widget.layout().addWidget(
            ConnectedLabel(self.compressor.connectionStatus, "connected")
        )

        hb = Heartbeat(indicator=False)
        self.compressor.heartbeat.connect(hb.heartbeat)
        self.__control_widget.layout().addWidget(hb)

        self.power_on = self.__control_widget.add_csc_button(TEXT_POWER_ON, "powerOn")
        self.power_off = self.__control_widget.add_csc_button(
            TEXT_POWER_OFF, "powerOff"
        )
        self.reset = self.__control_widget.add_csc_button(TEXT_RESET, "reset")

        self.__control_widget.layout().addWidget(errors_widget)
        self.__control_widget.layout().addWidget(warnings_widget)

        self.__control_widget.layout().addStretch()

        top_layout.addWidget(self.__control_widget)
        top_layout.addLayout(data_layout)
        top_layout.addLayout(status_layout)
        top_layout.addWidget(TimeChartView(user_time_chart))

        master_layout.addLayout(top_layout)
        master_layout.addWidget(LogWidget(self.compressor))

        self.setLayout(master_layout)

        self.compressor.status.connect(self.status)

    @Slot()
    def status(self, data: salobj.BaseMsgType) -> None:
        summary_state = self.compressor.remote.evt_summaryState.get()
        if summary_state is not None:
            self.__control_widget.csc_state(summary_state)
