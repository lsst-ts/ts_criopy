# This file is part of cRIOpy package.
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
# along with this program.If not, see < https:  // www.gnu.org/licenses/>.

import asyncio
import concurrent
import typing

from PySide2.QtCharts import QtCharts
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QGraphicsItem

from .. import TimeCache

__all__ = ["AbstractChart"]


class AbstractChart(QtCharts.QChart):
    """
    Parameters
    ----------
    update_interval: `float`, optional
        Interval for chart redraws responding to append call. Defaults to 0.1
        second.
    """

    def __init__(
        self,
        parent: QGraphicsItem = None,
        wFlags: Qt.WindowFlags = Qt.WindowFlags(),
        update_interval: float = 0.1,
    ):
        super().__init__(parent, wFlags)

        self._next_update: float = 0.0
        self.update_interval = update_interval

        self.updateTask: asyncio.Future | concurrent.futures.Future = asyncio.Future()
        self.updateTask.set_result(None)

    def findAxis(
        self, titleText: str, axisType: Qt.Orientation = Qt.Vertical
    ) -> QtCharts.QAbstractAxis | None:
        for a in self.axes(axisType):
            if a.titleText() == titleText:
                return a
        return None

    def findSerie(self, name: str) -> QtCharts.QAbstractSeries | None:
        """
        Returns series with given name.

        Parameters
        ----------
        name : `str`
            Serie name.

        Returns
        -------
        serie : `QAbstractSeries`
            Series with given name. None if no series exists.

        Raises
        ------
        KeyError
            When serie cannot be found.
        """
        for s in self.series():
            if s.name() == name:
                return s
        return None

    def remove(self, name: str) -> None:
        """Removes series with given name."""
        s = self.findSerie(name)
        if s is None:
            return
        self.removeSeries(s)

    def clearData(self) -> None:
        """Removes all data from the chart."""
        self.removeAllSeries()
        for a in self.axes(Qt.Vertical):
            self.removeAxis(a)

    def _addSerie(self, name: str, axis: typing.Any) -> None:
        raise NotImplementedError(
            "AbstractChart._addSeries should not be instantiated directly"
        )

    def _attachSeries(self) -> None:
        raise NotImplementedError(
            "AbstractChart._attachSeries should not be instantiated directly"
        )

    def _createCaches(
        self, items: dict[str, list[str | None]] | None, max_items: int = 50 * 30
    ) -> None:
        # prevents race conditions by processing any outstanding events
        # (paint,..) before manipulating axes. Lock would work as well, but as
        # we really care just about latest diagram repaint, better cancel what
        # shall anyway not make it to screen.
        self.updateTask.cancel()
        QApplication.instance().processEvents()

        for a in self.axes():
            self.removeAxis(a)

        self.removeAllSeries()
        self._caches = []
        if items is None:
            return

        for axis in items.items():
            data = [("timestamp", "f8")]
            for d in axis[1]:
                if d is None:
                    self._caches.append(TimeCache(max_items, data))
                    data = [("timestamp", "f8")]
                else:
                    data.append((d, "f8"))
                    self._addSerie(d, axis[0])
            self._caches.append(TimeCache(max_items, data))
