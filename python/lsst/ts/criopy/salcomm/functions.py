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

import asyncio
import typing

from lsst.ts.salobj import base
from PySide6.QtWidgets import QMessageBox, QWidget

from .meta_sal import MetaSAL

__all__ = ["warning", "command", "command_group"]


def warning(parent: QWidget, title: str, description: str) -> asyncio.Future:
    """Creates future with QMessageBox. Enables use of QMessageBox with
    qasync/asyncio. Mimics QMessageBox.warning behaviour - but QMessageBox
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

    future: asyncio.Future = asyncio.Future()
    dialog = QMessageBox(parent)
    dialog.setWindowTitle(title)
    dialog.setText(description)
    dialog.setIcon(QMessageBox.Warning)
    dialog.finished.connect(lambda r: future.set_result(r))
    dialog.open()
    return future


async def command(parent: QWidget, cmd: typing.Any, **kwargs: typing.Any) -> bool:
    """

    Parameters
    ----------
    parent : `QWidget`
        Parent widget, needed to display error messages.
    cmd : `RemoteCommand`
        SAL command
    **kwargs : `dict`
        Arguments passed to SAL command.
    """

    try:
        await cmd.set_start(**kwargs)
        return True
    except base.AckError as ackE:
        warning(
            parent,
            f"Error executing {cmd.name}",
            "Executing SAL/DDS command"
            f" <i>{cmd.name}({kwargs}</i>):<br/>{ackE.ackcmd.result}",
        )
    except RuntimeError as rte:
        warning(
            parent,
            f"Error executing {cmd.name}",
            "Executing SAL/DDS command"
            f" <b>{cmd.name}</b>(<i>{kwargs}</i>):<br/>{str(rte)}",
        )
    return False


async def command_group(
    parent: QWidget, comms: list[MetaSAL], cmdName: str, **kwargs: typing.Any
) -> None:
    """
    Command a set of SAL remotes.

    Parameters
    ----------
    parent : `QWidget`
        Parent widget, needed to display error messages.
    comms : `[MetaSAL]`
        List of MetaSAL objects. The command will be executed for each member
        of the list.
    cmdName : `str`
        SAL command name
    **kwargs : `dict`
        Arguments passed to SAL command.
    """

    for comm in comms:
        try:
            cmd = getattr(comm.remote, "cmd_" + cmdName)
            await cmd.set_start(**kwargs)
        except base.AckError as ackE:
            warning(
                parent,
                "Error executing"
                f" {comm.remote.salinfo.name}:{comm.remote.salinfo.index}"
                f" {cmd.name}",
                "Executing SAL/DDS command"
                f" <i>{cmd.name}"
                f"({kwargs}</i>):<br/>{ackE.ackcmd.result}",
            )
        except RuntimeError as rte:
            warning(
                parent,
                "Error executing"
                f" {comm.remote.salinfo.name}:{comm.remote.salinfo.index}"
                f" {cmd.name}",
                f"Executing SAL/DDS command <b>{cmd.name}"
                f"</b>(<i>{kwargs}</i>):<br/>{str(rte)}",
            )
