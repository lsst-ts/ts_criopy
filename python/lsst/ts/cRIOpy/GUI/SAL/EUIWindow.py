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

# You should have received a copy of the GNU General Public License along with
# this program.If not, see <https://www.gnu.org/licenses/>.

import asyncio
import enum
from functools import partial

from asyncqt import asyncClose
from PySide2.QtCore import QSettings, Slot
from PySide2.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .CSCControlWidget import CSCControlWidget


class EUIWindow(QMainWindow):
    def __init__(self, name, comms, default_size=(1000, 700)):
        super().__init__()
        self.app_name = "LSST.TS." + name
        self.comms = comms

        control_widget = QGroupBox("CSC Control")
        application_control_layout = QVBoxLayout()
        application_control_layout.addWidget(CSCControlWidget(comms[0]))
        control_widget.setLayout(application_control_layout)

        make_window = QPushButton("Open in &Window")
        make_window.clicked.connect(self.make_window)

        self.pages = {}
        self.windows = {}

        self.application_pagination = QListWidget()
        self.application_pagination.currentRowChanged.connect(self.change_page)

        left_layout = QVBoxLayout()
        left_layout.addWidget(control_widget)
        left_layout.addWidget(make_window)
        left_layout.addWidget(self.application_pagination)

        self.tab_widget = QTabWidget()
        self.tab_widget.tabBar().hide()

        layout = QHBoxLayout()
        layout.addLayout(left_layout, 0)
        layout.addWidget(self.tab_widget, 1)

        main_widget = QWidget()
        main_widget.setLayout(layout)

        self.setCentralWidget(main_widget)

        settings = QSettings(self.app_name, "MainWindow")
        self._last_tab = ""
        try:
            self.restoreGeometry(settings.value("geometry"))
            self.restoreState(settings.value("windowState"))
            self._last_tab = settings.value("currentTab")
        except AttributeError:
            self.resize(*default_size)

    def add_page(self, name: str, widget_class: QWidget, *params):
        self.pages[name] = partial(widget_class, *params)
        self.application_pagination.addItem(name)
        self.tab_widget.addTab(widget_class(*params), name)
        self.windows[name] = []

        if name == self._last_tab:
            self.application_pagination.setCurrentRow(
                self.application_pagination.count() - 1
            )

    def state_string(self, state: enum.IntEnum | int) -> str:
        """Retrieve nicely formated state description."""
        text = str(state)
        text = text[text.index(".") + 1 :]
        return text[0] + text[1:].lower().replace("_", " ")

    @Slot()
    def make_window(self, checked: bool) -> None:
        name = self.application_pagination.currentItem().text()
        widget = self.pages[name]()
        widget.setWindowTitle(f"{name}:{len(self.windows[name])+1}")
        widget.show()
        self.windows[name].append(widget)

    @Slot()
    def change_page(self, row: int) -> None:
        if row < 0:
            return
        self.tab_widget.setCurrentIndex(row)

    @asyncClose
    async def closeEvent(self, event):
        for windows in self.windows.values():
            for window in windows:
                window.close()
        settings = QSettings(self.app_name, "MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue(
            "currentTab", self.application_pagination.currentItem().text()
        )
        await asyncio.gather(*[c.close() for c in self.comms])
        super().closeEvent(event)
