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
import typing

from asyncqt import asyncClose
from PySide2.QtCore import QSettings, Slot
from PySide2.QtGui import QCloseEvent
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
from .SALComm import MetaSAL


class EUIWindow(QMainWindow):
    """Construct primary EUI window.

    The window provides CSC state control and displays pages showing various CSC
    views and controls. The EUIWindow class saves and restore various settings,
    including window geometry and the last viewed page.

    A button is provided to show any page a separate window.

    Parameters
    ----------
    name : `str`
        EUI name. Primary used to store current window settings.
    comms : `[MetaSAL]`
        MetaSAL communication objects. They will be proplerly closed as the
        window closes.
    default_size : `(int, int)`
        EUI window default size. Note that the size is among parameters stored
        in EUI configuration, and restored when the window is initialized.
    csc_control_widget : `QWidget`, optional
        CSC control widget. Defaults to CSCControlWidget class. It's
        recommended (but not enforced) this parameter is subclass of CSCControlWidget.
    """

    def __init__(
        self,
        name: str,
        comms: list[MetaSAL],
        default_size: tuple[int, int] = (1000, 700),
        csc_control_widget: QWidget | None = None,
    ):
        super().__init__()
        self.app_name = "LSST.TS." + name
        self.comms = comms

        if csc_control_widget is None:
            csc_control_widget = CSCControlWidget(comms[0])
        self.csc_control_widget = csc_control_widget

        control_widget = QGroupBox("CSC Control")
        control_widget.setLayout(self.csc_control_widget.layout())

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

    def add_page(
        self, name: str, widget_class: QWidget, *params: list[typing.Any]
    ) -> None:
        """Add page to available pages.

        Parameters
        ----------
        name : `str`
            Page name. This is shown in pagination list and in title of any
            windows created from the page.
        widget_class : `QWidget`
            Page class. When created, *params are passed to its constructor.
        *params : `[Any]`
            Parameters passed to widget_class constructor.

        Note
        ----
        A class and constructor parameters are passed, as the application
        creates new object when new window is requested. This works much better
        than any (deep) copying.
        """

        self.pages[name] = partial(widget_class, *params)
        self.application_pagination.addItem(name)
        self.tab_widget.addTab(widget_class(*params), name)
        self.windows[name] = []

        if self._last_tab == "" and self.application_pagination.count() == 1:
            self.application_pagination.setCurrentRow(0)
        elif name == self._last_tab:
            self.application_pagination.setCurrentRow(
                self.application_pagination.count() - 1
            )

    def state_string(self, state: enum.IntEnum) -> str:
        """Retrieve nicely formatted state description.

        Parameters
        ----------
        state : `enum.intEnum`
            Current CSC state enumeration.

        Returns
        -------
        state_str : `str`
            String description of the state, constructed from the enumeration
            string value.
        """
        text = str(state)
        text = text[text.index(".") + 1 :]
        return text[0] + text[1:].lower().replace("_", " ")

    @Slot()
    def make_window(self, checked: bool) -> None:
        """Create new window with copy of currently selected tab."""
        name = self.application_pagination.currentItem().text()
        widget = self.pages[name]()
        widget.setWindowTitle(f"{name}:{len(self.windows[name])+1}")
        widget.show()
        self.windows[name].append(widget)

    @Slot()
    def change_page(self, row: int) -> None:
        """Called when currently selected item in the pagination list changes."""
        if row < 0:
            return
        self.tab_widget.setCurrentIndex(row)

    @asyncClose
    async def closeEvent(self, event: QCloseEvent) -> None:
        """Called as the window is being closed.

        Makes sure all managed MetaSAL/SAL proxies are close. Also closes any
        subwindows.
        """
        for windows in self.windows.values():
            for window in windows:
                window.close()
        settings = QSettings(self.app_name, "MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())

        current_item = self.application_pagination.currentItem()
        if current_item is not None:
            settings.setValue("currentTab", current_item.text())

        await asyncio.gather(*[c.close() for c in self.comms])
        super().closeEvent(event)
