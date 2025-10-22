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

from PySide6.QtCore import QCommandLineOption, QCommandLineParser, QMargins, QRect
from PySide6.QtWidgets import QApplication, QMainWindow
from qasync import QEventLoop

from ... import __version__
from ...salcomm import MetaSAL
from .splash_screen import SplashScreen


class Application:
    """cRIO GUI application class. Parses command line arguments. Runs
    application including splash screen (can be disabled by command line
    option). Splash screen is shown during SAL initialization.

    Attributes
    ----------
    eui : `QMainWindow`
        Main application window.
    parser : `QCommandLineParser`
        Command line argument parser.

    Methods
    -------
    process_command_line(self, parser: QCommandLineParser) -> None
        Called to process command line arguments collected by application.

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

    def __init__(
        self,
        eui_class: type[QMainWindow],
        *options: QCommandLineOption,
        **arguments: tuple[str, str],
    ):
        self._eui_class = eui_class
        self._app = QApplication(sys.argv)
        self._app.setApplicationVersion(__version__)

        self.parser = QCommandLineParser()
        self.parser.addHelpOption()
        self.parser.addVersionOption()

        no_splash = QCommandLineOption(["n", "no-splash"], "don't show splash screen")
        self.parser.addOption(no_splash)

        sal_info = QCommandLineOption(
            ["s", "SAL-info"],
            "show SAL info (including methods checksums) and exits",
        )

        resize = QCommandLineOption(["r", "resize"], "resize to small size")
        self.parser.addOption(resize)

        self.parser.addOption(sal_info)

        self.parser.addOptions(options)

        for name, options in arguments.items():
            self.parser.addPositionalArgument(name, *options)

        self.parser.process(self._app)

        self._loop = QEventLoop(self._app)
        asyncio.set_event_loop(self._loop)

        self._comms_args: list[SplashScreen.CommArgs] = []
        self._sal_info = self.parser.isSet(sal_info)
        self._splash = not (self.parser.isSet(no_splash))
        self._resize = self.parser.isSet(resize)
        self.eui: QMainWindow | None = None

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

    def process_command_line(self) -> None:
        """Called to process command line arguments. Shall be overridden in
        children, if custom command line processing is desired. Use self.parser
        to access command line parser."""
        pass

    def run(self) -> None:
        """Runs the application. Creates splash screen, display it if
        requested. Creates and display main window after SAL/DDS is
        initialized.
        """

        class AppSplashScreen(SplashScreen):
            def started(splash, *comms: MetaSAL) -> None:  # noqa: N805
                eui = self._eui_class(*comms)
                splash.finish(self.eui)

                screen_size = eui.screen().size()
                eui_rect = eui.frameGeometry()

                def rect_str(r: QRect) -> str:
                    return f"({r.left()},{r.top()},{r.right()},{r.bottom()})"

                if self._resize:
                    eui.move(50, 50)
                    eui.resize(1000, 700)
                    print(f"Window resized to {rect_str(eui.frameGeometry())}, as requested.")
                elif (
                    eui_rect.top() < 0
                    or eui_rect.left() < 0
                    or eui_rect.bottom() > screen_size.height()
                    or eui_rect.right() > screen_size.width()
                ):
                    new_size = screen_size.shrunkBy(QMargins(50, 50, 50, 50))
                    eui.move(50, 50)
                    eui.resize(new_size)
                    print(f"Window moved from {rect_str(eui_rect)} to {rect_str(eui.frameGeometry())}.")
                else:
                    print(
                        f"Window size {rect_str(eui_rect)}, "
                        f"screen size ({screen_size.width()},{screen_size.height()})."
                    )

                eui.show()
                self.eui = eui
                # re-emit signals from history
                for c in comms:
                    c.reemit_remote()

                assert self.eui is not None
                self.process_command_line()

                if self._sal_info:
                    for c in splash.comms:
                        for m in dir(c.remote):
                            if m.startswith("cmd_") or m.startswith("tel_") or m.startswith("evt_"):
                                ti = getattr(c.remote, m).topic_info
                                print(ti.component_name, ti.sal_name, ti.get_revcode())
                    self._app.quit()

        splash = AppSplashScreen(*self._comms_args, show=self._splash)
        if self._splash:
            splash.show()

        def handler(signum: int, frame: typing.Any) -> None:
            print(f"Catching signal {signum}, exiting")
            self._loop.call_soon(splash.stop)
            self._loop.call_soon(self._app.closeAllWindows)

        signals = [signal.SIGINT, signal.SIGTERM]
        if sys.platform == "linux":
            signals += [signal.SIGHUP]
        for signum in signals:
            signal.signal(signum, handler)

        # Run the main Qt loop
        with self._loop:
            self._loop.run_forever()
