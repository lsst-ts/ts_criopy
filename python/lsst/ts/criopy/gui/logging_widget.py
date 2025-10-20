# This file is part of criopy package.
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

__all__ = ["LoggingWidget"]

from html import escape
from logging import Handler, LogRecord

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget


class LoggingWidget(QWidget, Handler):
    """Class to display system log messages."""

    def __init__(self) -> None:
        QWidget.__init__(self)
        Handler.__init__(self)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.messages = QPlainTextEdit()
        font = QFont("Monospace")
        font.setStyleHint(QFont.TypeWriter)
        self.messages.setFont(font)

        layout.addWidget(self.messages)

    def emit(self, record: LogRecord) -> None:
        self.messages.appendHtml(f"<span>{record.asctime} {record.levelname} {escape(record.message)}</span>")
