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

from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QButtonGroup,
)
from PySide2.QtCore import Slot
from asyncqt import asyncSlot

from lsst.ts import salobj

from ..GUI import (
    DataLabel,
    DataFormButton,
    DataFormWidget,
    DataUnitLabel,
    Ampere,
    DataDegC,
    Percent,
    PressureInmBar,
    KiloWatt,
    Hours,
    Seconds,
    Volt,
    RPM,
    OnOffLabel,
    PowerOnOffLabel,
    ErrorLabel,
    WarningLabel,
)
from ..GUI import UserSelectedTimeChart, TimeChartView
from ..GUI.SAL import SummaryStateLabel
from ..GUI.SAL.SALLog import Widget as SALLogWidget
from ..GUI.SAL.SALComm import warning


class CompressorsPageWidget(QWidget):
    # Constants for button titles. Titles are used to select command send to
    # SAL.
    TEXT_START = "&Start"
    TEXT_ENABLE = "&Enable"
    TEXT_DISABLE = "&Disable"
    TEXT_STANDBY = "&Standby"
    TEXT_EXIT_CONTROL = "&Exit Control"

    def __init__(self, compressor):
        super().__init__()
        self.compressor = compressor

        self._lastEnabled = None

        masterLayout = QVBoxLayout()
        topLayout = QHBoxLayout()
        commandLayout = QVBoxLayout()

        userTimeChart = UserSelectedTimeChart(
            {compressor.remote.tel_analogData: compressor.analogData}
        )

        errorsWidget = DataFormButton(
            "Errors",
            compressor.errors,
            [
                ("Power supply failure", ErrorLabel(field="powerSupplyFailureE400")),
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
                ("Controller Hardware", ErrorLabel(field="controllerHardwareE409")),
                ("Cooling", ErrorLabel(field="coolingE410")),
                ("Oil Pressure Low", ErrorLabel(field="oilPressureLowE411")),
                ("External Fault", ErrorLabel(field="externalFaultE412")),
                ("Dryer", ErrorLabel(field="dryerE413")),
                ("Condensate Drain", ErrorLabel(field="condensateDrainE414")),
                ("No Pressure Build Up", ErrorLabel(field="noPressureBuildUpE415")),
                ("Heavy Startup", ErrorLabel(field="heavyStartupE416")),
                ("Pre Adjustment VSD", ErrorLabel(field="preAdjustmentVSDE500")),
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

        warningsWidget = DataFormButton(
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
                ("Line Pressure High", WarningLabel(field="linePressureHighA606")),
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
                ("Oil Temperature High", WarningLabel(field="oilTemperatureHighA614")),
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
                ("Temperature High VSD", WarningLabel(field="temperatureHighVSDA700")),
            ],
        )

        self.commandButtons = QButtonGroup(self)
        self.commandButtons.buttonClicked.connect(self._buttonClicked)

        def _addButton(text):
            button = QPushButton(text)
            button.setEnabled(False)
            self.commandButtons.addButton(button)
            commandLayout.addWidget(button)
            return button

        _addButton(self.TEXT_START)
        _addButton(self.TEXT_ENABLE)
        _addButton(self.TEXT_EXIT_CONTROL)

        dataLayout = QVBoxLayout()
        dataLayout.addWidget(
            DataFormWidget(
                self.compressor.compressorInfo,
                [
                    ("Compressor Software Version", DataLabel(field="softwareVersion")),
                    ("Serial Number", DataLabel(field="serialNumber")),
                ],
            )
        )

        dataLayout.addWidget(
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
                        "Power consumption",
                        KiloWatt(field="compressorPowerConsumption"),
                    ),
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
                userTimeChart,
            )
        )

        dataLayout.addWidget(
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
                    ("Loaded hours 50 percent", Seconds("loadedHours50Percent")),
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

        statusLayout = QVBoxLayout()
        statusLayout.addWidget(
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

        commandLayout.addWidget(
            SummaryStateLabel(self.compressor.summaryState, "summaryState")
        )

        commandLayout.addSpacing(15)
        commandLayout.addWidget(errorsWidget)
        commandLayout.addWidget(warningsWidget)

        commandLayout.addStretch()

        topLayout.addLayout(commandLayout)
        topLayout.addLayout(dataLayout)
        topLayout.addLayout(statusLayout)
        topLayout.addWidget(TimeChartView(userTimeChart))

        masterLayout.addLayout(topLayout)
        masterLayout.addWidget(SALLogWidget(self.compressor))

        self.setLayout(masterLayout)

        self.compressor.summaryState.connect(self.summaryState)

    def disableAllButtons(self):
        if self._lastEnabled is None:
            self._lastEnabled = []
            for b in self.commandButtons.buttons():
                self._lastEnabled.append(b.isEnabled())
                b.setEnabled(False)

    def restoreEnabled(self):
        if self._lastEnabled is None:
            return
        bi = 0
        for b in self.commandButtons.buttons():
            b.setEnabled(self._lastEnabled[bi])
            bi += 1

        self._lastEnabled = None

    @Slot(map)
    def summaryState(self, data):
        # text mean button is enabled and given text shall be displayed. None
        # for disabled buttons.
        stateMap = {
            salobj.State.STANDBY: [
                self.TEXT_START,
                None,
                self.TEXT_EXIT_CONTROL,
            ],
            salobj.State.DISABLED: [
                None,
                self.TEXT_ENABLE,
                self.TEXT_STANDBY,
            ],
            salobj.State.ENABLED: [
                None,
                self.TEXT_DISABLE,
                None,
            ],
            salobj.State.FAULT: [None, None, self.TEXT_STANDBY],
            salobj.State.OFFLINE: [None, None, None],
        }

        self._lastEnabled = None

        try:
            dbSet = True
            stateData = stateMap[data.summaryState]
            bi = 0
            for b in self.commandButtons.buttons():
                text = stateData[bi]
                if text is None:
                    b.setEnabled(False)
                    b.setDefault(False)
                else:
                    b.setText(text)
                    b.setEnabled(True)
                    b.setDefault(dbSet)
                    dbSet = False
                bi += 1

        except KeyError:
            print(f"Unhandled detailed state {data.detailedState}")

    @asyncSlot()
    async def _buttonClicked(self, bnt):
        text = bnt.text()
        self.disableAllButtons()
        try:
            if text == self.TEXT_START:
                await self.compressor.remote.cmd_start.set_start(
                    configurationOverride="Default", timeout=60
                )
            elif text == self.TEXT_EXIT_CONTROL:
                await self.compressor.remote.cmd_exitControl.start()
            elif text == self.TEXT_ENABLE:
                await self.compressor.remote.cmd_enable.start()
            elif text == self.TEXT_DISABLE:
                await self.compressor.remote.cmd_disable.start()
            elif text == self.TEXT_STANDBY:
                await self.compressor.remote.cmd_standby.start()
            else:
                raise RuntimeError(f"unassigned command for button {text}")
        except (salobj.base.AckError, salobj.base.AckTimeoutError) as ackE:
            warning(
                self,
                f"Error executing button {text}",
                f"Error executing button <i>{text}</i>:<br/>{ackE.ackcmd.result}",
            )
        except RuntimeError as rte:
            warning(
                self,
                f"Error executing {text()}",
                f"Executing button <i>{text()}</i>:<br/>{str(rte)}",
            )
        finally:
            self.restoreEnabled()
