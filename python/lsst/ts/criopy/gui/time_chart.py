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
from PySide6.QtGui import QContextMenuEvent, QPainter, QWheelEvent
from PySide6.QtWidgets import QMenu

from ..time_cache import TimeCache
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
        super().__init__(axis_num=1 if items is None else len(items), update_interval=update_interval)
        self.time_axis: QDateTimeAxis | None = None

        self._create_caches(items, max_items)
        self._attach_series()

    def _add_serie(self, name: str, axis: str) -> None:
        s = QLineSeries()
        s.setName(name)
        # TODO crashes (core dumps) on some systems. Need to investigate
        # s.setUseOpenGL(True)
        a = self.find_axis(axis)
        if a is None:
            a = QValueAxis()
            a.setTickCount(10)
            a.setTitleText(axis)
            self.addAxis(a, Qt.AlignRight if len(self.axes(Qt.Vertical)) % 2 else Qt.AlignLeft)
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
        self.time_axis = QDateTimeAxis()
        self.time_axis.setReverse(False)
        self.time_axis.setTickCount(5)
        self.time_axis.setFormat("h:mm:ss.zzz")
        self.time_axis.setTitleText("Time (TAI)")
        self.time_axis.setGridLineVisible(True)

        self.addAxis(self.time_axis, Qt.AlignBottom)

        for serie in self.series():
            serie.attachAxis(self.time_axis)

    def append(
        self,
        timestamp: float,
        data: list[float],
        axis_index: int = 0,
        cache_index: int | None = None,
        update: bool = False,
    ) -> None:
        """Add data to a serie. Creates axis and serie if needed. Shrink if
        more than expected elements are stored. Redraw plot data if needed or
        requested.

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
            cache_index = axis_index

        cache = self._caches[cache_index]

        cache.append(tuple([timestamp * 1000.0] + data))

        # replot if needed
        if update:
            self.update_task.cancel()
            self._next_update = [0] * len(self._caches)

        if (
            self._next_update[cache_index] < time.monotonic()
            and self.update_task.done()
            and self.isVisibleTo(None)
        ):
            with concurrent.futures.ThreadPoolExecutor() as pool:
                self.update_task = pool.submit(self._replot, axis_index, cache)

            self._next_update[cache_index] = time.monotonic() + self.update_interval

    def replace(self, caches: list[TimeCache]) -> None:
        self._caches = caches
        self.resync()

    def resync(self) -> None:
        """Reload data from cache and plot those. This is usefull when data in
        externally supplied TimeCaches are update outside of the graph - this
        then replot data based on the current cache content.
        """

        def update_all() -> None:
            try:
                for index, cache in enumerate(self._caches):
                    self._replot(0, cache)
            except Exception as ex:
                print("Exception updating", str(ex), index, str(cache))

        self.update_task.cancel()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            self.update_task = pool.submit(update_all)

        self._next_update = [time.monotonic() + self.update_interval] * len(self._caches)

    def _replot(self, axis_index: int, cache: TimeCache) -> None:
        """Updates given cache.

        Parameters
        ----------
        cache : TimeCache
            Time cache from which data shall be updated.
        """
        if self.time_axis is None:
            return

        axis = self.axes(Qt.Vertical)[axis_index]
        d_min = d_max = None
        for n in cache.columns()[1:]:
            serie = self.find_serie(n)
            if serie is None or serie.isVisible() is False:
                continue

            if cache.empty():
                continue

            data = cache[n]
            if d_min is None or d_max is None:
                d_min = min(data)
                d_max = max(data)
            else:
                d_min = min(d_min, min(data))
                d_max = max(d_max, max(data))

            points = [QPointF(*i) for i in zip(cache["timestamp"], data)]

            serie.replace(points)

        self.time_axis.setRange(*[QDateTime().fromMSecsSinceEpoch(int(t)) for t in cache.time_range()])
        if d_min == d_max:
            if d_min == 0 or d_min is None or d_max is None:
                d_min = -1
                d_max = 1
            else:
                d_min -= d_min * 0.05
                d_max += d_max * 0.05

        axis.setRange(d_min, d_max)

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

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Zoom on mouse wheel action."""
        self.chart().zoom(1.1 if event.angleDelta().y() > 0 else 0.9)

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        context_menu = QMenu()

        for s in self.chart().series():
            action = context_menu.addAction(s.name())
            action.setCheckable(True)
            action.setChecked(s.isVisible())

        context_menu.addSeparator()

        # add actions for different zooming
        actions_rb = {
            "Verical": QChartView.VerticalRubberBand,
            "Horizontal": QChartView.HorizontalRubberBand,
            "Rectangle": QChartView.RectangleRubberBand,
        }

        rb = self.rubberBand()

        for title, a_rb in actions_rb.items():
            action = context_menu.addAction(title)
            action.setCheckable(True)
            action.setChecked(rb == a_rb)

        context_menu.addSeparator()

        context_menu.addAction("Zoom &in")
        context_menu.addAction("Zoom &out")
        context_menu.addAction("&Reset zoom")

        selected = context_menu.exec_(event.globalPos())

        if selected is None or selected.text() is None:
            return

        for s in self.chart().series():
            if selected.text() == s.name():
                s.setVisible(selected.isChecked())
                return

        if selected.text() in actions_rb:
            self.setRubberBand(actions_rb[selected.text()])
        elif selected.text() == "Zoom &in":
            self.chart().zoomIn()
        elif selected.text() == "Zoom &out":
            self.chart().zoomOut()
        elif selected.text() == "&Reset zoom":
            self.chart().zoomReset()
