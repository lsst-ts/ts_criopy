# This file is part of the cRIO GUI.
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

import typing
from datetime import datetime

import astropy.units as u
from astropy.coordinates import Angle
from lsst.ts.salobj import BaseMsgType
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QDockWidget,
    QFrame,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..salcomm import MetaSAL
from .colors import Colors
from .event_window import EventWindow
from .formators import DataFormator, Formator, MaxFormator, MinFormator

__all__ = [
    "VLine",
    "ColoredButton",
    "DataLabel",
    "DataFormatorLabel",
    "FormatLabel",
    "UnitLabel",
    "DataUnitLabel",
    "Force",
    "Moment",
    "Mm",
    "Arcsec",
    "Ampere",
    "Liter",
    "LiterMinute",
    "Percent",
    "Volt",
    "RPM",
    "PressureInBar",
    "PressureInmBar",
    "Hours",
    "Seconds",
    "MilliSeconds",
    "MinMilliSeconds",
    "MaxMilliSeconds",
    "KiloWatt",
    "DMS",
    "DataDegC",
    "Hz",
    "DegS2",
    "MSec2",
    "ArcsecWarning",
    "MmWarning",
    "OnOffLabel",
    "PowerOnOffLabel",
    "ConnectedLabel",
    "ErrorLabel",
    "WarningLabel",
    "WarningButton",
    "InterlockOffLabel",
    "StatusLabel",
    "EnumLabel",
    "Clipped",
    "Heartbeat",
    "LogEventWarning",
    "SimulationStatus",
    "DockWindow",
]


class VLine(QFrame):
    """A simple Vertical line."""

    def __init__(self) -> None:
        super().__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


class ColoredButton(QPushButton):
    """Button with setColor method to change color."""

    def __init__(self, text: str):
        super().__init__(text)

    def setColor(self, color: QColor | None) -> None:
        """Sets button color.

        Parameters
        ----------
        color : `QColor`
            New button background color. If None, color isn't changed.
        """
        pal = self.palette()
        if color is None:
            color = pal.base().color()

        pal.setColor(QPalette.Button, color)
        self.setPalette(pal)

    def setTextColor(self, text: str, color: QColor) -> None:
        """Sets button text and color.
        Parameters
        ----------
        text : `str`
            New button text.
        color : `QColor`
            New button background color.
        """
        self.setText(text)
        self.setColor(color)


class DataLabel(QLabel):
    """Displays data from (SAL originated) signal.

    Parameters
    ----------
    signal : `Signal`, optional
        When not None, given signal will be connected to method calling
        setValue with a field from signal data. Field is the second argument.
        Defaults to None.
    field : `str`, optional
        When specified (and signal parameter is provided), will use this field
        as fieldname from data arriving with the signal. This will be store as
        object name. Defaults to None.
    """

    def __init__(self, signal: Signal | None = None, field: str | None = None):
        super().__init__("---")
        self._field = field
        if signal is not None:
            signal.connect(self.new_data)
        if field is not None:
            self.setObjectName(field)
            self.setCursor(Qt.PointingHandCursor)

    def __copy__(self) -> "DataLabel":
        return DataLabel()

    @Slot()
    def new_data(self, data: BaseMsgType) -> None:
        """Called when new data arrives. Updates label text."""
        assert self._field is not None
        self.setValue(getattr(data, self._field))

    def setValue(self, value: typing.Any) -> None:
        """Sets value.

        Parameters
        ----------
        value : `bool`
            Current (=to be displayed) variable value. True means warning.
        """
        self.setText(str(value))


class UnitLabel(QLabel):
    """Qt Label that can display and convert Astropy units.

    Parameters
    ----------
    formator : Formator
        Object formating new data. It can be used to collect statistics -
        displaying instead of the actual value minimum, maximum or similar
        calculated values."""

    resetFormat = Signal()

    def __init__(
        self,
        formator: Formator | None = None,
    ):
        super().__init__("---")
        self.formator = Formator() if formator is None else formator

        self.resetFormat.connect(self.formator.reset_formator)

    def __copy__(self) -> "UnitLabel":
        return UnitLabel(self.formator)

    def setValue(self, value: float) -> None:
        """Sets value. Transformation and formatting is done according to unit,
        convert and fmt constructor arguments.

        Parameters
        ----------
        value : `float`
            Current (=to be displayed) variable value.
        """
        self.setText(self.formator.format(value))

    def setTextColor(self, color: QColor) -> None:
        """Change text color.

        Parameters
        ----------
        color : `QColor`a
            New text color.
        """
        pal = self.palette()
        pal.setColor(QPalette.WindowText, color)
        self.setPalette(pal)


class FormatLabel(UnitLabel):
    """A simply formatting label.

    Parameters
    ----------
    fmt : `str`
        Format string. See Python formatting function for details. Defaults to
        'd' for decimal number.
    """

    def __init__(self, fmt: str):
        super().__init__(Formator(fmt))


class DataFormatorLabel(UnitLabel):
    """Formated unit label. Add formating and handling of the cursor
    interactions.

    Parameters
    ----------
    signal : `Signal`
        When not None, given signal will be connected to method calling
        setValue with a field from signal data. Field is the second argument.
    formator : DataFormator
        Object formating new data. It can be used to collect statistics -
        displaying instead of the actual value minimum, maximum or similar
        calculated values.
    """

    def __init__(self, signal: Signal | None, formator: DataFormator):
        super().__init__(formator)

        if signal is not None:
            signal.connect(self.new_data)

        self.setObjectName(formator._field)
        self.setCursor(Qt.PointingHandCursor)

    @Slot()
    def new_data(self, data: BaseMsgType) -> None:
        self.setText(self.formator.format_data(data))  # type: ignore[attr-defined]


class DataUnitLabel(DataFormatorLabel):
    """Combines DataFormatorLabel and UnitLabel handling for SAL data with
    error and warning functions. Parameters specify signal and field name (as
    in DataLabel) and display options (as in UnitLabel).

    Parameters
    ----------
    signal : `Signal`, optional
        When not None, given signal will be connected to method calling
        setValue with a field from signal data. Field is the second argument.
        Defaults to None.
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
        to be in warning range and will be color coded (displayed in warning
        text). Default is None - no color coded error value.
    """

    def __init__(
        self,
        signal: Signal | None = None,
        field: str | None = None,
        fmt: str = "f",
        unit: str | u.Unit | None = None,
        convert: u.Unit | None = None,
        is_warn_func: typing.Callable[[float], bool] | None = None,
        is_err_func: typing.Callable[[float], bool] | None = None,
    ):
        super().__init__(
            signal, DataFormator(field, fmt, unit, convert, is_warn_func, is_err_func)
        )


class Force(DataUnitLabel):
    """Displays force in N (Newtons).

    Parameters
    ----------
    signal : `Signal`, optional
        Signal the force connect to.
    field : `str`, optional
        Topic/signal field holding the value to display.
    fmt : `str`, optional
        Float formatting. Defaults to .02f.
    """

    def __init__(
        self, signal: Signal | None = None, field: str | None = None, fmt: str = "0.02f"
    ):
        super().__init__(signal, field, fmt, u.N)


class Moment(UnitLabel):
    """Displays moment in N*m (Newtons meters).

    Parameters
    ----------
    fmt : `str`, optional
        Float formatting. Defaults to .02f.
    """

    def __init__(self, fmt: str = ".02f"):
        super().__init__(Formator(fmt, u.N * u.m))


class Mm(UnitLabel):
    """Display meters as mm (millimeters).

    Parameters
    ----------
    fmt : `str`, optional
        Float formatting. Defaults to .04f.
    """

    def __init__(
        self,
        fmt: str = ".04f",
        is_warn_func: typing.Callable[[float], bool] | None = None,
        is_err_func: typing.Callable[[float], bool] | None = None,
    ):
        super().__init__(Formator(fmt, u.meter, u.mm, is_warn_func, is_err_func))


class MmWarning(Mm):
    """Display meters as mm (millimeters). Shows values above threshold as
    error / fault.

    Parameters
    ----------
    fmt : `str`, optional
        Float formatting. Defaults to .04f.
    warning_threshold : `float`, optional
        If abs(value) is above the threshold, display value as warning (bright
        text). Defaults to 4 microns, half allowed deviation.
    error_threshold : `float`, optional
        If abs(value) is above the threshold, display value as error (red
        text). Defaults to 8 microns, full sensor error budget.
    """

    def __init__(
        self,
        fmt: str = ".04f",
        warning_threshold: float = 4 * u.um.to(u.meter),
        error_threshold: float = 8 * u.um.to(u.meter),
    ):
        super().__init__(
            fmt,
            lambda v: abs(v) > warning_threshold,
            lambda v: abs(v) > error_threshold,
        )


class Arcsec(UnitLabel):
    """Display degrees as arcseconds.

    Parameters
    ----------
    fmt : `str`, optional
        Float formatting. Defaults to .02f.
    """

    def __init__(
        self,
        fmt: str = "0.02f",
        is_warn_func: typing.Callable[[float], bool] | None = None,
        is_err_func: typing.Callable[[float], bool] | None = None,
    ):
        super().__init__(Formator(fmt, u.deg, u.arcsec, is_warn_func, is_err_func))


class Ampere(DataUnitLabel):
    """Displays Ampere.

    Parameters
    ----------
    signal : `Signal`, optional
        When not None, given signal will be connected to method calling
        setValue with a field from signal data. Field is the second argument.
        Defaults to None.
    field : `str`, optional
        When specified (and signal parameter is provided), will use this field
        as fieldname from data arriving with the signal. Defaults to None.
    fmt : `str`, optional
        Float formatting. Defaults to 0.02f.
    """

    def __init__(
        self, signal: Signal | None = None, field: str | None = None, fmt: str = "0.02f"
    ):
        super().__init__(signal, field, fmt, u.A)


class Liter(DataUnitLabel):
    """Displays Liters.

    Parameters
    ----------
    signal : `Signal`, optional
        When not None, given signal will be connected to method calling
        setValue with a field from signal data. Field is the second argument.
        Defaults to None.
    field : `str`, optional
        When specified (and signal parameter is provided), will use this field
        as fieldname from data arriving with the signal. Defaults to None.
    fmt : `str`, optional
        Float formatting. Defaults to 0.02f.
    """

    def __init__(
        self, signal: Signal | None = None, field: str | None = None, fmt: str = "0.02f"
    ):
        super().__init__(signal, field, fmt, u.liter)


class LiterMinute(DataUnitLabel):
    """Displays Liters per Minute.

    Parameters
    ----------
    signal : `Signal`, optional
        When not None, given signal will be connected to method calling
        setValue with a field from signal data. Field is the second argument.
        Defaults to None.
    field : `str`, optional
        When specified (and signal parameter is provided), will use this field
        as fieldname from data arriving with the signal. Defaults to None.
    fmt : `str`, optional
        Float formatting. Defaults to 0.02f.
    """

    def __init__(
        self, signal: Signal | None = None, field: str | None = None, fmt: str = "0.02f"
    ):
        super().__init__(signal, field, fmt, u.liter / u.minute)


class Percent(DataUnitLabel):
    """Displays percents.

    Parameters
    ----------
    signal : `Signal`, optional
        When not None, given signal will be connected to method calling
        setValue with a field from signal data. Field is the second argument.
        Defaults to None.
    field : `str`, optional
        When specified (and signal parameter is provided), will use this field
        as fieldname from data arriving with the signal. Defaults to None.
    fmt : `str`, optional
        Float formatting. Defaults to 0.02f.
    """

    def __init__(
        self, signal: Signal | None = None, field: str | None = None, fmt: str = "0.02f"
    ):
        super().__init__(signal, field, fmt, u.percent)


class Volt(DataUnitLabel):
    """Displays Volts.

    Parameters
    ----------
    signal : `Signal`, optional
        When not None, given signal will be connected to method calling
        setValue with a field from signal data. Field is the second argument.
        Defaults to None.
    field : `str`, optional
        When specified (and signal parameter is provided), will use this field
        as fieldname from data arriving with the signal. Defaults to None.
    fmt : `str`, optional
        Float formatting. Defaults to 0.02f.
    """

    def __init__(
        self, signal: Signal | None = None, field: str | None = None, fmt: str = "0.02f"
    ):
        super().__init__(signal, field, fmt, u.V)


class RPM(DataUnitLabel):
    """Displays RPM.

    Parameters
    ----------
    signal : `Signal`, optional
        When not None, given signal will be connected to method calling
        setValue with a field from signal data. Field is the second argument.
        Defaults to None.
    field : `str`, optional
        When specified (and signal parameter is provided), will use this field
        as fieldname from data arriving with the signal. Defaults to None.
    fmt : `str`, optional
        Float formatting. Defaults to .0f.
    """

    def __init__(
        self, signal: Signal | None = None, field: str | None = None, fmt: str = ".0f"
    ):
        super().__init__(signal, field, fmt, u.Unit("min^-1"))


class PressureInBar(DataUnitLabel):
    """Display pressure in bar and psi"""

    def __init__(self, signal: Signal | None = None, field: str | None = None):
        super().__init__(signal, field)
        self.unit_name = "bar"

    def setValue(self, value: float) -> None:
        psi = value * u.mbar.to(u.imperial.psi)
        self.setText(f"{value:.04f} bar ({psi:.02f} psi)")


class PressureInmBar(DataLabel):
    def __init__(self, signal: Signal | None = None, field: str | None = None):
        super().__init__(signal, field)
        self.unit_name = "mbar"  # this is only for display

    def setValue(self, value: float) -> None:
        mbar = value * u.mbar
        bar = (mbar).to(u.bar).value
        psi = mbar.to(u.imperial.psi).value
        self.setText(f"{bar:.04f} bar ({psi:.02f} psi)")


class Hours(DataUnitLabel):
    def __init__(self, field: str | None = None):
        super().__init__(None, field, ".0f", u.h)


class Seconds(DataUnitLabel):
    def __init__(self, field: str | None = None):
        super().__init__(None, field, ".0f", u.s)


class MilliSeconds(DataUnitLabel):
    def __init__(self, field: str | None = None):
        super().__init__(None, field, ".1f", u.s, u.ms)


class MinMilliSeconds(DataFormatorLabel):
    def __init__(self, field: str | None = None):
        super().__init__(None, MinFormator(field, ".1f", u.s, u.ms))


class MaxMilliSeconds(DataFormatorLabel):
    def __init__(self, field: str | None = None):
        super().__init__(None, MaxFormator(field, ".1f", u.s, u.ms))


class KiloWatt(DataUnitLabel):
    def __init__(self, signal: Signal | None = None, field: str | None = None):
        super().__init__(signal, field, ".01f", u.kW)


class DMS(DataUnitLabel):
    def __init__(
        self, signal: Signal | None = None, field: str | None = None, fmt: str = ".02f"
    ):
        super().__init__(signal, field, fmt)

    def setValue(self, value: float) -> None:
        dms = Angle(value * u.deg).dms
        self.setText(
            f"{dms.d:.0f}<b>°</b> {dms.m:02.0f}<b>'</b> {dms.s:05.02f}<b>\"</b>"
        )


class DataDegC(DataUnitLabel):
    def __init__(
        self, signal: Signal | None = None, field: str | None = None, fmt: str = ".02f"
    ):
        super().__init__(signal, field, fmt, u.deg_C)


class Hz(DataUnitLabel):
    def __init__(
        self, signal: Signal | None = None, field: str | None = None, fmt: str = ".02f"
    ):
        super().__init__(signal, field, fmt, u.Hz)


class DegS2(DataUnitLabel):
    def __init__(
        self, signal: Signal | None = None, field: str | None = None, fmt: str = ".02f"
    ):
        super().__init__(signal, field, fmt, u.deg / u.s**2)


class MSec2(DataUnitLabel):
    def __init__(
        self, signal: Signal | None = None, field: str | None = None, fmt: str = ".02f"
    ):
        super().__init__(signal, field, fmt, u.m / u.s**2)


class ArcsecWarning(Arcsec):
    """Display degrees as arcseconds. Shows values above threshold as error /
    fault.

    Parameters
    ----------
    fmt : `str`, optional
        Float formatting. Defaults to 0.02f.
    warning_threshold : `float`, optional
        If abs(value) is above the threshold, display value as warning (bright
        text). Defaults to 0.73 arcsecond, half of the allowed measurement
        error.

    error_threshold : `float`, optional
        If abs(value) is above the threshold, display value as error (red
        text).  Defaults to 1.45 arcseconds, full measurement error budget.
    """

    def __init__(
        self,
        fmt: str = "0.02f",
        warning_threshold: float = 0.73 * u.arcsec.to(u.deg),
        error_threshold: float = 1.45 * u.arcsec.to(u.deg),
    ):
        super().__init__(
            fmt,
            lambda v: abs(v) > warning_threshold,
            lambda v: abs(v) > error_threshold,
        )


class OnOffLabel(DataLabel):
    """Displays on/off warnings

    Parameters
    ----------
    signal : `Signal`, optional
        When not None, given signal will be connected to method calling
        setValue with a field from signal data. Field is the second argument.
        Defaults to None.
    field : `str`, optional
        When specified (and signal parameter is provided), will use this field
        as fieldname from data arriving with the signal. Defaults to None.
    """

    def __init__(self, signal: Signal | None = None, field: str | None = None):
        super().__init__(signal, field)

    def __copy__(self) -> "OnOffLabel":
        return OnOffLabel()

    def setValue(self, value: float) -> None:
        """Sets formatted value. Color codes On (red)/Off (green).

        Parameters
        ----------
        value : `bool`
            Current (=to be displayed) variable value. True means warning/error
            is raised.
        """
        if value:
            self.setText(f"<font color='{Colors.ERROR.name()}'>On</font>")
        else:
            self.setText(f"<font color='{Colors.OK.name()}'>Off</font>")


class PowerOnOffLabel(DataLabel):
    """Displays on/off power state"""

    def __init__(self, signal: Signal | None = None, field: str | None = None):
        super().__init__(signal, field)

    def __copy__(self) -> "PowerOnOffLabel":
        return PowerOnOffLabel()

    def setValue(self, value: float) -> None:
        """Sets formatted value. Color codes On (red)/Off (green).

        Parameters
        ----------
        value : `bool`
            Current (=to be displayed) variable value. True means power is On.
        """
        if value:
            self.setText("<font color='green'>On</font>")
        else:
            self.setText("<font color='gold'>Off</font>")


class ConnectedLabel(DataLabel):
    """Displays connection status. Constructor can be passed parameters
    allowing connection to a Signal emitted when warning value changes.

    Parameters
    ----------
    signal : `Signal`, optional
        When not None, given signal will be connected to method calling
        setValue with a field from signal data. Field is the second argument.
        Defaults to None.
    field : `str`, optional
        When specified (and signal parameter is provided), will use this field
        as fieldname from data arriving with the signal. This will be store as
        object name. Defaults to None.
    """

    def __init__(self, signal: Signal | None = None, field: str | None = None):
        super().__init__(signal, field)

    def __copy__(self) -> "ConnectedLabel":
        return ConnectedLabel()

    def setValue(self, is_connected: bool) -> None:
        """Sets formatted value. Color codes ERROR (red)/OK (green).

        Parameters
        ----------
        is_connected : `bool`
            Current (=to be displayed) variable value. True means connected.
        """
        if is_connected:
            self.setText(f"<font color='{Colors.OK.name()}'>Connected</font>")
        else:
            self.setText(f"<font color='{Colors.ERROR.name()}'>Disconnected</font>")


class ErrorLabel(DataLabel):
    """Displays ERROR/OK. Constructor can be passed parameters allowing
    connection to a Signal emitted when warning value changes.

    Parameters
    ----------
    signal : `Signal`, optional
        When not None, given signal will be connected to method calling
        setValue with a field from signal data. Field is the second argument.
        Defaults to None.
    field : `str`, optional
        When specified (and signal parameter is provided), will use this field
        as fieldname from data arriving with the signal. This will be store as
        object name. Defaults to None.
    """

    def __init__(self, signal: Signal | None = None, field: str | None = None):
        super().__init__(signal, field)

    def __copy__(self) -> "ErrorLabel":
        return ErrorLabel()

    def setValue(self, value: bool) -> None:
        """Sets formatted value. Color codes ERROR (red)/OK (green).

        Parameters
        ----------
        value : `bool`
            Current (=to be displayed) variable value. True means error.
        """
        if value:
            self.setText(f"<font color='{Colors.ERROR.name()}'>ERROR</font>")
        else:
            self.setText(f"<font color='{Colors.OK.name()}'>OK</font>")


class WarningLabel(DataLabel):
    """Displays WARNING/OK. Constructor can be passed parameters allowing
    connection to a Signal emitted when warning value changes.

    Parameters
    ----------
    signal : `Signal`, optional
        When not None, given signal will be connected to method calling
        setValue with a field from signal data. Field is the second argument.
        Defaults to None.
    field : `str`, optional
        When specified (and signal parameter is provided), will use this field
        as fieldname from data arriving with the signal. This will be store as
        object name. Defaults to "anyWarning".
    """

    def __init__(self, signal: Signal | None = None, field: str = "anyWarning"):
        super().__init__(signal, field)

    def __copy__(self) -> "WarningLabel":
        return WarningLabel()

    def setValue(self, value: bool) -> None:
        """Sets formatted value. Color codes WARNING (red)/OK (green).

        Parameters
        ----------
        value : `bool`
            Current (=to be displayed) variable value. True means warning.
        """
        if value:
            self.setText(f"<font color='{Colors.ERROR.name()}'>WARNING</font>")
        else:
            self.setText(f"<font color='{Colors.OK.name()}'>OK</font>")


class WarningButton(ColoredButton):
    """Displays WARNING/OK button. When clicked, displays window with values in
    the signal. Button is color-coded (red for problems, green for OK values).

    Parameters
    ----------
    comm : `MetaSAL`
        SALComm object representing the signals
    topic : `str`
        Topic name. Should be event/telemetry name without leading evt_ (for
        events).
    field : `str`, optional
        Field from topic used to display button state. Defaults to anyWarning
    """

    def __init__(self, comm: MetaSAL, topic: str, field: str = "anyWarning"):
        super().__init__("---")
        self.comm = comm
        self._topic = topic
        self._field = field
        getattr(comm, topic).connect(self.newData)
        self.window: None | EventWindow = None
        self.clicked.connect(self._showWindow)

    @Slot()
    def newData(self, data: BaseMsgType) -> None:
        self.setValue(getattr(data, self._field))

    def _showWindow(self) -> None:
        if self.window is None:
            self.window = EventWindow(self.comm, self._topic)
        self.window.show()

    def setValue(self, value: bool) -> None:
        """Sets formatted value. Color codes WARNING (red)/OK (green).

        Parameters
        ----------
        value : `bool`
            Current (=to be displayed) variable value. True means warning.
        """
        if value:
            self.setTextColor("WARNING", Colors.ERROR)
        else:
            self.setTextColor("OK", Colors.OK)


class InterlockOffLabel(QLabel):
    """Displays PROBLEM/OK. Constructor can be passed parameters allowing
    connection to a Signal emitted when warning value changes.

    Parameters
    ----------
    signal : `Signal`, optional
        When not None, given signal will be connected to method calling
        setValue with a field from signal data. Field is the second argument.
        Defaults to None.
    field : `str`, optional
        When specified (and signal parameter is provided), will use this field
        as fieldname from data arriving with the signal. Defaults to
        "anyWarning".
    """

    def __init__(self, signal: Signal | None = None, field: str = "anyWarning"):
        super().__init__("---")
        if signal is not None:
            self._field = field
            signal.connect(self.new_data)

    @Slot()
    def new_data(self, data: BaseMsgType) -> None:
        """Called when new data arrives. Should be overwritten to include data
        pre-processing.

        Parameters
        ----------
        data : `BaseMsgType`
            Message data. As new_data method is connected to data signal, the
            signal stub pass that as additional argument to the call.
        """
        self.setValue(getattr(data, self._field))

    def setValue(self, interlock_off: bool) -> None:
        """Sets formatted value. Color codes WARNING (red)/OK (green).

        Parameters
        ----------
        interlock_off : `bool`
            Current interlock off state. True means interlock is locked
            (=PROBLEM).
        """
        if interlock_off:
            self.setText(f"<font color='{Colors.ERROR.name()}'>PROBLEM</font>")
        else:
            self.setText(f"<font color='{Colors.OK.name()}'>OK</font>")


class StatusLabel(QLabel):
    """Displays OK/Error status."""

    def __init__(self) -> None:
        super().__init__("---")

    def __copy__(self) -> "StatusLabel":
        return StatusLabel()

    def setValue(self, value: bool) -> None:
        """Sets formatted value. Color codes Error (red)/OK (green).

        Parameters
        ----------
        value : `bool`
            Current (=to be displayed) variable value. True means OK.
        """
        if value:
            self.setText(f"<font color='{Colors.OK.name()}'>OK</font>")
        else:
            self.setText(f"<font color='{Colors.ERROR.name()}'>Error</font>")


class EnumLabel(QLabel):
    """Display enumeration values.

    Uses map supplied in constructor to find matching status string.
    """

    def __init__(self, mapping: typing.Dict[int, str]):
        """Construct EnumLable using provided mapping.

        Parameters
        ----------
        mapping : `map(int, str)`
            Enumeration mapping. Key is variable value, value is string (can
            include Qt/html) to display.
        """
        super().__init__("---")
        self._mapping = mapping

    def setValue(self, value: int) -> None:
        try:
            self.setText(self._mapping[value])
        except KeyError:
            self.setText(f"<font color='{Colors.ERROR.name()}'>Unknown {value}</font>")


class Clipped(QLabel):
    "Display clipped/not clipped"

    def __init__(self, force: str):
        super().__init__()
        self._force = force

    def setClipped(self, clipped: bool) -> None:
        if clipped:
            self.setText(
                f"<font color='{Colors.ERROR.name()}'>{self._force} forces clipped</font>"
            )
        else:
            self.setText(
                f"<font color='{Colors.OK.name()}'>{self._force} forces not clipped</font>"
            )


class Heartbeat(QWidget):
    """Display heartbeat. Shows warning/errors if heartbeats are missed. Show
    error if receiving and sending timestamps differs.

    Parameters
    ----------
    parent : `QWidget`, optional
        Parent widget. Defaults to None.

    Slots
    -----
    heartbeat(data)
        Shall be connected to heartbeat signal.

    Example
    -------

    .. code-block:: python
       import SALComm
       from lsst.ts.criopy.gui import Heartbeat

       ...

       comm = SALComm.create("<subsystem>": None)

       ...

       hbWidget = Heartbeat()
       comm.<subsystem>.heartbeat.connect(hbWIdget.heartbeat)
    """

    difftime_error = 0.5
    difftime_warning = 0.01

    def __init__(self, parent: QWidget | None = None, indicator: bool = True):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        if indicator:
            self.hbIndicator = QProgressBar()
            self.hbIndicator.setRange(0, 2)
            self.hbIndicator.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
            layout.addWidget(self.hbIndicator)
        else:
            self.hbIndicator = None

        self.timestamp = QLabel("- waiting -")

        layout.addWidget(self.timestamp)
        self.setLayout(layout)

        self._timeoutTimer: QTimer | None = None
        self._initTimer(3000)

    def _initTimer(self, timeout: int = 2001) -> None:
        if self._timeoutTimer is not None:
            self._timeoutTimer.stop()

        self._timeoutTimer = QTimer(self)
        self._timeoutTimer.setSingleShot(True)
        self._timeoutTimer.timeout.connect(self.timeouted)
        self._timeoutTimer.start(timeout)

    @Slot()
    def timeouted(self) -> None:
        if self.hbIndicator is not None:
            self.hbIndicator.setFormat("")
            self.hbIndicator.setValue(0)
            self.hbIndicator.setInvertedAppearance(False)
        self.timestamp.setText(
            f"<font color='{Colors.ERROR.name()}'>- timeouted -</font>"
        )

    @Slot()
    def heartbeat(self, data: BaseMsgType) -> None:
        """Slot to connect to heartbeat data signal.

        Parameters
        ----------
        data : `object`
            Heartbeat event. As only private fields are used, can be any
            salobj. But needs to be received at least once per second."""
        v = data.private_seqNum % 3
        if self.hbIndicator is not None:
            if v in (0, 1):
                self.hbIndicator.setValue(1)
                self.hbIndicator.setInvertedAppearance(v == 1)
            else:
                self.hbIndicator.setValue(2)

            self.hbIndicator.setFormat(f"{data.private_seqNum % int(1e12):012d}")

        diff = data.private_rcvStamp - data.private_sndStamp
        if abs(diff) > self.difftime_error:
            self.timestamp.setText(
                datetime.fromtimestamp(data.private_sndStamp).strftime(
                    f"<font color='{Colors.ERROR.name()}'>%H:%M:%S.%f ({diff:0.3f})</font>"
                )
            )
        elif abs(diff) > self.difftime_warning:
            self.timestamp.setText(
                datetime.fromtimestamp(data.private_sndStamp).strftime(
                    f"<font color='{Colors.WARNING.name()}'>%H:%M:%S.%f ({diff:0.3f})</font>"
                )
            )
        else:
            self.timestamp.setText(
                datetime.fromtimestamp(data.private_sndStamp).strftime(
                    f"<font color='{Colors.OK.name()}'>%H:%M:%S.%f</font>"
                )
            )

        self._initTimer(2001)


class LogEventWarning(QLabel):
    """Display status of various evt_XXXWarnings. Shows either green OK if
    everything is fine, or yellow Warning on anyWarning.

    Parameters
    ----------
    signal : `Signal`
        Signal fired when logevent data changes.
    """

    def __init__(self, signal: Signal):
        super().__init__("---")
        signal.connect(self._logEvent)

    @Slot()
    def _logEvent(self, data: BaseMsgType) -> None:
        if data.anyWarning:
            self.setText("<font color='yellow'>Warning</font>")
        else:
            self.setText("<font color='green'>OK</font>")


class SimulationStatus(QLabel):
    """Displays if CSC is running in simulation mode.

    Parameters
    ----------
    comm : `lsst.ts.m1m3.salobj.Remote`
        Remote used for communciation with SAL/DDS CSC.

    """

    def __init__(self, comm: MetaSAL):
        super().__init__("--")
        try:
            comm.simulationMode.connect(self.simulationMode)
        except AttributeError:
            # simulationMode needs to be subscribed from remote
            self.setText(f"{comm.remote.salinfo.name} simulationMode missing")

    @Slot()
    def simulationMode(self, data: BaseMsgType) -> None:
        self.setText(
            f"<font color='{Colors.OK.name()}'>HW</font>"
            if data.mode == 0
            else f"<font color='{Colors.ERROR.name()}'>SIM</font>"
        )


class DockWindow(QDockWidget):
    """Widget transforming to Window when floated. Window can be maximized,
    placed better than floating dock.

    Parameters
    ----------
    title : `str`
        Dock title and object name.
    """

    def __init__(self, title: str):
        super().__init__(title)
        self.setObjectName(title)
        self.topLevelChanged.connect(self._topLevelChanged)

    @Slot()
    def _topLevelChanged(self, topLevel: bool) -> None:
        if topLevel:
            self.setWindowFlags(Qt.Window)
        self.show()
