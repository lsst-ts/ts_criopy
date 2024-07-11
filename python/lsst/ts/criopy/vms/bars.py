# This file is part of cRIO/VMS GUI.
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

# You should have received a copy of the GNU General Public License along with
# this program.If not, see <https://www.gnu.org/licenses/>.

__all__ = ["ToolBar", "StatusBar"]

from datetime import datetime

import astropy.units as u
from PySide6.QtCore import QSettings, Signal, Slot
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QLabel,
    QSpinBox,
    QStatusBar,
    QStyle,
    QToolBar,
)


class ToolBar(QToolBar):
    """Toolbar for VMS. Provides widget to setup frequency range and window
    width.
    """

    frequencyChanged = Signal(float, float)
    intervalChanged = Signal(float)
    integralBinningChanged = Signal(int)

    def __init__(self) -> None:
        super().__init__()

        settings = QSettings("LSST.TS", "VMSGUI")

        self.setObjectName("VMSToolBar")

        self.addAction(self.style().standardIcon(QStyle.SP_MediaStop), "Stop")

        self.addWidget(QLabel("Frequency"))

        self.minFreq = QDoubleSpinBox()
        self.minFreq.setDecimals(1)
        self.minFreq.setRange(0, 10000)
        self.minFreq.setSingleStep(5)
        self.minFreq.setSuffix(" Hz")
        self.minFreq.setValue(float(str(settings.value("minFreq", 0))))
        self.minFreq.editingFinished.connect(self.minMaxChanged)
        self.addWidget(self.minFreq)

        self.addWidget(QLabel("-"))

        self.maxFreq = QDoubleSpinBox()
        self.maxFreq.setDecimals(1)
        self.maxFreq.setRange(0.1, 10000)
        self.maxFreq.setSingleStep(5)
        self.maxFreq.setSuffix(" Hz")
        self.maxFreq.setValue(float(str(settings.value("maxFreq", 200))))
        self.maxFreq.editingFinished.connect(self.minMaxChanged)
        self.addWidget(self.maxFreq)

        self.addWidget(QLabel("Interval:"))

        self.interval = QDoubleSpinBox()
        self.interval.setDecimals(3)
        self.interval.setRange(0.01, 3600)
        self.interval.setSingleStep(0.1)
        self.interval.setSuffix(" s")
        self.interval.setValue(float(str(settings.value("interval", 50.0))))
        self.interval.editingFinished.connect(self.newInterval)
        self.addWidget(self.interval)

        self.addWidget(QLabel("Integral binning"))

        self.integralBinning = QSpinBox()
        self.integralBinning.setRange(2, 10000)
        self.integralBinning.setSingleStep(10)
        self.integralBinning.setValue(int(str(settings.value("integralBinning", 10))))
        self.integralBinning.editingFinished.connect(self.newIntegralBinning)
        self.addWidget(self.integralBinning)

        self.frequencyChanged.emit(self.minFreq.value(), self.maxFreq.value())

    def storeSettings(self) -> None:
        """Store settings through QSettings."""
        settings = QSettings("LSST.TS", "VMSGUI")
        settings.setValue("minFreq", self.minFreq.value())
        settings.setValue("maxFreq", self.maxFreq.value())
        settings.setValue("interval", self.interval.value())
        settings.setValue("integralBinning", self.integralBinning.value())

    @Slot()
    def minMaxChanged(self) -> None:
        self.frequencyChanged.emit(*self.getFrequencyRange())

    @Slot()
    def newInterval(self) -> None:
        self.intervalChanged.emit(self.interval.value())

    @Slot()
    def newIntegralBinning(self) -> None:
        self.integralBinningChanged.emit(self.integralBinning.value())

    def getFrequencyRange(self) -> tuple[float, float]:
        return (self.minFreq.value(), self.maxFreq.value())

    def getIntegralBinning(self) -> int:
        return self.integralBinning.value()


class StatusBar(QStatusBar):
    """Displays cache status on status bar."""

    def __init__(self, systems: list[str]) -> None:
        super().__init__()
        self.sampleTimes = [None] * len(systems)
        self.cacheStatus = []
        for system in systems:
            self.addWidget(QLabel(system))
            label = QLabel("Size: 0 --- - ---")
            self.cacheStatus.append(label)
            self.addWidget(label)

    @Slot()
    def cacheUpdated(self, index: int, length: int, start: float, end: float) -> None:
        """Emitted when cache is updated.

        Parameters
        ----------
        index : `int`
            VMS index (1 - M1M3, 2 - M2, 3 - CameraRotator)
        length : `int`
            Number of points cached.
        start : `float`
            Start timestamp.
        end : `float`
            End timestamp.
        """
        if self.sampleTimes[index] is None:
            self.cacheStatus[index].setText("No data")
        else:
            self.cacheStatus[index].setText(
                f"Size: {length}"
                f" {datetime.fromtimestamp(start).strftime('%H:%M:%S.%f')} -"
                f" {datetime.fromtimestamp(end).strftime('%H:%M:%S.%f')}"
                f" {end-start+self.sampleTimes[index]*u.ms.to(u.s):.03f}s"
            )
