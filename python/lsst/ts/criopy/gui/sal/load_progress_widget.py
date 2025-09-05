# This file is part of M1M3 SS GUI.
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

__all__ = ["LoadProgressWidget"]

import time

from lsst.ts.criopy.salcomm import EfdCacheRequest
from PySide6.QtCore import QTimerEvent, Slot
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QHBoxLayout, QTreeView, QWidget

from ...salcomm import Player


class LoadProgressModel(QStandardItemModel):
    """
    Model for QTreeView showing loading progress.
    """

    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels(
            ["Worker", "CSC", "Topic", "Start", "Elapsed time"]
        )

    @Slot()
    def request_started(self, request: EfdCacheRequest, worker: int) -> None:
        """
        Called when request processing stars - on requestStarted signal.

        Parameters
        ----------
        request : `EfdCacheRequest`
            Request started.
        worker : `int`
            Worker ID running the request.
        """
        now = time.monotonic()

        row = [
            QStandardItem(s)
            for s in [
                str(worker),
                request.csc_name,
                request.topic,
                time.strftime("%D %T"),
                "---",
            ]
        ]

        row[2].setData(request)
        row[3].setData(now)

        self.appendRow(row)

    def find_request(self, request: EfdCacheRequest, worker: int) -> int | None:
        """
        Find request and worker combination in list of running requests.

        Parameters
        ----------
        request : `EfdCacheRequest`
            Request to seach for.
        worker : `int`
            Worker ID running the request.

        Returns
        -------
        row : `int | None`
            Row number of the request/worker combination.
        """
        items = self.findItems(str(worker), column=0)
        if len(items) == 0:
            return None
        if len(items) == 1:
            return items[0].index().row()

        for i in items:
            row = i.index().row()
            item_request = self.item(row, 2).data()
            if item_request == request:
                return row

        return None

    def update_times(self) -> None:
        """
        Updates requests elapsed time (column 3).
        """
        now = time.monotonic()

        for r in range(self.rowCount()):
            self.item(r, 4).setText(f"{(now - self.item(r, 3).data()):.2f} s")

    @Slot()
    def request_terminated(self, request: EfdCacheRequest, worker: int) -> None:
        """
        Called when request processing terminates - on requestTerminated
        signal.

        Parameters
        ----------
        request : `EfdCacheRequest`
            Request being terminated.
        worker : `int`
            Worker ID running the request.
        """
        row = self.find_request(request, worker)
        if row is not None:
            self.removeRows(row, 1)

    @Slot()
    def request_finished(self, request: EfdCacheRequest, worker: int) -> None:
        """
        Called when request processing finshes - on requestFinished signal.

        Parameters
        ----------
        request : `EfdCacheRequest`
            Request just finished.
        worker : `int`
            Worker ID running the request.
        """

        row = self.find_request(request, worker)
        assert row is not None
        self.removeRows(row, 1)


class LoadProgressWidget(QWidget):
    """
    Widget showing request being executed. Contains QTreeView with requests
    being executed.
    """

    def __init__(self):
        super().__init__()

        self.in_progress = QTreeView()
        self.in_progress.setModel(LoadProgressModel())

        self.in_progress.setSortingEnabled(True)

        for col, width in enumerate([50, 100, 200, 125, 50]):
            self.in_progress.setColumnWidth(col, width)

        layout = QHBoxLayout()
        layout.addWidget(self.in_progress)

        self.setLayout(layout)

        self.startTimer(100)

    def timerEvent(self, event: QTimerEvent) -> None:
        """
        Called to update requests elapsed times.
        """
        self.in_progress.model().update_times()

    def connect_player(self, player: Player) -> None:
        """
        Called to connect progress widget to new Player.

        Parameters
        ----------
        player : `Player`
            New Player responsible for request playbacks.
        """
        model = self.in_progress.model()

        player.requestStarted.connect(model.request_started)
        player.requestTerminated.connect(model.request_terminated)
        player.requestFinished.connect(model.request_finished)

    def clear(self) -> None:
        """
        Remove all requests from the list.
        """
        self.in_progress.setModel(LoadProgressModel())
