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

from lsst.ts.salobj import BaseMsgType
from PySide6.QtCore import Signal

from ..time_chart import TimeChart, TimeChartView

__all__ = ["AxisValue", "Axis", "ChartWidget"]

AxisVar = typing.TypeVar("AxisVar", bound="Axis")


class AxisValue:
    def __init__(self, field: str, index: int | None = None, scale: float | None = None):
        self.field = field
        self.index = index
        self.scale = scale

    def get_value(self, data: BaseMsgType) -> float:
        if self.index is not None:
            ret = getattr(data, self.field)[self.index]
        else:
            ret = getattr(data, self.field)
        if self.scale is not None:
            return ret * self.scale
        return ret


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
        self.fields: dict[str, AxisValue] = {}

    def addValue(self: AxisVar, name: str, field: str, scale: float | None = None) -> AxisVar:
        self.fields[name] = AxisValue(field, scale=scale)
        return self

    def addArrayValue(self, name: str, field: str, index: int) -> typing.Self:
        self.fields[name] = AxisValue(field, index)
        return self

    def add_values(self, fields: dict[str, AxisValue]) -> typing.Self:
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
        a2.add_values({
            "X" : AxisValue("xForce"),
            "Y" : AxisValue("yForce"),
            "Z" : AxisValue("zForce")
        })

        chart = ChartWidget(a1, a2, Axis(
            "Pre-clipped Forces (N)",
            m1m3.preclippedForces,
        ).addValue("X", "xForce"))
    """

    def __init__(self, *values: Axis, max_items: int = 50 * 30, update_interval: float = 0.1):
        self.chart = TimeChart({v.title: list(v.fields.keys()) for v in values}, max_items, update_interval)
        axis_index = 0
        for v in values:
            v.signal.connect(partial(self._append, axis_index=axis_index, fields=v.fields.values()))
            axis_index += 1
        self._has_timestamp: bool | None = None

        super().__init__(self.chart)

    def _append(
        self,
        data: BaseMsgType,
        axis_index: int,
        fields: typing.Iterable[AxisValue],
    ) -> None:
        if self._has_timestamp is None:
            try:
                getattr(data, "timestamp")
                self._has_timestamp = True
            except AttributeError:
                self._has_timestamp = False

        display_data = []
        for f in fields:
            display_data.append(f.get_value(data))

        self.chart.append(
            data.timestamp if self._has_timestamp else data.private_sndStamp,
            display_data,
            axis_index=axis_index,
        )
