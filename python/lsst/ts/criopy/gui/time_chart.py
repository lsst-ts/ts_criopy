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

import concurrent.futures
import time
import typing

from lsst.ts.salobj import BaseMsgType
from PySide6.QtCharts import QChart, QChartView, QDateTimeAxis, QLineSeries, QValueAxis
from PySide6.QtCore import QDateTime, QPointF, Qt, Signal, Slot
from PySide6.QtGui import QContextMenuEvent, QPainter
from PySide6.QtWidgets import QMenu

from .abstract_chart import AbstractChart
from .custom_labels import UnitLabel

__all__ = ["TimeChart", "UserSelectedTimeChart", "TimeChartView"]


class TimeChart(AbstractChart):
    """Class with time axis and value(s). Keeps last n/dt items. Holds axis
    titles and series, and handle axis auto scaling.

    Data to the graph shall be added with the append method. The class does the
    rest, creates axis/series and autoscale them as needed. Data are cached
    before being draw.

    Parameters
    ----------
    items : `{`str` : [`str`]}`
        Items stored in plot. Key is axis, items are labels.
    max_items : `int`, optional
        Number of items to keep in graph. When series grows above the specified
        number of points, oldest points are removed. Defaults to 50 * 30 = 50Hz
        * 30s.
    update_interval: `float`, optional
        Interval for chart redraws responding to append call. Defaults to 0.1
        second.
    """

    def __init__(
        self,
        items: dict[str, list[str | None]] | None,
        max_items: int = 50 * 30,
        update_interval: float = 0.1,
    ):
        super().__init__(update_interval=update_interval)
        self.timeAxis: QDateTimeAxis | None = None

        self._create_caches(items, max_items)
        self._attach_series()

    def _add_serie(self, name: str, axis: str) -> None:
        s = QLineSeries()
        s.setName(name)
        # TODO crashes (core dumps) on some systems. Need to investigate
        # s.setUseOpenGL(True)
        a = self.findAxis(axis)
        if a is None:
            a = QValueAxis()
            a.setTickCount(10)
            a.setTitleText(axis)
            self.addAxis(
                a, Qt.AlignRight if len(self.axes(Qt.Vertical)) % 2 else Qt.AlignLeft
            )
        self.addSeries(s)
        s.attachAxis(a)

    def _attach_series(self) -> None:
        # Caveat emptor, the order here is important. Hard to find, but the
        # order in which chart, axis and series are constructed and attached
        # should always be:
        # - construct Axis, Chart, Serie
        # - addAxis to chart
        # - attach series to axis
        # Changing the order will result in undetermined behaviour, most
        # likely the axis or even graph not shown. It's irrelevant when you
        # fill series with data. See QtChart::createDefaultAxes in QtChart
        # source code for details.
        self.timeAxis = QDateTimeAxis()
        self.timeAxis.setReverse(True)
        self.timeAxis.setTickCount(5)
        self.timeAxis.setFormat("h:mm:ss.zzz")
        self.timeAxis.setTitleText("Time (TAI)")
        self.timeAxis.setGridLineVisible(True)

        self.addAxis(self.timeAxis, Qt.AlignBottom)

        for serie in self.series():
            serie.attachAxis(self.timeAxis)

    def append(
        self,
        timestamp: float,
        data: list[float],
        axis_index: int = 0,
        cache_index: int | None = None,
        update: bool = False,
    ) -> None:
        """Add data to a serie. Creates axis and serie if needed. Shrink if
        more than expected elements are stored.

        Parameters
        ----------
        timestamp : `float`
            Values timestamp.
        data : `[float]`
            Axis data.
        axis_index : `int`, optional
            Axis index. Defaults to 0.
        cache_index : `int`, optional
            Cache index. Equals to axis_index if None. Defaults to None.
        update : `boolean`, optional
            If true, updates plot. Otherwise, store points for future update
            call and update plot if update_interval passed since the last
            completed update."""
        if cache_index is None:
            cache = self._caches[axis_index]
        else:
            cache = self._caches[cache_index]

        cache.append(tuple([timestamp * 1000.0] + data))

        def replot() -> None:
            if self.timeAxis is None:
                return

            axis = self.axes(Qt.Vertical)[axis_index]
            d_min = d_max = None
            for n in cache.columns()[1:]:
                serie = self.findSerie(n)
                if serie is None or serie.isVisible() is False:
                    continue

                data = cache[n]
                if d_min is None:
                    d_min = min(data)
                    d_max = max(data)
                else:
                    d_min = min(d_min, min(data))
                    d_max = max(d_max, max(data))
                points = [QPointF(*i) for i in zip(cache["timestamp"], data)]

                serie.replace(points)

            self.timeAxis.setRange(
                *[QDateTime().fromMSecsSinceEpoch(int(t)) for t in cache.time_range()]
            )
            if d_min == d_max:
                if d_min == 0 or d_min is None or d_max is None:
                    d_min = -1
                    d_max = 1
                else:
                    d_min -= d_min * 0.05
                    d_max += d_max * 0.05

            axis.setRange(d_min, d_max)

            self._next_update = time.monotonic() + self.update_interval

        # replot if needed
        if update:
            self.update_task.cancel()
            self._next_update = 0

        if (
            self._next_update < time.monotonic()
            and self.update_task.done()
            and self.isVisibleTo(None)
        ):
            with concurrent.futures.ThreadPoolExecutor() as pool:
                self.update_task = pool.submit(replot)

    def clear_data(self) -> None:
        """Removes all data from the chart."""
        super().removeAllSeries()


class UserSelectedTimeChart(TimeChart):
    """
    Parameters
    ----------
    topics : `dict[topic, signal]`
    Signals
    -------
    topicSelected : `Signal(object)`
        Send when DataUnitLabel or DataLabel is clicked. Object parameters
        denotes selected label.
    """

    topicSelected = Signal(object)

    def __init__(self, topics: dict[typing.Any, typing.Any]):
        super().__init__(None)
        self._topics = topics
        self._signal = None
        self._name: str | None = None
        self._index: int | None = None
        self.topicSelected.connect(self._topic_selected)

    @Slot()
    def _topic_selected(self, obj: UnitLabel) -> None:
        name = obj.objectName()
        index = None
        try:
            s = name.index("[")
            index = int(name[s + 1 : -1])
            name = name[:s]
        except ValueError:
            index = None

        for t, s in self._topics.items():
            for n in vars(t.DataType()):
                if n != name:
                    continue

                if self._signal is not None:
                    self._signal.disconnect(self._append_data)

                try:
                    unit_name = obj.formator.unit_name
                except AttributeError:
                    try:
                        unit_name = obj.unit_name
                    except AttributeError:
                        unit_name = "Y"

                self._create_caches({unit_name: [name]})
                self._attach_series()

                self._signal = s
                assert self._signal is not None

                self._name = name
                self._index = index

                self._signal.connect(self._append_data)
                self._next_update = 0

                break

    @Slot()
    def _append_data(self, data: BaseMsgType) -> None:
        if self._name is None:
            return

        if self._index is not None:
            self.append(data.private_sndStamp, [getattr(data, self._name)[self._index]])
        else:
            self.append(data.private_sndStamp, [getattr(data, self._name)])


class TimeChartView(QChartView):
    """Time chart view. Add handling of mouse move events.

    Parameters
    ----------
    chart : `QChart`, optional
        Chart associated with view. Defaults to None.
    """

    def __init__(self, chart: QChart | None = None):
        if chart is None:
            super().__init__()
        else:
            super().__init__(chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRubberBand(QChartView.HorizontalRubberBand)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        contextMenu = QMenu()

        for s in self.chart().series():
            action = contextMenu.addAction(s.name())
            action.setCheckable(True)
            action.setChecked(s.isVisible())

        action = contextMenu.exec_(event.globalPos())
        if action.text() is None:
            return

        for s in self.chart().series():
            if action.text() == s.name():
                s.setVisible(action.isChecked())
                return
