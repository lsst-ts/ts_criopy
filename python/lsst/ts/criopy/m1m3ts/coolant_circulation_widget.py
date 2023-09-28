# This file is part of M1M3 GUI.
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

import astropy.units as u
from PySide2.QtCore import Slot
from PySide2.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ..gui import (
    Ampere,
    Colors,
    DataFormWidget,
    DataLabel,
    FieldButton,
    Hz,
    Liter,
    LiterMinute,
    TopicStatusLabel,
    Volt,
)
from ..salcomm import MetaSAL, command
from .glycol_loop_temperature_widget import GlycolLoopTemperatureWidget


class CoolantPumpWidget(QWidget):
    def __init__(self, m1m3ts: MetaSAL):
        super().__init__()
        self.m1m3ts = m1m3ts

        layout = QHBoxLayout()

        cmdlayout = QVBoxLayout()

        self.powerButton = QPushButton("Power on")
        self.powerButton.clicked.connect(self._power)

        cmdlayout.addWidget(self.powerButton)

        startButton = QPushButton("Start")
        startButton.clicked.connect(self._start)

        cmdlayout.addWidget(startButton)

        stopButton = QPushButton("Stop")
        stopButton.clicked.connect(self._stop)

        cmdlayout.addWidget(stopButton)

        resetButton = QPushButton("Reset")
        resetButton.clicked.connect(self._reset)

        cmdlayout.addWidget(resetButton)

        self.frequency = QDoubleSpinBox()
        self.frequency.setRange(0, 300)
        self.frequency.setDecimals(2)
        self.frequency.setSingleStep(0.10)
        self.frequency.setSuffix(" " + str(u.Hz))

        setButton = QPushButton("Set")
        setButton.clicked.connect(self._setCoolantPumpFrequency)

        freqlayout = QHBoxLayout()

        freqlayout.addWidget(self.frequency)
        freqlayout.addWidget(setButton)

        cmdlayout.addLayout(freqlayout)

        tellayout = QVBoxLayout()
        tellayout.addWidget(
            DataFormWidget(
                m1m3ts.glycolPump,
                [
                    ("Commanded Frequency", Hz(field="commandedFrequency")),
                    ("Output Frequency", Hz(field="outputFrequency")),
                    ("Output Current", Ampere(field="outputCurrent")),
                    ("Bus Voltage", Volt(field="busVoltage", fmt="0.0f")),
                    (
                        "Output Voltage",
                        Volt(field="outputVoltage", fmt="0.01f"),
                    ),
                ],
            )
        )
        tellayout.addWidget(
            TopicStatusLabel(
                self.m1m3ts.glycolPumpStatus,
                "Glycol Pump Status",
                [
                    FieldButton(
                        "faulted", ("OK", Colors.OK), ("Faulted", Colors.ERROR)
                    ),
                    FieldButton(
                        "running",
                        ("Not running", Colors.WARNING),
                        ("Running", Colors.OK),
                    ),
                    FieldButton(
                        "accelerating",
                        ("Not accelerating", None),
                        ("Accelerating", Colors.WARNING),
                    ),
                    FieldButton(
                        "decelerating",
                        ("Not decelerating", None),
                        ("Decelerating", Colors.WARNING),
                    ),
                    FieldButton(
                        "forwardCommanded",
                        ("Not Forward Commanded", None),
                        ("Forward Commanded", None),
                    ),
                    FieldButton(
                        "forwardRotating",
                        ("Not rotating forward", None),
                        ("Rotating forward", Colors.OK),
                    ),
                    FieldButton(
                        "ready",
                        ("Not ready", Colors.ERROR),
                        ("Ready", Colors.OK),
                    ),
                    FieldButton(
                        "mainFrequencyControlled",
                        ("Main frequency not controlled", None),
                        ("Main frequency controlled", None),
                    ),
                    FieldButton(
                        "operationCommandControlled",
                        ("Operation command not controlled", None),
                        ("Operating command controlled", None),
                    ),
                    FieldButton(
                        "parametersLocked",
                        ("Parameters not locked", Colors.OK),
                        ("Parameters locked", Colors.WARNING),
                    ),
                ],
            )
        )

        layout.addLayout(cmdlayout)
        layout.addLayout(tellayout)

        layout.addStretch()

        self.setLayout(layout)

        self.m1m3ts.engineeringMode.connect(self.engineeringMode)

    @Slot()
    def engineeringMode(self, data: typing.Any) -> None:
        """Called when engineeringMode event is received. Intercept to
        enable/disable form buttons."""
        if data.engineeringMode:
            self.setEnabled(True)
        else:
            self.setEnabled(False)

    @asyncSlot()
    async def _power(self) -> None:
        if self.powerButton.text() == "Power on":
            await command(self, self.m1m3ts.remote.cmd_coolantPumpPower, power=True)
            self.powerButton.setText("Power off")
        else:
            await command(self, self.m1m3ts.remote.cmd_coolantPumpPower, power=False)
            self.powerButton.setText("Power on")

    @asyncSlot()
    async def _start(self) -> None:
        await command(self, self.m1m3ts.remote.cmd_coolantPumpStart)

    @asyncSlot()
    async def _stop(self) -> None:
        await command(self, self.m1m3ts.remote.cmd_coolantPumpStop)

    @asyncSlot()
    async def _reset(self) -> None:
        await command(self, self.m1m3ts.remote.cmd_coolantPumpReset)

    @asyncSlot()
    async def _setCoolantPumpFrequency(self) -> None:
        await command(
            self,
            self.m1m3ts.remote.cmd_coolantPumpFrequency,
            targetFrequency=self.frequency.value(),
        )


class FlowMeterWidget(QWidget):
    def __init__(self, m1m3ts: MetaSAL):
        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(
            DataFormWidget(
                m1m3ts.flowMeter,
                [
                    ("Signal Strength", DataLabel(field="signalStrength")),
                    ("Flow Rate", LiterMinute(field="flowRate")),
                    ("Net Total", Liter(field="netTotalizer")),
                    ("Positive Total", Liter(field="positiveTotalizer")),
                    ("Negative Total", Liter(field="negativeTotalizer")),
                ],
            )
        )

        self.setLayout(layout)


class CoolantCirculationWidget(QWidget):
    """Display Glycol coolant re-circulation pump telemetry, allows motor
    commanding."""

    def __init__(self, m1m3ts: MetaSAL):
        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(CoolantPumpWidget(m1m3ts))
        layout.addWidget(FlowMeterWidget(m1m3ts))
        layout.addWidget(GlycolLoopTemperatureWidget(m1m3ts))

        layout.addStretch()

        self.setLayout(layout)
