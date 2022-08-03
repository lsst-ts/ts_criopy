# This file is part of M1M3 SS GUI.
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

from PySide2.QtCore import Slot, QTimer, Qt
from PySide2.QtWidgets import (
    QFrame,
    QWidget,
    QLabel,
    QVBoxLayout,
    QProgressBar,
    QSizePolicy,
    QDockWidget,
    QPushButton,
)
from PySide2.QtGui import QPalette
import astropy.units as u
from datetime import datetime

from .EventWindow import EventWindow

__all__ = [
    "VLine",
    "DataLabel",
    "UnitLabel",
    "DataUnitLabel",
    "Force",
    "Moment",
    "Mm",
    "Arcsec",
    "Ampere",
    "Percent",
    "Volt",
    "RPM",
    "PressureInBar",
    "PressureInmBar",
    "Hours",
    "Seconds",
    "KiloWatt",
    "DataDegC",
    "ArcsecWarning",
    "MmWarning",
    "OnOffLabel",
    "PowerOnOffLabel",
    "ErrorLabel",
    "WarningLabel",
    "WarningButton",
    "InterlockOffLabel",
    "StatusLabel",
    "Clipped",
    "Heartbeat",
    "LogEventWarning",
    "SimulationStatus",
    "DockWindow",
]

WARNING = "#FF6700"
"""Warning color"""


class VLine(QFrame):
    """A simple Vertical line."""

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


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

    def __init__(self, signal=None, field=None):
        super().__init__("---")
        if signal is not None:
            self._field = field
            signal.connect(self._data)
        if field is not None:
            self.setObjectName(field)
            self.setCursor(Qt.PointingHandCursor)

    def __copy__(self):
        return DataLabel()

    @Slot(map)
    def _data(self, data):
        self.setValue(getattr(data, self._field))

    def setValue(self, value):
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
    fmt : `str`, optional
        Format string. See Python formatting function for details. Defaults to
        'd' for decimal number.
    unit : `astropy.units or str`, optional
        Variable unit. Default is None - no unit. Can be specified as string.
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
        text). Default is None - no color coded error value."""

    def __init__(
        self, fmt="d", unit=None, convert=None, is_warn_func=None, is_err_func=None
    ):
        super().__init__("---")
        self.fmt = fmt
        if type(unit) == str:
            unit = u.Unit(unit)
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
        }
        try:
            self.unit_name = aliases[self.unit_name]
        except KeyError:
            pass

        self.unit_name = " " + self.unit_name

        self.unit = unit
        self.convert = convert
        self.is_warn_func = is_warn_func
        self.is_err_func = is_err_func

    def __copy__(self):
        return UnitLabel(
            self.fmt, self.unit, self.convert, self.is_warn_func, self.is_err_func
        )

    def setValue(self, value):
        """Sets value. Transformation and formatting is done according to unit,
        convert and fmt constructor arguments.

        Parameters
        ----------
        value : `float`
            Current (=to be displayed) variable value.
        """
        text = f"{(value * self.scale):{self.fmt}}{self.unit_name}"
        if self.is_err_func is not None and self.is_err_func(value):
            self.setText("<font color='red'>" + text + "</font>")
        elif self.is_warn_func is not None and self.is_warn_func(value):
            self.setText(f"<font color='{WARNING}'>{text}</font>")
        else:
            self.setText(text)


# TODO: tried to combine UnitLabel and DataLabel directly, but failed.  the
# closest I was able to get was probably using **kwargs for DataLabel and
# UnitLabel, and keep Python super().__init__(... call
class DataUnitLabel(UnitLabel):
    """Combines DataLabel and UnitLabel. Parameters specify signal and field
    name (as in DataLabel) and display options (as in UnitLabel).

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
        signal=None,
        field=None,
        fmt="d",
        unit=None,
        convert=None,
        is_warn_func=None,
        is_err_func=None,
    ):
        super().__init__(fmt, unit, convert, is_warn_func, is_err_func)
        if signal is not None:
            self._field = field
            signal.connect(self._data)
        if field is not None:
            self.setObjectName(field)
            self.setCursor(Qt.PointingHandCursor)

    @Slot(map)
    def _data(self, data):
        self.setValue(getattr(data, self._field))


class Force(UnitLabel):
    """Displays force in N (Newtons).

    Parameters
    ----------
    fmt : `str`, optional
        Float formatting. Defaults to .02f.
    """

    def __init__(self, fmt=".02f"):
        super().__init__(fmt, u.N)


class Moment(UnitLabel):
    """Displays moment in N*m (Newtons meters).

    Parameters
    ----------
    fmt : `str`, optional
        Float formatting. Defaults to .02f.
    """

    def __init__(self, fmt=".02f"):
        super().__init__(fmt, u.N * u.m)


class Mm(UnitLabel):
    """Display meters as mm (millimeters).

    Parameters
    ----------
    fmt : `str`, optional
        Float formatting. Defaults to .04f.
    """

    def __init__(self, fmt=".04f", is_warn_func=None, is_err_func=None):
        super().__init__(fmt, u.meter, u.mm, is_warn_func, is_err_func)


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
        fmt=".04f",
        warning_threshold=4 * u.um.to(u.meter),
        error_threshold=8 * u.um.to(u.meter),
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

    def __init__(self, fmt="0.02f", is_warn_func=None, is_err_func=None):
        super().__init__(fmt, u.deg, u.arcsec, is_warn_func, is_err_func)


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

    def __init__(self, signal=None, field=None, fmt="0.02f"):
        super().__init__(signal, field, fmt, u.A)


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

    def __init__(self, signal=None, field=None, fmt="0.02f"):
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

    def __init__(self, signal=None, field=None, fmt="0.02f"):
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

    def __init__(self, signal=None, field=None, fmt=".0f"):
        super().__init__(signal, field, fmt, u.Unit("min^-1"))


class PressureInBar(DataLabel):
    """Display pressure in bar and psi"""

    def __init__(self, signal=None, field=None):
        super().__init__(signal, field)
        self.unit_name = "bar"

    def setValue(self, value):
        psi = value * 14.5038
        self.setText(f"{value:.04f} bar ({psi:.02f} psi)")


class PressureInmBar(DataLabel):
    def __init__(self, signal=None, field=None):
        super().__init__(signal, field)
        self.unit_name = "mbar"  # this is only for display

    def setValue(self, value):
        mbar = value * u.mbar
        bar = (mbar).to(u.bar).value
        psi = mbar.to(u.imperial.psi).value
        self.setText(f"{bar:.04f} bar ({psi:.02f} psi)")


class Hours(DataUnitLabel):
    def __init__(self, field=None):
        super().__init__(None, field, ".0f", u.h)


class Seconds(DataUnitLabel):
    def __init__(self, field=None):
        super().__init__(None, field, ".0f", u.s)


class KiloWatt(DataUnitLabel):
    def __init__(self, signal=None, field=None):
        super().__init__(signal, field, ".01f", u.kW)


class DataDegC(DataUnitLabel):
    def __init__(self, signal=None, field=None, fmt=".02f"):
        super().__init__(signal, field, fmt, u.deg_C)


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
        fmt="0.02f",
        warning_threshold=0.73 * u.arcsec.to(u.deg),
        error_threshold=1.45 * u.arcsec.to(u.deg),
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

    def __init__(self, signal=None, field=None):
        super().__init__(signal, field)

    def __copy__(self):
        return OnOffLabel()

    def setValue(self, value):
        """Sets formatted value. Color codes On (red)/Off (green).

        Parameters
        ----------
        value : `bool`
            Current (=to be displayed) variable value. True means warning/error
            is raised.
        """
        if value:
            self.setText("<font color='red'>On</font>")
        else:
            self.setText("<font color='green'>Off</font>")


class PowerOnOffLabel(DataLabel):
    """Displays on/off power state"""

    def __init__(self, signal=None, field=None):
        super().__init__(signal, field)

    def __copy__(self):
        return PowerOnOffLabel()

    def setValue(self, value):
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

    def __init__(self, signal=None, field=None):
        super().__init__(signal, field)

    def __copy__(self):
        return ErrorLabel()

    def setValue(self, value):
        """Sets formatted value. Color codes ERROR (red)/OK (green).

        Parameters
        ----------
        value : `bool`
            Current (=to be displayed) variable value. True means error.
        """
        if value:
            self.setText("<font color='red'>ERROR</font>")
        else:
            self.setText("<font color='green'>OK</font>")


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

    def __init__(self, signal=None, field="anyWarning"):
        super().__init__(signal, field)

    def __copy__(self):
        return WarningLabel()

    def setValue(self, value):
        """Sets formatted value. Color codes WARNING (red)/OK (green).

        Parameters
        ----------
        value : `bool`
            Current (=to be displayed) variable value. True means warning.
        """
        if value:
            self.setText("<font color='red'>WARNING</font>")
        else:
            self.setText("<font color='green'>OK</font>")


class WarningButton(QPushButton):
    """Displays WARNING/OK button. When clicked, displays window with values in
    the signal. Button is color-coded (red for problems, green for OK values).

    Parameters
    ----------
    comm : `SALComm`
        SALComm object representing the signals
    topic : `str`
        Topic name. Should be event/telemetry name without leading evt_ (for
        events).
    field : `str`, optional
        Field from topic used to display button state. Defaults to anyWarning
    """

    def __init__(self, comm, topic, field="anyWarning"):
        super().__init__("---")
        self.comm = comm
        self._topic = topic
        self._field = field
        getattr(comm, topic).connect(self._data)
        self.window = None
        self.clicked.connect(self._showWindow)

    @Slot(map)
    def _data(self, data):
        self.setValue(getattr(data, self._field))

    def _showWindow(self):
        if self.window is None:
            self.window = EventWindow(self.comm, self._topic)
        self.window.show()

    def setValue(self, value):
        """Sets formatted value. Color codes WARNING (red)/OK (green).

        Parameters
        ----------
        value : `bool`
            Current (=to be displayed) variable value. True means warning.
        """
        pal = self.palette()
        if value:
            self.setText("WARNING")
            pal.setColor(QPalette.Button, Qt.red)
        else:
            self.setText("OK")
            pal.setColor(QPalette.Button, Qt.green)
        self.setPalette(pal)


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

    def __init__(self, signal=None, field="anyWarning"):
        super().__init__("---")
        if signal is not None:
            self._field = field
            signal.connect(self._data)

    @Slot(map)
    def _data(self, data):
        self.setValue(getattr(data, self._field))

    def setValue(self, value):
        """Sets formatted value. Color codes WARNING (red)/OK (green).

        Parameters
        ----------
        interlockOff : `bool`
            Current interlock off state. True means interlock is locked
            (=PROBLEM).
        """
        if value:
            self.setText("<font color='red'>PROBLEM</font>")
        else:
            self.setText("<font color='green'>OK</font>")


class StatusLabel(QLabel):
    """Displays OK/Error status."""

    def __init__(self):
        super().__init__("---")

    def __copy__(self):
        return StatusLabel()

    def setValue(self, value):
        """Sets formatted value. Color codes Error (red)/OK (green).

        Parameters
        ----------
        value : `bool`
            Current (=to be displayed) variable value. True means OK.
        """
        if value:
            self.setText("<font color='green'>OK</font>")
        else:
            self.setText("<font color='red'>Error</font>")


class Clipped(QLabel):
    "Display clipped/not clipped"

    def __init__(self, force):
        super().__init__()
        self._force = force

    def setClipped(self, clipped):
        if clipped:
            self.setText(f"<font color='red'>{self._force} forces clipped</font>")
        else:
            self.setText(f"<font color='green'>{self._force} forces not clipped</font>")


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
       from CustomLabels import Heartbeat

       ...

       comm = SALComm.create("<subsystem>": None)

       ...

       hbWidget = Heartbeat()
       comm.<subsystem>.heartbeat.connect(hbWIdget.heartbeat)
    """

    difftime_error = 0.5
    difftime_warning = 0.01

    def __init__(self, parent=None, indicator=True):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setMargin(0)

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

        self._timeoutTimer = None
        self._initTimer(3000)

    def _initTimer(self, timeout=2001):
        if self._timeoutTimer is not None:
            self._timeoutTimer.stop()

        self._timeoutTimer = QTimer(self)
        self._timeoutTimer.setSingleShot(True)
        self._timeoutTimer.timeout.connect(self.timeouted)
        self._timeoutTimer.start(timeout)

    @Slot()
    def timeouted(self):
        if self.hbIndicator is not None:
            self.hbIndicator.setFormat("")
            self.hbIndicator.setValue(0)
            self.hbIndicator.setInvertedAppearance(False)
        self.timestamp.setText("<font color='red'>- timeouted -</font>")

    @Slot(map)
    def heartbeat(self, data):
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
                    f"<font color='red'>%H:%M:%S.%f ({diff:0.3f})</font>"
                )
            )
        elif abs(diff) > self.difftime_warning:
            self.timestamp.setText(
                datetime.fromtimestamp(data.private_sndStamp).strftime(
                    f"<font color='{WARNING}'>%H:%M:%S.%f ({diff:0.3f})</font>"
                )
            )
        else:
            self.timestamp.setText(
                datetime.fromtimestamp(data.private_sndStamp).strftime(
                    "<font color='green'>%H:%M:%S.%f</font>"
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

    def __init__(self, signal):
        super().__init__("---")
        signal.connect(self._logEvent)

    @Slot(map)
    def _logEvent(self, data):
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

    def __init__(self, comm):
        super().__init__("--")
        try:
            comm.simulationMode.connect(self.simulationMode)
        except AttributeError:
            # simulationMode needs to be subscribed from remote
            self.setText(f"{comm.remote.salinfo.name} simulationMode missing")

    @Slot(map)
    def simulationMode(self, data):
        self.setText(
            "<font color='green'>HW</font>"
            if data.mode == 0
            else "<font color='red'>SIM</font>"
        )


class DockWindow(QDockWidget):
    """Widget transforming to Window when floated. Window can be maximized,
    placed better than floating dock.

    Parameters
    ----------
    title : `str`
        Dock title and object name.
    """

    def __init__(self, title):
        super().__init__(title)
        self.setObjectName(title)
        self.topLevelChanged.connect(self._topLevelChanged)

    @Slot(bool)
    def _topLevelChanged(self, topLevel):
        if topLevel:
            self.setWindowFlags(Qt.Window)
        self.show()
