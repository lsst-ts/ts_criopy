# This file is part of cRIO GUI.
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

import asyncio
import signal
import sys
import typing

from PySide2.QtCore import QCommandLineOption, QCommandLineParser
from PySide2.QtWidgets import QApplication, QMainWindow
from qasync import QEventLoop

from ... import __version__
from ...salcomm import MetaSAL
from .splash_screen import SplashScreen


class Application:
    """cRIO GUI application class. Parses command line arguments. Runs
    application including splash screen (can be disabled by command line
    option). Splash screen is shown during SAL initialization.

    Parameters
    ----------
    eui_class : `class`
        Class, ideally child of QMainWindow, which will be instantiated after
        wait for SAL/DDS initialization. It's parameters are SAL created
        with add_comm method.

    Usage
    -----
    .. code-block:: python
       from lsst.ts.criopy.gui import Application


       class EUI(QMainWindow):
           ...

       if __name__ == "__main__":
           app = Application(EUI)
           app.add_comm("MTM1M3")
           app.add_comm("MTMount", include=["azimuth", "elevation"])
           app.add_comm("MTAirCompressor", index=2)
           app.run()
    """

    def __init__(self, eui_class: type[QMainWindow]):
        self._eui_class = eui_class
        self._app = QApplication(sys.argv)
        self._app.setApplicationVersion(__version__)

        parser = QCommandLineParser()
        parser.addHelpOption()
        parser.addVersionOption()

        noSplash = QCommandLineOption(["n", "no-splash"], "don't show splash screen")
        parser.addOption(noSplash)

        salInfo = QCommandLineOption(
            ["s", "SAL-info"],
            "show SAL info (including methods checksums) and exits",
        )
        parser.addOption(salInfo)

        parser.process(self._app)

        self._loop = QEventLoop(self._app)
        asyncio.set_event_loop(self._loop)

        self._comms: list[MetaSAL] = []
        self._comms_args: list[SplashScreen.CommArgs] = []
        self._sal_info = parser.isSet(salInfo)
        self._splash = not (parser.isSet(noSplash))
        self._eui: typing.Any | None = None

    def add_comm(
        self,
        name: str,
        manual: dict[str, typing.Any] | None = None,
        **kwargs: typing.Any,
    ) -> None:
        """Adds SALComm object to parameters of QMainWindow class.

        Parameters
        ----------
        name : `str`
            Remote name.
        manual : `hash`
            Events and telemetry topics created with optional arguments. Keys
            are events and telemetry names, values is a hash of additional
            arguments.
        **kwargs : `dict`
            Optional parameters passed to remote.
        """
        self._comms_args.append(SplashScreen.CommArgs(name, manual, kwargs))

    def run(self) -> None:
        """Runs the application. Creates splash screen, display it if
        requested. Creates and display main window after SAL/DDS is
        initialized."""

        if self._sal_info:
            for c in self._comms:
                for m in dir(c.remote):
                    if (
                        m.startswith("cmd_")
                        or m.startswith("tel_")
                        or m.startswith("evt_")
                    ):
                        print(getattr(c.remote, m).dds_name)
            sys.exit(0)

        class AppSplashScreen(SplashScreen):
            def started(splash, *comms: MetaSAL) -> None:  # noqa: N805
                eui = self._eui_class(*comms)
                splash.finish(self._eui)
                eui.show()
                self._eui = eui
                # re-emit signals from history
                for c in comms:
                    c.reemit_remote()

        splash = AppSplashScreen(*self._comms_args, show=self._splash)
        if self._splash:
            splash.show()

        def handler(signum: int, frame: typing.Any) -> None:
            print(f"Catching signal {signum}, exiting")
            self._loop.call_soon(splash.stop)
            self._loop.call_soon(self._app.closeAllWindows)

        for signum in [signal.SIGINT, signal.SIGHUP, signal.SIGTERM]:
            signal.signal(signum, handler)

        # Run the main Qt loop
        with self._loop:
            self._loop.run_forever()
