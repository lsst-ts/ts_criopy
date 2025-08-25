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

from astropy.time import Time, TimeDelta
from PySide6.QtCore import QDateTime, QSettings, Qt, QTimerEvent, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QDateTimeEdit,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSlider,
    QSpinBox,
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


class ReplayControlWidget(QWidget):
    """
    Widget for controlling salcomm.player. Contains slider and buttons to
    replay retrieved data on EUI.

    Parameters
    ----------
    sal : MetaSAL
       SAL CSC connection.
    efd : str
       Name of the EFD to queury data.
    """

    def __init__(self, sal: MetaSAL, efd: str):
        super().__init__()
        self.sal = sal
        self.player: Player | None = None
        self.efd = efd

        self.play_interval = 0
        self.play_timer = None
        self.play_step_time = 100  # time for one play step in ms

        now = QDateTime.currentDateTime()

        self.play_time = now

        self.start = MSecDateTimeEdit(now.addSecs(-600))
        self.duration = QDoubleSpinBox()
        self.duration.setRange(1, 3600)
        self.duration.setDecimals(3)
        self.duration.setSingleStep(10)
        self.duration.setValue(60)

        retrieve_data_button = QPushButton("&Retrieve data")
        retrieve_data_button.clicked.connect(self.retrieve_data)

        start_end_layout = QHBoxLayout()
        start_end_layout.addWidget(QLabel("From"))
        start_end_layout.addWidget(self.start)
        start_end_layout.addWidget(QLabel("for"))
        start_end_layout.addWidget(self.duration)
        start_end_layout.addWidget(QLabel("s"))
        start_end_layout.addStretch()
        start_end_layout.addWidget(retrieve_data_button)

        self.slider = QSlider(Qt.Horizontal)

        self.current = MSecDateTimeEdit(self.start)
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

        layout = QVBoxLayout()

        player_layout = QHBoxLayout()
        player_layout.addWidget(backward_button)
        player_layout.addWidget(step_backward_button)
        player_layout.addWidget(pause_button)
        player_layout.addWidget(step_forward_button)
        player_layout.addWidget(play_button)
        player_layout.addWidget(forward_button)

        layout.addLayout(start_end_layout)
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
    def retrieve_data(self) -> None:
        self.slider.setMinimum(0)
        self.slider.setMaximum(self.duration.value() * 1000)
        self.slider.setValue(0)
        self.slider_moved(0)
        self.play_time = self.start.dateTime()

    @Slot()
    def slider_moved(self, value: int) -> None:
        new = self.start.dateTime().addMSecs(value)
        if new != self.current.dateTime():
            self.current.setDateTime(new)

    @Slot()
    def download_started(self) -> None:
        self.setEnabled(False)

    @Slot()
    def download_finished(self) -> None:
        self.setEnabled(True)

    @asyncSlot()
    async def replay(self, date_time: QDateTime) -> None:
        if self.player is None:
            self.player = Player(self.sal, self.efd)
            self.player.downloadStarted.connect(self.download_started)
            self.player.downloadFinished.connect(self.download_finished)

            self.sal.freeze(self.player.cache)

        timepoint = (
            date_time.toMSecsSinceEpoch() - self.start.dateTime().toMSecsSinceEpoch()
        )
        if timepoint < 0:
            date_time = self.start.dateTime()
            timepoint = 0
        elif timepoint > self.slider.maximum():
            date_time = self.start.dateTime.addMSecs(int(self.duration.value() * 1000))
            timepoint = self.slider.maximum()

        self.slider.setValue(timepoint)
        start = Time(date_time.toMSecsSinceEpoch() / 1000.0, format="unix")
        await self.player.replay(start, TimeDelta(self.duration.value(), format="sec"))


class ReplayWidget(QWidget):
    """Widget containing control for data replay and a GUI log widget.

    Parameters
    ----------
    sal : MetaSAL
        SAL CSC connection.
    """

    def __init__(self, sal: MetaSAL):
        super().__init__()
        self.setWindowTitle("Replay")
        self.app_name = "LSST.TS.REPLAY"

        layout = QVBoxLayout()
        self.setLayout(layout)

        # TODO: shall be user-selectable. OSW-927
        self.replay_control = ReplayControlWidget(sal, "usdf_efd")
        layout.addWidget(self.replay_control)

        logging_widget = LoggingWidget()
        a_ch = self.fontMetrics().averageCharWidth()
        logging_widget.setMinimumWidth(a_ch * 40)
        logging_widget.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)
        logging.getLogger().addHandler(logging_widget)

        layout.addWidget(logging_widget)

        settings = QSettings(self.app_name, "ReplayWindow")
        try:
            self.restoreGeometry(settings.value("geometry"))
        except AttributeError:
            self.resize(a_ch * 115, 600)

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings(self.app_name, "ReplayWindow")
        settings.setValue("geometry", self.saveGeometry())
