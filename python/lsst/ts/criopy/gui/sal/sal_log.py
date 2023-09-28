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

__all__ = ["LEVELS", "LogToolBar", "LogWidget", "LogDock", "Messages"]

import typing
from datetime import datetime
from html import escape

from PySide2.QtCore import QObject, Signal, Slot
from PySide2.QtGui import QFont
from PySide2.QtWidgets import (
    QComboBox,
    QDockWidget,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QStyle,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ...salcomm import MetaSAL, command_group
from ..custom_labels import DockWindow

LEVELS = ["Trace", "Debug", "Info", "Warning", "Error", "Critical"]


def _levelToIndex(level: int) -> int:
    return min(int(level / 10), 5)


class LogToolBar(QWidget):
    """Toolbar for DockWidget. Can handle messages coming from multiple CSC.

    Parameters
    ----------
    *comms : `MetaSAL`
        SAL/DDS communications to handle.
    """

    clear = Signal()
    changeLevel = Signal(int)
    setSize = Signal(int)

    def __init__(self, parent: QWidget, *comms: MetaSAL):
        super().__init__(parent)
        toolbar = QHBoxLayout()

        clearButton = QPushButton("Clear")
        clearButton.clicked.connect(self.clear.emit)

        level = QComboBox()
        level.addItems(LEVELS)
        level.currentIndexChanged.connect(self.changeLevel.emit)

        maxBlock = QSpinBox()
        maxBlock.setMaximum(1000000)
        maxBlock.setSingleStep(10)
        maxBlock.valueChanged.connect(self.setSize.emit)
        maxBlock.setValue(1000)
        maxBlock.setMinimumWidth(100)

        toolbar.addWidget(clearButton)
        toolbar.addWidget(QLabel("Level"))
        toolbar.addWidget(level)
        toolbar.addWidget(QLabel("Current"))

        def addLevelLabel(comm: MetaSAL) -> None:
            currentLevel = QLabel("---")
            toolbar.addWidget(currentLevel)
            comm.logLevel.connect(
                lambda data: currentLevel.setText(LEVELS[_levelToIndex(data.level)])
            )

        for comm in comms:
            addLevelLabel(comm)

        toolbar.addWidget(QLabel("Max lines"))
        toolbar.addWidget(maxBlock)
        toolbar.addStretch()

        if issubclass(type(parent), QDockWidget):
            floatButton = QPushButton(
                self.style().standardIcon(QStyle.SP_TitleBarNormalButton), ""
            )

            def _toggleFloating() -> None:
                parent.setFloating(not parent.isFloating())

            floatButton.clicked.connect(_toggleFloating)

            closeButton = QPushButton(
                self.style().standardIcon(QStyle.SP_TitleBarCloseButton), ""
            )
            closeButton.clicked.connect(parent.close)

            toolbar.addWidget(floatButton)
            toolbar.addWidget(closeButton)

        self.setLayout(toolbar)


class Messages(QPlainTextEdit):
    """Displays log messages.

    Parameters
    ----------
    comms : `[SALComm]` or `SALComm`
        SAL/DDS communications to handle.
    """

    LEVELS_IDS = [
        "<font color='gray'>T</font></font>",
        "<font color='darkcyan'>D</font>",
        "<font color='green'>I</font>",
        "<font color='goldenrod'>W</font>",
        "<font color='red'>E</font>",
        "<font color='purple'>C</font>",
    ]

    LEVEL_TEXT_STYLE = [
        "color:gray; font-weight:normal;",
        "color:black; font-weight:normal;",
        "font-weight:bold;",
        "font-weight:bold;",
        "font-weight:bold;",
        "color:red; font-weight:bold;",
    ]

    def __init__(self, *comms: MetaSAL):
        super().__init__()
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setCenterOnScroll(True)
        font = QFont("Monospace")
        font.setStyleHint(QFont.TypeWriter)
        self.setFont(font)

        for comm in comms:
            comm.logMessage.connect(self.logMessage)

    @Slot()
    def logMessage(self, data: typing.Any) -> None:
        date = datetime.fromtimestamp(data.private_sndStamp).isoformat(
            sep=" ", timespec="milliseconds"
        )
        level = min(int(data.level / 10), 5)
        self.appendHtml(
            f"{date} [<b>{self.LEVELS_IDS[level]}</b>]"
            f" <span style='{self.LEVEL_TEXT_STYLE[level]}'>"
            f"{escape(data.message)}"
            "</span>"
        )
        self.ensureCursorVisible()


class Object(QObject):
    """Construct and populate toolbar and messages."""

    def __init__(self, toolbar: LogToolBar, messages: Messages, *comms: MetaSAL):
        self.comms = comms
        self.messages = messages

        toolbar.clear.connect(messages.clear)
        toolbar.changeLevel.connect(self.changeLevel)
        toolbar.setSize.connect(self.setMessageSize)

    @Slot()
    def setMessageSize(self, i: int) -> None:
        self.messages.setMaximumBlockCount(i)

    @asyncSlot()
    async def changeLevel(self, index: int) -> None:
        await command_group(self, list(self.comms), "setLogLevel", level=index * 10)


class LogWidget(QWidget, Object):
    def __init__(self, *comms: MetaSAL):
        QWidget.__init__(self)

        messages = Messages(*comms)
        toolbar = LogToolBar(self, *comms)

        Object.__init__(self, toolbar, messages, *comms)

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(messages)

        self.setLayout(layout)


class LogDock(DockWindow, Object):
    """Dock with SAL messages.

    Parameters
    ----------
    *comms : `MetaSAL`
        SAL/DDS communications to handle.
    """

    def __init__(self, *comms: MetaSAL):
        super().__init__("SAL Log")

        messages = Messages(*comms)
        toolbar = LogToolBar(self, *comms)

        Object.__init__(self, toolbar, messages, *comms)

        self.setTitleBarWidget(toolbar)
        self.setWidget(messages)
