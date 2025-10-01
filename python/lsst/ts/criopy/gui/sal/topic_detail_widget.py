# This file is part of TS cRIOpy.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from lsst.ts.salobj import BaseMsgType
from PySide6.QtWidgets import QWidget


class TopicDetailWidget(QWidget):
    """
    Provides details about currently selected actuator. Abstract class, shall
    be subclassed and data_changed method implemented.
    """

    def __init__(self) -> None:
        super().__init__()

    def data_changed(self, data: BaseMsgType | None) -> None:
        """
        Called when new data are available.

        Parameters
        ----------
        data : `BaseMsgType`
            New data. Either received from SAL, or retrived from some cache.
        """
        raise NotImplementedError(
            "data_changed method needs to be overriden in TopicDetailWidget subclass."
        )
