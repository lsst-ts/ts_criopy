# This file is part of criopy package.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https: //www.lsst.org).
# See the COPYRIGHT file at the top - level directory of this distribution
# for details of code ownership.
#
# This program is free software : you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.If not, see <https://www.gnu.org/licenses/>.

__all__ = ["ReplayWidget"]

import logging

from astropy.time import Time
from lsst_efd_client import EfdClient
from PySide6.QtCore import QDateTime, Qt, Slot
from PySide6.QtWidgets import (
    QDateTimeEdit,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QStyle,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ...salcomm import MetaSAL, Player
from ..logging_widget import LoggingWidget


class MSecDateTimeEdit(QDateTimeEdit):
    def __init__(self, date_time: QDateTime):
        super().__init__(date_time)
        self.setDisplayFormat(self.displayFormat() + ".zzz")


class ReplayWidget(QWidget):
    """Widget controlling data replay."""

    def __init__(self, sal: MetaSAL):
        super().__init__()
        self.sal = sal
        self.player: Player | None = None

        self.setWindowTitle("Replay")

        now = QDateTime.currentDateTime()

        self.start = MSecDateTimeEdit(now.addSecs(-10))
        self.end = MSecDateTimeEdit(now)

        layout = QVBoxLayout()
        self.setLayout(layout)

        start_end_layout = QHBoxLayout()
        start_end_layout.addWidget(self.start)
        start_end_layout.addWidget(QLabel("-"))
        start_end_layout.addWidget(self.end)

        self.slider = QSlider(Qt.Horizontal)

        logging_widget = LoggingWidget()

        logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)
        logging.getLogger().addHandler(logging_widget)

        self.current = MSecDateTimeEdit(self.start)
        self.current.dateTimeChanged.connect(self.replay)

        current_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("Current time"))
        current_layout.addWidget(self.current)

        self.backward_button = QPushButton(
            self.style().standardIcon(QStyle.SP_MediaSeekBackward), "Backward"
        )
        self.pause_button = QPushButton(
            self.style().standardIcon(QStyle.SP_MediaPause), "Pause"
        )
        self.play_button = QPushButton(
            self.style().standardIcon(QStyle.SP_MediaPlay), "Play"
        )
        self.forward_button = QPushButton(
            self.style().standardIcon(QStyle.SP_MediaSeekForward), "Forward"
        )

        player_layout = QHBoxLayout()
        player_layout.addWidget(self.backward_button)
        player_layout.addWidget(self.pause_button)
        player_layout.addWidget(self.play_button)
        player_layout.addWidget(self.forward_button)

        layout.addLayout(start_end_layout)
        layout.addWidget(logging_widget)
        layout.addWidget(self.slider)
        layout.addLayout(current_layout)
        layout.addLayout(player_layout)

        self.backward_button.clicked.connect(self.backward)
        self.pause_button.clicked.connect(self.pause)
        self.play_button.clicked.connect(self.play)
        self.forward_button.clicked.connect(self.forward)

        self.slider.valueChanged.connect(self.slider_value_changed)

        self.update_slider_range()

    @Slot()
    def backward(self, checked: bool) -> None:
        pass

    @Slot()
    def pause(self, checked: bool) -> None:
        pass

    @Slot()
    def play(self, checked: bool) -> None:
        pass

    @Slot()
    def forward(self, checked: bool) -> None:
        pass

    @Slot()
    def update_slider_range(self) -> None:
        self.slider.setMinimum(0)
        self.slider.setMaximum(
            self.end.dateTime().toMSecsSinceEpoch()
            - self.start.dateTime().toMSecsSinceEpoch()
        )
        self.slider.setValue(0)
        self.slider_value_changed(0)

    @Slot()
    def slider_value_changed(self, value: int) -> None:
        self.current.setDateTime(self.start.dateTime().addMSecs(value))

    @asyncSlot()
    async def replay(self, date_time: QDateTime) -> None:
        if self.player is None:
            self.player = Player(self.sal, EfdClient("usdf_efd"))
        await self.player.replay(
            Time(date_time.toMSecsSinceEpoch() / 1000.0, format="unix")
        )
