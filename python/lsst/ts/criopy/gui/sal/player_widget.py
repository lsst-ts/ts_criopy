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

__all__ = ["PlayerWidget"]

from astropy.time import Time, TimeDelta
from PySide6.QtCore import QDateTime, Qt, QTimerEvent, Slot
from PySide6.QtWidgets import (
    QDateTimeEdit,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QStyle,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ...salcomm import MetaSAL, Player
from .load_progress_widget import LoadProgressWidget


class MSecDateTimeEdit(QDateTimeEdit):
    def __init__(self, date_time: QDateTime | None):
        super().__init__(date_time)
        self.setDisplayFormat(self.displayFormat() + ".zzz")


class PlayerWidget(QWidget):
    """
    Widget for interactive player control.

    Parameters
    ----------
    sal : `MetaSAL`
        SAL CSC connection.
    """

    def __init__(
        self,
        sal: MetaSAL,
        start: MSecDateTimeEdit,
        duration: QDoubleSpinBox,
        load_progress: LoadProgressWidget,
    ):
        super().__init__()
        self.sal = sal
        self.start = start
        self.duration = duration
        self.load_progress = load_progress

        self.efd_name: str | None = None

        self.player: Player | None = None

        self.play_interval = 0
        self.play_timer = None
        self.play_step_time = 100  # time for one play step in ms

        self.play_time = self.start.dateTime()

        self.slider = QSlider(Qt.Horizontal)

        self.current = MSecDateTimeEdit(None)
        self.current.dateTimeChanged.connect(self.replay)

        self.step_size_box = QSpinBox()
        self.step_size_box.setRange(1, 500)
        self.step_size_box.setSuffix(" ms")
        self.step_size_box.setSingleStep(10)
        self.step_size_box.setValue(20)

        play_speed_box = QSpinBox()
        play_speed_box.setRange(1, 100)
        play_speed_box.setSuffix("%")
        play_speed_box.setSingleStep(5)
        play_speed_box.setValue(50)

        play_speed_box.valueChanged.connect(self.change_play_speed)

        current_layout = QHBoxLayout()
        current_layout.addWidget(QLabel("Current time"))
        current_layout.addWidget(self.current)
        current_layout.addStretch()
        current_layout.addWidget(QLabel("Step size"))
        current_layout.addWidget(self.step_size_box)
        current_layout.addWidget(QLabel("Play speed"))
        current_layout.addWidget(play_speed_box)

        play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)

        backward_button = QPushButton(
            self.style().standardIcon(QStyle.SP_MediaSeekBackward), "Backward"
        )
        step_backward_button = QPushButton(play_icon, "Step Backward")
        pause_button = QPushButton(
            self.style().standardIcon(QStyle.SP_MediaPause), "Pause"
        )
        step_forward_button = QPushButton(play_icon, "Step Forward")
        play_button = QPushButton(play_icon, "Play")
        forward_button = QPushButton(
            self.style().standardIcon(QStyle.SP_MediaSeekForward), "Forward"
        )

        player_layout = QHBoxLayout()
        player_layout.addWidget(backward_button)
        player_layout.addWidget(step_backward_button)
        player_layout.addWidget(pause_button)
        player_layout.addWidget(step_forward_button)
        player_layout.addWidget(play_button)
        player_layout.addWidget(forward_button)

        layout = QVBoxLayout()
        layout.addWidget(self.slider)
        layout.addLayout(current_layout)
        layout.addLayout(player_layout)

        self.setLayout(layout)

        backward_button.clicked.connect(self.backward)
        step_backward_button.clicked.connect(self.step_backward)
        pause_button.clicked.connect(self.pause)
        step_forward_button.clicked.connect(self.step_forward)
        play_button.clicked.connect(self.play)
        forward_button.clicked.connect(self.forward)

        self.slider.sliderMoved.connect(self.slider_moved)

    def timerEvent(self, event: QTimerEvent) -> None:
        self.play_time = self.play_time.addMSecs(self.play_interval)
        start = self.start.dateTime()
        if start <= self.play_time <= start.addMSecs(int(self.duration.value() * 1000)):
            self.current.setDateTime(self.play_time)
        else:
            self.killTimer(self.play_timer)
            self.play_timer = None
            self.play_time = self.start.dateTime()

    def __change_timer(self, new_interval: int) -> None:
        if self.play_timer is not None:
            self.killTimer(self.play_timer)
        self.play_interval = new_interval
        self.play_time = self.current.dateTime()
        self.play_timer = self.startTimer(self.play_step_time)

    def retrieve_data(self, efd_name: str, timepoint: QDateTime) -> None:
        self.efd_name = efd_name
        self.play_time = timepoint
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.duration.value() * 1000)
        self.slider.setValue(0)
        self.slider_moved(0)

    @Slot()
    def slider_moved(self, value: int) -> None:
        new = self.start.dateTime().addMSecs(value)
        if new != self.current.dateTime():
            self.current.setDateTime(new)

    @Slot()
    def change_play_speed(self, value: int) -> None:
        self.play_step_time = int(20 / (float(value) / 100.0))
        if self.play_timer is not None:
            self.killTimer(self.play_timer)
        self.play_timer = self.startTimer(self.play_step_time)

    @Slot()
    def backward(self, checked: bool) -> None:
        self.__change_timer(-500)

    @Slot()
    def step_backward(self, checked: bool) -> None:
        next_time = self.current.dateTime().addMSecs(-self.step_size_box.value())
        start = self.start.dateTime()
        if start <= next_time <= start.addMSecs(int(self.duration.value() * 1000)):
            self.current.setDateTime(next_time)

    @Slot()
    def pause(self, checked: bool) -> None:
        if self.play_timer is not None:
            self.killTimer(self.play_timer)
            self.play_timer = None

    @Slot()
    def step_forward(self, checked: bool) -> None:
        next_time = self.current.dateTime().addMSecs(self.step_size_box.value())
        start = self.start.dateTime()
        if start <= next_time <= start.addMSecs(int(self.duration.value() * 1000)):
            self.current.setDateTime(next_time)

    @Slot()
    def play(self, checked: bool) -> None:
        self.__change_timer(10)

    @Slot()
    def forward(self, checked: bool) -> None:
        self.__change_timer(500)

    @Slot()
    def download_started(self) -> None:
        self.setEnabled(False)

    @Slot()
    def download_finished(self) -> None:
        assert self.player is not None
        self.sal.freeze(self.player.cache)
        self.setEnabled(True)

    @asyncSlot()
    async def replay(self, date_time: QDateTime) -> None:
        if self.player is None:
            self.player = Player(self.sal)
            self.player.downloadStarted.connect(self.download_started)
            self.player.downloadFinished.connect(self.download_finished)

            self.load_progress.connect_player(self.player)

        timepoint = (
            date_time.toMSecsSinceEpoch() - self.start.dateTime().toMSecsSinceEpoch()
        )
        if timepoint < 0:
            date_time = self.start.dateTime()
            timepoint = 0
        elif timepoint > self.slider.maximum():
            date_time = self.start.dateTime().addMSecs(
                int(self.duration.value() * 1000)
            )
            timepoint = self.slider.maximum()

        self.slider.setValue(timepoint)
        start = Time(date_time.toMSecsSinceEpoch() / 1000.0, format="unix")

        assert self.player is not None
        assert self.efd_name is not None
        await self.player.replay(
            self.efd_name,
            start,
            TimeDelta(self.duration.value(), format="sec"),
        )
