# This file is part of M1M3 SS GUI.
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re
import typing

import astropy.units as u
from lsst.ts.salobj import BaseMsgType
from PySide6.QtCore import Slot

from .colors import Colors

__all__ = ["DataFormator", "MinFormator", "MaxFormator"]


class DataFormator:
    """Class formating data prior to displaying them. Internal state of the
    formator can be reseted by emitting reset_formator signal.

    Parameters
    ----------
    field : `str`, optional
        When specified (and signal parameter is provided), will use this field
        as fieldname from data arriving with the signal. Defaults to None.
    fmt : `str`, optional
        Format string. See Python formatting function for details. Defaults to
        'd' for decimal number.
    unit : `astropy.units`, optional
        Variable unit. Default is None - no unit
    convert : `astropy.units`, optional
        Convert values to this unit. Default is None - no unit. If provided,
        unit must be provided as well.
    is_warn_func : `func`, optional
        Function evaluated on each value. If true is returned, value is assumed
        to be in warning range and will be color coded (displayed in warning
        text). Default is None - no color coded warning value.
    is_err_func : `func`, optional
        Function evaluated on each value. If true is returned, value is assumed
        to be in error range and will be color coded (displayed in error
        text). Default is None - no color coded error value.
    """

    def __init__(
        self,
        field: str | None = None,
        fmt: str = "d",
        unit: str | u.Unit | None = None,
        convert: u.Unit | None = None,
        is_warn_func: typing.Callable[[float], bool] | None = None,
        is_err_func: typing.Callable[[float], bool] | None = None,
    ):
        self._field = field

        self.fmt = fmt
        if isinstance(unit, str):
            unit = u.Unit(unit)

        if unit is not None:
            assert issubclass(unit.__class__, u.UnitBase)

        if convert is not None:
            if unit is None:
                raise RuntimeError("Cannot specify conversion without input units!")
            self.scale = unit.to(convert)
            self.unit_name = convert.to_string()
        elif unit is not None:
            self.scale = 1
            self.unit_name = unit.to_string()
        else:
            self.scale = 1
            self.unit_name = ""

        # we can display some units better using unicode
        aliases = {
            "deg_C": "°C",
            "1 / min": "RPM",
            "m N": "N m",
        }
        try:
            self.unit_name = aliases[self.unit_name]
        except KeyError:
            pass

        self.unit_name = re.sub(r"\bdeg[^;]", "°", self.unit_name)

        # s2, s3 using sup
        self.unit_name = self.unit_name.replace("s2", "s<sup>2</sup>")
        self.unit_name = self.unit_name.replace("s3", "s<sup>3</sup>")

        self.unit_name = " " + self.unit_name

        self.unit = unit
        self.convert = convert
        self.is_warn_func = is_warn_func
        self.is_err_func = is_err_func

    def format(self, data: BaseMsgType) -> str:
        """Does the formating.

        Parameters
        ----------
        data : `BaseMsgType`
            New data, in SALobj/ts_xml structure.

        Returns
        -------
        str
            String to display in the label."""
        assert self._field is not None

        value = getattr(data, self._field)
        text = f"{(value * self.scale):{self.fmt}}{self.unit_name}"

        if self.is_err_func is not None and self.is_err_func(value):
            text = "<font color='{Colors.ERROR.name()}'>{text}</font>"
        elif self.is_warn_func is not None and self.is_warn_func(value):
            text = f"<font color='{Colors.WARNING.name()}'>{text}</font>"
        return text

    @Slot()
    def reset_formator(self) -> None:
        """Called to reset collected data. Placeholder for resetting internal
        state of the formator."""
        pass


class MinFormator(DataFormator):
    """Display minimum value of received data. Resets minimum on reset_formator
    signal."""

    _current_data: BaseMsgType = None

    def format(self, data: BaseMsgType) -> str:
        assert self._field is not None

        if self._current_data is None:
            self._current_data = data
        else:
            if getattr(data, self._field) < getattr(self._current_data, self._field):
                self._current_data = data
        return super().format(self._current_data)

    @Slot()
    def reset_formator(self) -> None:
        self._current_data = None


class MaxFormator(DataFormator):
    """Display maximum value of received data. Resets maximum on reset_formator
    signal."""

    _current_data: BaseMsgType = None

    def format(self, data: BaseMsgType) -> str:
        assert self._field is not None

        if self._current_data is None:
            self._current_data = data
        else:
            if getattr(data, self._field) > getattr(self._current_data, self._field):
                self._current_data = data
        return super().format(self._current_data)

    @Slot()
    def reset_formator(self) -> None:
        self._current_data = None
