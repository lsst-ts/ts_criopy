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
# along with this program.If not, see <https://www.gnu.org/licenses/>.

import typing
from functools import partial

from PySide2.QtCore import Signal

from ..TimeChart import TimeChart, TimeChartView

__all__ = ["Axis", "ChartWidget"]

AxisVar = typing.TypeVar("AxisVar", bound="Axis")


class Axis:
    """
    Represents axis in SALChartWidget. Series should be added by various
    addValue* methods.

    Parameters
    ----------
    title : `str`
        Axis title. Will be shown next to the axis.
    signal : `Signal`
        Signal the axis gets it's data from.
    """

    def __init__(self, title: str, signal: Signal):
        self.title = title
        self.signal = signal
        self.fields: dict[str, str | tuple[str, int]] = {}

    def addValue(self: AxisVar, name: str, field: str) -> AxisVar:
        self.fields[name] = field
        return self

    def addArrayValue(self: AxisVar, name: str, field: str, index: int) -> AxisVar:
        self.fields[name] = (field, index)
        return self

    def addValues(self: AxisVar, fields: dict[str, str]) -> AxisVar:
        self.fields = {**self.fields, **fields}
        return self


class ChartWidget(TimeChartView):
    """
    Widget plotting SAL data. Connects to SAL signal triggered when new data
    arrives and redraw graph.

    Parameters
    ----------
    *values : `Axis`
        Axis or axes to plot.

    Example
    -------
        a1 = Axis("Measured Forces (N)", m1m3.measuredForces)
        a1.addValue("X", "xForce")
        a1.addValue("Y", "yForce")
        a1.addValue("Z", "zForce")

        a2 = Axis("Applied Forces (N)", m1m3.appliedForces)
        a2.addValues({"X" : "xForce", "Y" : "yForce", "Z" : "zForce"})

        chart = ChartWidget(a1, a2, Axis(
            "Pre-clipped Forces (N)",
            m1m3.preclippedForces,
        ).addValue("X", "xForce"))
    """

    def __init__(
        self, *values: Axis, max_items: int = 50 * 30, update_interval: float = 0.1
    ):
        self.chart = TimeChart(
            {v.title: list(v.fields.keys()) for v in values}, max_items, update_interval
        )
        axis_index = 0
        for v in values:
            v.signal.connect(
                partial(
                    self._append, axis_index=axis_index, fields=list(v.fields.values())
                )
            )
            axis_index += 1
        self._has_timestamp: bool | None = None

        super().__init__(self.chart)

    def _append(self, data: typing.Any, axis_index: int, fields: list[str]) -> None:
        if self._has_timestamp is None:
            try:
                getattr(data, "timestamp")
                self._has_timestamp = True
            except AttributeError:
                self._has_timestamp = False

        displayData = []
        for f in fields:
            if type(f) is tuple:
                displayData.append(getattr(data, f[0])[f[1]])
            else:
                displayData.append(getattr(data, f))

        self.chart.append(
            data.timestamp if self._has_timestamp else data.private_sndStamp,
            displayData,
            axis_index=axis_index,
        )
