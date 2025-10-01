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

from lsst_efd_client import EfdClient
from PySide6.QtCore import QDateTime, QSettings, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ...salcomm import MetaSAL
from ..logging_widget import LoggingWidget
from .load_progress_widget import LoadProgressWidget
from .player_widget import MSecDateTimeEdit, PlayerWidget


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

    def __init__(self, sal: MetaSAL):
        super().__init__()

        self.sal = sal

        efd_layout = QHBoxLayout()

        self.select_efd = QComboBox()

        efd_names = EfdClient.list_efd_names()
        self.select_efd.clear()
        for name in sorted(efd_names):
            self.select_efd.addItem(name)

        efd_layout.addWidget(QLabel("EFD:"))
        efd_layout.addWidget(self.select_efd)
        efd_layout.addStretch()

        stop_button = QPushButton("&Stop")
        stop_button.clicked.connect(self.stop)

        retrieve_data_button = QPushButton("&Retrieve data")
        retrieve_data_button.clicked.connect(self.retrieve_data)

        now = QDateTime.currentDateTime()

        self.start = MSecDateTimeEdit(now.addSecs(-600))
        self.duration = QDoubleSpinBox()
        self.duration.setRange(1, 3600)
        self.duration.setDecimals(3)
        self.duration.setSingleStep(10)
        self.duration.setValue(60)

        start_end_layout = QHBoxLayout()
        start_end_layout.addWidget(QLabel("From"))
        start_end_layout.addWidget(self.start)
        start_end_layout.addWidget(QLabel("for"))
        start_end_layout.addWidget(self.duration)
        start_end_layout.addWidget(QLabel("s"))
        start_end_layout.addStretch()
        start_end_layout.addWidget(stop_button)
        start_end_layout.addWidget(retrieve_data_button)

        self.load_progress = LoadProgressWidget()

        self.player_widget = PlayerWidget(
            self.sal, self.start, self.duration, self.load_progress
        )
        self.player_widget.setEnabled(False)

        layout = QVBoxLayout()

        layout.addLayout(efd_layout)
        layout.addLayout(start_end_layout)
        layout.addWidget(self.player_widget)

        layout.addWidget(self.load_progress)

        self.setLayout(layout)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.player_widget.set_player(None)
        self.sal.thaw()

    @asyncSlot()
    async def retrieve_data(self) -> None:
        self.player_widget.retrieve_data(
            self.select_efd.currentText(), self.start.dateTime()
        )

    @Slot()
    def stop(self) -> None:
        self.player_widget.setEnabled(False)
        if self.player_widget.player is not None:
            self.player_widget.player.stop()


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

        self.replay_control = ReplayControlWidget(sal)
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

        self.replay_control.select_efd.setCurrentText(
            settings.value("efd_name", "usdf_efd")
        )

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings(self.app_name, "ReplayWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("efd_name", self.replay_control.select_efd.currentText())
