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

from PySide2.QtCore import Slot
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QPlainTextEdit, QWidget, QVBoxLayout

from datetime import datetime

__all__ = ["SALErrorCodeWidget"]


class SALErrorCodeWidget(QWidget):
    """Displays errorCode messages."""

    def __init__(self, comm):
        super().__init__()

        layout = QVBoxLayout()

        self.plainText = QPlainTextEdit()
        self.plainText.setReadOnly(True)
        self.plainText.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.plainText.setCenterOnScroll(True)
        font = QFont("Monospace")
        font.setStyleHint(QFont.TypeWriter)
        self.plainText.setFont(font)

        layout.addWidget(self.plainText)
        self.setLayout(layout)

        comm.errorCode.connect(self.errorCode)

    @Slot()
    def errorCode(self, data):
        date = datetime.fromtimestamp(data.private_sndStamp).isoformat(
            sep=" ", timespec="milliseconds"
        )
        self.plainText.appendHtml(
            f"{date} [<b>{data.errorCode:06X}</b>] <span style='color:{'green' if data.errorCode==0 else 'red'}'>{data.errorReport}</span>"
        )
        self.plainText.ensureCursorVisible()
