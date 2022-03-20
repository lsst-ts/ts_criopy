from .CustomLabels import DataLabel, OnOffLabel
from .SALComm import warning

from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QPushButton,
    QButtonGroup,
)
from PySide2.QtCore import Slot
from asyncqt import asyncSlot

from lsst.ts import salobj


class CompressorsPageWidget(QWidget):
    # Constants for button titles. Titles are used to select command send to SAL.
    TEXT_START = "&Start"
    TEXT_ENABLE = "&Enable"
    TEXT_DISABLE = "&Disable"
    TEXT_STANDBY = "&Standby"
    TEXT_EXIT_CONTROL = "&Exit Control"

    def __init__(self, compressor):
        super().__init__()
        self.compressor = compressor

        self._lastEnabled = None

        layout = QHBoxLayout()

        commandLayout = QVBoxLayout()
        dataLayout = QFormLayout()
        statusLayout = QFormLayout()

        layout.addLayout(commandLayout)
        layout.addLayout(dataLayout)
        layout.addLayout(statusLayout)
        layout.addStretch()

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

        commandLayout.addStretch()

        dataLayout.addRow(
            "Compressor Software Version",
            DataLabel(self.compressor.compressorInfo, "softwareVersion"),
        )
        dataLayout.addRow(
            "Serial Number", DataLabel(self.compressor.compressorInfo, "serialNumber")
        )

        dataLayout.addRow(
            "Water level", DataLabel(self.compressor.analogData, "waterLevel")
        )
        dataLayout.addRow(
            "Target speed", DataLabel(self.compressor.analogData, "targetSpeed")
        )
        dataLayout.addRow(
            "Motor current", DataLabel(self.compressor.analogData, "motorCurrent")
        )
        dataLayout.addRow(
            "Heatsink temperature",
            DataLabel(self.compressor.analogData, "heatsinkTemperature"),
        )
        dataLayout.addRow(
            "DC link voltage", DataLabel(self.compressor.analogData, "dclinkVoltage")
        )
        dataLayout.addRow(
            "Motor speed percentage",
            DataLabel(self.compressor.analogData, "motorSpeedPercentage"),
        )
        dataLayout.addRow(
            "Motor speed RPM", DataLabel(self.compressor.analogData, "motorSpeedRPM")
        )
        dataLayout.addRow(
            "Motor input", DataLabel(self.compressor.analogData, "motorInput")
        )
        dataLayout.addRow(
            "Power consumption",
            DataLabel(self.compressor.analogData, "compressorPowerConsumption"),
        )
        dataLayout.addRow(
            "Volume percentage",
            DataLabel(self.compressor.analogData, "compressorVolumePercentage"),
        )
        dataLayout.addRow(
            "Volume", DataLabel(self.compressor.analogData, "compressorVolume")
        )
        dataLayout.addRow(
            "Stage 1 output pressure",
            DataLabel(self.compressor.analogData, "stage1OutputPressure"),
        )
        dataLayout.addRow(
            "Line pressure", DataLabel(self.compressor.analogData, "linePressure")
        )
        dataLayout.addRow(
            "Stage 1 output temperature",
            DataLabel(self.compressor.analogData, "stage1OutputTemperature"),
        )
        dataLayout.addRow(
            "Running hours", DataLabel(self.compressor.timerInfo, "runningHours")
        )
        dataLayout.addRow(
            "Loaded hours", DataLabel(self.compressor.timerInfo, "loadedHours")
        )
        dataLayout.addRow(
            "Lowest service counter",
            DataLabel(self.compressor.timerInfo, "lowestServiceCounter"),
        )
        dataLayout.addRow(
            "Run-On timer", DataLabel(self.compressor.timerInfo, "runOnTimer")
        )
        dataLayout.addRow(
            "Loaded hours 50 percent",
            DataLabel(self.compressor.timerInfo, "loadedHours50Percent"),
        )

        statusLayout.addRow(
            "Read to start", OnOffLabel(self.compressor.status, "readyToStart")
        )
        statusLayout.addRow(
            "Operating", OnOffLabel(self.compressor.status, "operating")
        )
        statusLayout.addRow(
            "Start Inhibit", OnOffLabel(self.compressor.status, "startInhibit")
        )
        statusLayout.addRow(
            "Motor start phase", OnOffLabel(self.compressor.status, "motorStartPhase")
        )
        statusLayout.addRow("Off load", OnOffLabel(self.compressor.status, "offLoad"))
        statusLayout.addRow("On load", OnOffLabel(self.compressor.status, "onLoad"))
        statusLayout.addRow("Soft stop", OnOffLabel(self.compressor.status, "softStop"))
        statusLayout.addRow(
            "Run on timer", OnOffLabel(self.compressor.status, "runOnTimer")
        )
        statusLayout.addRow("Fault", OnOffLabel(self.compressor.status, "fault"))
        statusLayout.addRow("Warning", OnOffLabel(self.compressor.status, "warning"))
        statusLayout.addRow(
            "Service required", OnOffLabel(self.compressor.status, "serviceRequired")
        )
        statusLayout.addRow(
            "Min. allowed speed",
            OnOffLabel(self.compressor.status, "minAllowedSpeedAchieved"),
        )
        statusLayout.addRow(
            "Max. allowed speed",
            OnOffLabel(self.compressor.status, "maxAllowedSpeedAchieved"),
        )

        statusLayout.addRow(
            "Start by remote", OnOffLabel(self.compressor.status, "startByRemote")
        )
        statusLayout.addRow(
            "Start with timer control",
            OnOffLabel(self.compressor.status, "startWithTimerControl"),
        )
        statusLayout.addRow(
            "Start with pressure requirement",
            OnOffLabel(self.compressor.status, "startWithPressureRequirement"),
        )
        statusLayout.addRow(
            "Start after de-pressurise",
            OnOffLabel(self.compressor.status, "startAfterDePressurise"),
        )
        statusLayout.addRow(
            "Start after power-loss",
            OnOffLabel(self.compressor.status, "startAfterPowerLoss"),
        )
        statusLayout.addRow(
            "Start after dryer pre-run",
            OnOffLabel(self.compressor.status, "startAfterDryerPreRun"),
        )

        self.setLayout(layout)

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
        # text mean button is enabled and given text shall be displayed. None for disabled buttons.
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
            salobj.State.OFFLINE: [None, None, None, None, None],
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
