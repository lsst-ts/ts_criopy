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
# along with this program.If not, see < https:  // www.gnu.org/licenses/>.

import asyncio
import concurrent
import typing

from PySide6.QtCharts import QAbstractAxis, QAbstractSeries, QChart
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QGraphicsItem

from ..time_cache import TimeCache

__all__ = ["AbstractChart"]


class AbstractChart(QChart):
    """
    Chart with caching. Create caches (using _create_caches method) to build
    list of data. Update chart only as needed - as fast updates after every
    point are CPU intense (when handling M1M3 telemetry at 50 Hz).

    Parameters
    ----------
    parent : `QGraphicsItem`, optional
        Parent widget, passed to QChart constructor.
    w_flags : `Qt.WindowFlags`, optional
        Window flags. Passed to QChart contructor.
    axis_num: `int`, optional
        Number of axis in the plot.
    update_interval: `float`, optional
        Interval for chart redraws responding to append call. Defaults to 0.1.
        second.
    """

    def __init__(
        self,
        parent: QGraphicsItem = None,
        w_flags: Qt.WindowFlags = Qt.WindowFlags(),
        axis_num: int = 1,
        update_interval: float = 0.1,
    ):
        super().__init__(parent, w_flags)

        self._next_update = [0.0] * axis_num
        self.update_interval = update_interval

        self.update_task: asyncio.Future | concurrent.futures.Future = asyncio.Future()
        self.update_task.set_result(None)

    def find_axis(self, title_text: str, axis_type: Qt.Orientation = Qt.Vertical) -> QAbstractAxis | None:
        """
        Locate axis.

        Parameters
        ----------
        title_text : `str`
            Axis title.
        axis_type : `Qt.Orientation`, optional
            Axis orientation. Defaults to Qt.Vertical.

        Returns
        -------
        axis : `QAbstractAxis | None`
            Axis found, or None if the axis doesn't exists.
        """
        for a in self.axes(axis_type):
            if a.titleText() == title_text:
                return a
        return None

    def find_serie(self, name: str) -> QAbstractSeries | None:
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
        s = self.find_serie(name)
        if s is None:
            return
        self.removeSeries(s)

    def clear_data(self) -> None:
        """Removes all data from the chart."""
        self.removeAllSeries()
        for a in self.axes(Qt.Vertical):
            self.removeAxis(a)

    def _add_serie(self, name: str, axis: typing.Any) -> None:
        raise NotImplementedError("AbstractChart._add_serie should not be instantiated directly")

    def _attach_series(self) -> None:
        raise NotImplementedError("AbstractChart._attach_series should not be instantiated directly")

    def _create_caches(self, items: dict[str, list[str | None]] | None, max_items: int = 50 * 30) -> None:
        """
        Create cache for data.

        Parameters
        ----------
        items : `{str, [str | None]} | None`
            Dictionary with items in the cache. Keys are field names. Cache
            values are SAL variable's names.
        max_items : `int`, optional
            Maximal number of items. Default to 50 * 30 (30 seconds at 50 Hz).
        """
        # prevents race conditions by processing any outstanding events
        # (paint,..) before manipulating axes. Lock would work as well, but as
        # we really care just about latest diagram repaint, better cancel what
        # shall anyway not make to the screen.
        self.update_task.cancel()
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
                    self._add_serie(d, axis[0])
            self._caches.append(TimeCache(max_items, data))
