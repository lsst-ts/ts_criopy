# This file is part of M1M3 SS GUI.
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

from PySide2.QtCore import Qt, QDateTime, QPointF, Signal, Slot
from PySide2.QtGui import QPainter
from PySide2.QtCharts import QtCharts
from PySide2.QtWidgets import QMenu

from lsst.ts.utils import make_done_future
from lsst.ts.cRIOpy import TimeCache
import time

import concurrent.futures
from functools import partial

__all__ = [
    "TimeChart",
    "UserSelectedTimeChart",
    "TimeChartView",
    "SALAxis",
    "SALChartWidget",
]


class AbstractChart(QtCharts.QChart):
    def __init__(self, parent=None, wFlags=Qt.WindowFlags()):
        super().__init__(parent, wFlags)

    def findAxis(self, titleText, axisType=Qt.Vertical):
        for a in self.axes(axisType):
            if a.titleText() == titleText:
                return a
        return None

    def findSerie(self, name):
        """
        Returns serie with given name.

        Parameters
        ----------
        name : `str`
            Serie name.

        Returns
        -------
        serie : `QAbstractSerie`
            Serie with given name. None if no serie exists.
        """
        for s in self.series():
            if s.name() == name:
                return s
        return None

    def remove(self, name):
        """Removes serie with given name."""
        s = self.findSerie(name)
        if s is None:
            return
        self.removeSeries(s)

    def clearData(self):
        """Removes all data from the chart."""
        self.removeAllSeries()
        for a in self.axes(Qt.Vertical):
            self.removeAxis(a)


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
    maxItems : `int`, optional
        Number of items to keep in graph. When series grows above the specified
        number of points, oldest points are removed. Defaults to 50 * 30 = 50Hz * 30s.
    updateInterval: `float`, optional
        Interval for chart redraws responding to append call. Defaults to 0.1 second.
    """

    def __init__(self, items, maxItems=50 * 30, updateInterval=0.1):
        super().__init__()
        self.maxItems = maxItems
        self.timeAxis = None

        self._next_update = 0
        self.updateInterval = updateInterval
        self.updateTask = make_done_future()

        self._createCaches(items, maxItems)

        self._attachSeries()

    def _addSerie(self, name, axis):
        s = QtCharts.QLineSeries()
        s.setName(name)
        # TODO crashes (core dumps) on some systems. Need to investigate
        # s.setUseOpenGL(True)
        a = self.findAxis(axis)
        if a is None:
            a = QtCharts.QValueAxis()
            a.setTickCount(10)
            a.setTitleText(axis)
            self.addAxis(
                a, Qt.AlignRight if len(self.axes(Qt.Vertical)) % 2 else Qt.AlignLeft
            )
        self.addSeries(s)
        s.attachAxis(a)

    def _attachSeries(self):
        # Caveat emptor, the order here is important. Hard to find, but the order in
        # which chart, axis and series are constructed and attached should always be:
        # - construct Axis, Chart, Serie
        # - addAxis to chart
        # - attach series to axis
        # Changing the order will result in undetermined behaviour, most
        # likely the axis or even graph not shown. It's irrelevant when you
        # fill series with data. See QtChart::createDefaultAxes in QtChart
        # source code for details.
        self.timeAxis = QtCharts.QDateTimeAxis()
        self.timeAxis.setReverse(True)
        self.timeAxis.setTickCount(5)
        self.timeAxis.setFormat("h:mm:ss.zzz")
        self.timeAxis.setTitleText("Time (TAI)")
        self.timeAxis.setGridLineVisible(True)

        self.addAxis(self.timeAxis, Qt.AlignBottom)

        for serie in self.series():
            serie.attachAxis(self.timeAxis)

    def _createCaches(self, items, maxItems=50 * 30):
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
                    self._caches.append(TimeCache(maxItems, data))
                    data = [("timestamp", "f8")]
                else:
                    data.append((d, "f8"))
                    self._addSerie(d, axis[0])
            self._caches.append(TimeCache(maxItems, data))

    def append(self, timestamp, data, axis_index=0, cache_index=None, update=False):
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
            call and update plot if updateInterval passed since the last
            completed update."""
        if cache_index is None:
            cache = self._caches[axis_index]
        else:
            cache = self._caches[cache_index]

        cache.append(tuple([timestamp * 1000.0] + data))

        def replot():
            axis = self.axes(Qt.Vertical)[axis_index]
            d_min = d_max = None
            for n in cache.columns()[1:]:
                serie = self.findSerie(n)
                if serie.isVisible() is False:
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
                *(map(QDateTime().fromMSecsSinceEpoch, cache.timeRange()))
            )
            if d_min == d_max:
                if d_min == 0:
                    d_min = -1
                    d_max = 1
                else:
                    d_min -= d_min * 0.05
                    d_max += d_max * 0.05

            axis.setRange(d_min, d_max)

            self._next_update = time.monotonic() + self.updateInterval

        # replot if needed
        if update:
            self.updateTask.cancel()
            self._next_update = 0

        if (
            self._next_update < time.monotonic()
            and self.updateTask.done()
            and self.isVisibleTo(None)
        ):
            with concurrent.futures.ThreadPoolExecutor() as pool:
                self.updateTask = pool.submit(replot)

    def clearData(self):
        """Removes all data from the chart."""
        super().removeAllSeries()


class UserSelectedTimeChart(TimeChart):
    """
    Signals
    -------
    topicSelected : `Signal(object)`
        Send when DataUnitLabel or DataLabel is clicked. Object parameters
        denotes selected label.
    """

    topicSelected = Signal(object)

    def __init__(self, topics):
        super().__init__(None)
        self._topics = topics
        self._signal = None
        self._name = None
        self.topicSelected.connect(self._topicSelected)

    @Slot(str)
    def _topicSelected(self, obj):
        name = obj.objectName()
        self._createCaches({obj.unit_name: [name]})
        self._attachSeries()
        for (t, s) in self._topics.items():
            for n in vars(t.DataType()):
                if n != name:
                    continue

                if self._signal is not None:
                    self._signal.disconnect(self._appendData)

                self._signal = s
                self._name = name

                self._signal.connect(self._appendData)
                break

    @Slot(map)
    def _appendData(self, data):
        self.append(data.private_sndStamp, [getattr(data, self._name)])


class TimeChartView(QtCharts.QChartView):
    """Time chart view. Add handling of mouse move events.

    Parameters
    ----------
    chart : `QChart`, optional
        Chart associated with view. Defaults to None.
    """

    def __init__(self, chart=None):
        if chart is None:
            super().__init__()
        else:
            super().__init__(chart)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRubberBand(QtCharts.QChartView.HorizontalRubberBand)

    def contextMenuEvent(self, event):
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


class SALAxis:
    def __init__(self, title, signal):
        self.title = title
        self.signal = signal
        self.fields = {}

    def addValue(self, name, field):
        self.fields[name] = field
        return self

    def addValues(self, fields):
        self.fields = {**self.fields, **fields}
        return self


class SALChartWidget(TimeChartView):
    """
    Widget plotting SAL data. Connects to SAL signal triggered when new data
    arrives and redraw graph.

    Parameters
    ----------
    fields : `[SALAxis]` or `SALAxis`
        Array of axis to plot.

    Example
    -------
        a1 = SALAxis("Measured Forces (N)", m1m3.measuredForces)
        a1.addValue("X", "xForce")
        a1.addValue("Y", "yForce")
        a1.addValue("Z", "zForce")

        a2 = SALAxis("Applied Forces (N)", m1m3.appliedForces)
        a2.addValues({"X" : "xForce", "Y" : "yForce", "Z" : "zForce"})

        chart = SALChartWidget(a1, a2, SALAxis("Pre-clipped Forces (N)", m1m3.preclippedForces).addValue("X", "xForce"))
    """

    def __init__(self, *values, **kwargs):
        self.chart = TimeChart(
            dict([(v.title, v.fields.keys()) for v in values]), **kwargs
        )
        axis_index = 0
        for v in values:
            v.signal.connect(
                partial(self._append, axis_index=axis_index, fields=v.fields)
            )
            axis_index += 1

        super().__init__(self.chart)

    def _append(self, data, axis_index, fields):
        self.chart.append(
            data.timestamp,
            [getattr(data, f) for f in fields.values()],
            axis_index=axis_index,
        )
