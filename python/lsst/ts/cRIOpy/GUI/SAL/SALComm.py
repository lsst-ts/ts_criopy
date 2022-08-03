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

# Generated from MTM1M3_Events, MTM1M3_Telemetry and MTMount_Telemetry
from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QMessageBox
from lsst.ts.salobj import Domain, Remote, base
from lsst.ts.salobj.topics import RemoteTelemetry, RemoteEvent

import asyncio

__all__ = ["create", "SALCommand", "SALListCommand"]


def _filterEvtTel(m):
    return m.startswith("tel_") or m.startswith("evt_")


class MetaSAL(type(QObject)):
    """Metaclass for Qt<->SAL/DDS glue class. Creates Qt Signal objects for all
    read topics. Remote arguments are read from class variable _args. SALObj
    remote is accessible through 'remote' class variable."""

    def __new__(cls, classname, bases, dictionary):
        dictionary["domain"] = Domain()

        if dictionary["_manual"] is None:
            dictionary["remote"] = Remote(dictionary["domain"], **dictionary["_args"])
        else:
            dictionary["remote"] = Remote(
                dictionary["domain"],
                start=False,
                exclude=dictionary["_manual"].keys(),
                **dictionary["_args"],
            )
            for name, args in dictionary["_manual"].items():
                if name in dictionary["remote"].salinfo.telemetry_names:
                    tel = RemoteTelemetry(dictionary["remote"].salinfo, name, **args)
                    setattr(dictionary["remote"], tel.attr_name, tel)
                elif name in dictionary["remote"].salinfo.event_names:
                    evt = RemoteEvent(dictionary["remote"].salinfo, name, **args)
                    setattr(dictionary["remote"], evt.attr_name, tel)
                else:
                    print(f"Unknown manual {name} - is not a telemetry or event topics")

            dictionary["remote"].start_task = asyncio.create_task(
                dictionary["remote"].start()
            )

        for m in filter(
            lambda m: m.startswith("tel_") or m.startswith("evt_"),
            dir(dictionary["remote"]),
        ):
            dictionary[m[4:]] = Signal(map)

        def connect_callbacks(self):
            for m in filter(_filterEvtTel, dir(self.remote)):
                getattr(self.remote, m).callback = getattr(self, m[4:]).emit

        def reemit_remote(self):
            """Re-emits all telemetry and event data from a single remote as Qt
            messages.
            """
            for m in filter(_filterEvtTel, dir(self.remote)):
                data = getattr(self.remote, m).get()
                if data is not None:
                    getattr(self, m[4:]).emit(data)

        async def close(self):
            await self.remote.close()
            await self.domain.close()

        newclass = super(MetaSAL, cls).__new__(cls, classname, bases, dictionary)

        # creates class methods
        setattr(newclass, connect_callbacks.__name__, connect_callbacks)
        setattr(newclass, reemit_remote.__name__, reemit_remote)
        setattr(newclass, close.__name__, close)

        return newclass


def create(name, manual=None, **kwargs):
    """Creates SALComm instance for given remote(s). The returned object
    contains PySide2.QtCore.Signal class variables. Those signals are emitted
    when SAL callback occurs, effectively linking SAL/DDS and Qt world. Signals
    can be connected to multiple Qt slots to process the incoming data.

    Class variable named "remote" is instance of lsst.ts.salobj.Remote. This
    can be used to start commands (available with `cmd_` prefix).

    Parameters
    ----------
    name : `str`
        Remote name.
    manual : `hash`
        Events and telemetry topics created with optional arguments. Keys are
        events and telemetry names, values is a hash of additional arguments.

    **kwargs : `dict`
        Optional parameters passed to remote.

    Usage
    -----

    .. code-block:: python
       import SALComm

       import sys
       from asyncqt import QEventLoop, asyncSlot
       from PySide2.QtWidgets import QApplication, QPushButton

       app = QApplication(sys.argv)
       loop = QEventLoop(app)
       asyncio.set_event_loop(loop)

       my_mount = SALComm.create("MTMount")

       # tel_data will be created with 400 items queue
       my_vms = SALComm.create(
           "MTVMS",
           index=1,
           manual={"data" : {"queue_len" : 400}}
       )

       @Slot(map)
       def update_labels_azimuth(data):
           ...

       @Slot(map)
       def update_data(data):
           ...

       my_mount.azimuth.connect(update_labels_azimuth)
       my_vms.data.connect(update_data)

       ...

       @asyncSlot()
       async def startIt():
           await my_sal.remote.cmd_start.set_start(settingsToApply="Default")

       runIt = QPushButton("Run it!")
       runIt.clicked.connect(startIt)

       ...

       # should trigger callbacks with historic data
       with loop:
           loop.run_forever()
    """

    class SALComm(QObject, metaclass=MetaSAL):
        """
        SAL proxy. Set callback to emit Qt signals.
        """

        _args = kwargs
        _args["name"] = name
        _manual = manual

        def __init__(self):
            super().__init__()

            self.connect_callbacks()

    return SALComm()


def warning(parent, title, description):
    """Creates future with QMessageBox. Enables use of QMessageBox with
    asyncqt/asyncio. Mimics QMessageBox.warning behaviour - but QMessageBox
    cannot be used, as it blocks Qt loops from executing (as all modal dialogs
    does).

    Parameters
    ----------
    parent : `QtWidget`
        Parent widget.
    title : `str`
        Message window title.
    description : `str`
        Descrption of warning occured.
    """

    future = asyncio.Future()
    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(description)
    dialog.setIcon(QMessageBox.Warning)
    dialog.finished.connect(lambda r: future.set_result(r))
    dialog.open()
    return future


def SALCommand(cmd):
    """Decorator to run a command and display error dialog when in troubles. To
    be used in QtWidget child method. Decorates a function call, pass supplied
    arguments to SAL/DDS command call.

    Parameters
    ----------
    cmd : `RemoteCommand`
        SAL command
    **kwargs : `dict`
        Arguments passed to SAL command.

    Usage
    -----

    Calling await runTheMachine will start command and wait for its completion.
    QMessageBox with details will be shown on errors.

    .. code-block:: python
        class MyCommandClass(QWidget):
           def __init__(self, csc):
               super().__init__()
               self.csc = csc

               button = QPushButton("Run!")
               button.clicked.connect(self.runIt)

           ...

           @asyncSlot()
           async def runIt(self):
               await self.runTheMachine(speed=1, angle=120)

           @SALCommand
           def runTheMachine(self, **kwargs):
               return self.csc.remote.runTheMachine
    """

    async def wrapper(self, **kwargs):
        called = cmd(self)
        try:
            await called.set_start(**kwargs)
        except base.AckError as ackE:
            warning(
                self,
                f"Error executing {called.name}",
                f"Executing SAL/DDS command <i>{called.name}({kwargs}</i>):<br/>{ackE.ackcmd.result}",
            )
        except RuntimeError as rte:
            warning(
                self,
                f"Error executing {called.name}",
                f"Executing SAL/DDS command <b>{called.name}</b>(<i>{kwargs}</i>):<br/>{str(rte)}",
            )

    return wrapper


def SALListCommand(cmd):
    """Decorator to run commands and display error dialog when in troubles. To
    be used in QtWidget child method. Decorates a function call, pass supplied
    arguments to SAL/DDS command call.

    Parameters
    ----------
    comms : `[SALComm]`
        List of SALComm objects. The command will be executed for each member
        of the list.
    cmd : `str`
        SAL command name
    **kwargs : `dict`
        Arguments passed to SAL command.

    Usage
    -----

    Calling await runTheMachine will start command and wait for its completion.
    QMessageBox with details will be shown on errors.

    .. code-block:: python
        class MyCommandClass(QWidget):
           def __init__(self):
               super().__init__()
               self.cscs = [SALComm(
                   'MTVMS',
                   index=1),
                   SALComm('MTVMS', index=2
               )]

               button = QPushButton("Run!")
               button.clicked.connect(self.runIt)

           ...

           @asyncSlot()
           async def runIt(self):
               await self.runTheMachine(speed=1, angle=120)

           @SALListCommand("runTheMachine")
           def runTheMachine(self, **kwargs):
               return self.cscs
    """

    def wrapper(comms):
        async def wrapper_f(self, **kwargs):
            for comm in comms(self):
                try:
                    called = getattr(comm.remote, "cmd_" + cmd)
                    await called.set_start(**kwargs)
                except base.AckError as ackE:
                    warning(
                        self,
                        f"Error executing"
                        f" {comm.remote.salinfo.name}:{comm.remote.salinfo.index}"
                        f" {called.name}",
                        f"Executing SAL/DDS command"
                        f" <i>{called.name}"
                        f"({kwargs}</i>):<br/>{ackE.ackcmd.result}",
                    )
                except RuntimeError as rte:
                    warning(
                        self,
                        f"Error executing {comm.remote.salinfo.name}:{comm.remote.salinfo.index}"
                        f" {called.name}",
                        f"Executing SAL/DDS command <b>{called.name}"
                        f"</b>(<i>{kwargs}</i>):<br/>{str(rte)}",
                    )

        return wrapper_f

    return wrapper
