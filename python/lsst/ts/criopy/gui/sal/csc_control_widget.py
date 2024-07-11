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


from lsst.ts import salobj
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QButtonGroup, QPushButton, QVBoxLayout, QWidget
from qasync import asyncSlot

from ...salcomm import MetaSAL, command


class CSCControlWidget(QWidget):
    """Generic control widget. Displays buttons to control CSC states. Buttons
    text is changed as CSC enters different states.

    Return value of the get_state_buttons_map method provides an array filled
    with text for active buttons. Buttons for None entries keep text, but are
    disabled.

    The widget is usually connected to summaryState topic and summaryState
    field. Other topics/fields can be specified in constructor.

    Parameters
    ----------
    comm : `MetaSAL`
        SAL object to receive data / run the commands.
    buttons : `[str]`, optional
        Text for defaults buttons.
    extra_Buttons_commands : `dict[str, str]', optional
        Commands for buttons texts.
    state_signal : `str`, optional
        Topic providing CSC state. Defaults to summaryState.
    state_field : `str`, optional
        Field inside topic providing CSC state. Defaults to summaryState.
    """

    TEXT_START = "&Start"
    """Constants for button titles. Titles are used to select command send to
    SAL."""
    TEXT_ENABLE = "&Enable"
    TEXT_DISABLE = "&Disable"
    TEXT_STANDBY = "&Standby"
    TEXT_EXIT_CONTROL = "&Exit Control"

    def __init__(
        self,
        comm: MetaSAL,
        buttons: list[str] = [TEXT_START, TEXT_ENABLE, TEXT_STANDBY],
        extra_buttons_commands: dict[str, str] = {},
        state_signal: str = "summaryState",
        state_field: str = "summaryState",
    ):
        super().__init__()

        self.comm = comm
        self.buttons_commands = {
            self.TEXT_START: "start",
            self.TEXT_ENABLE: "enable",
            self.TEXT_DISABLE: "disable",
            self.TEXT_STANDBY: "standby",
            self.TEXT_EXIT_CONTROL: "exitControl",
        }
        self.buttons_commands.update(extra_buttons_commands)

        self.__last_enabled: None | list[bool] = None

        self.buttons_group = QButtonGroup(self)
        self.buttons_group.buttonClicked.connect(self.csc_button_clicked)

        self.setLayout(QVBoxLayout())

        for text in buttons:
            self.add_csc_button(text)

        self.state_field = state_field
        getattr(self.comm, state_signal).connect(self.csc_state)

    def add_csc_button(self, text: str, command: None | str = None) -> QPushButton:
        """Adds button.

        Parameters
        ----------
        text : `str`
            Button text.
        command : `str`, optional
            Command associated with button.

        Returns
        -------
        button : `QPushButton`
            Newly added button.

        """
        button = QPushButton(text)
        button.setEnabled(False)
        self.buttons_group.addButton(button)
        self.layout().addWidget(button)
        if command is None:
            if text not in self.buttons_commands.keys():
                raise RuntimeError(f"Command for {text} not defined.")
        else:
            self.buttons_commands[text] = command
        return button

    def insert_widget(self, widget: QWidget, index: int = -1) -> None:
        """Inserts a widget into control buttons.

        Parameters
        ----------
        widget: QWidget
            Widget to be inserted at given index.
        index: `int`, optional
            Index to insert the widget. Defaults to -1, end of current button
            layout.
        """
        self.layout().insertWidget(index, widget)

    def disable_all_buttons(self) -> None:
        if self.__last_enabled is None:
            self.__last_enabled = []
            for b in self.buttons_group.buttons():
                self.__last_enabled.append(b.isEnabled())
                b.setEnabled(False)

    def restore_enabled(self) -> None:
        if self.__last_enabled is None:
            return
        bi = 0
        for b in self.buttons_group.buttons():
            b.setEnabled(self.__last_enabled[bi])
            bi += 1

        self.__last_enabled = None

    @asyncSlot()
    async def csc_button_clicked(self, bnt: QPushButton) -> None:
        text = bnt.text()
        cmd = self.get_buttons_command(text)
        self.disable_all_buttons()
        executed = await command(self, getattr(self.comm.remote, "cmd_" + cmd))
        if not (executed):
            self.restore_enabled()

    def get_buttons_command(self, text: str) -> str:
        return self.buttons_commands[text]

    def get_state_buttons_map(self, state: int) -> list[str | None]:
        """Returns button map for given state. This method is called on every
        CSC state change to retrieve buttons text.

        Parameters
        ----------
        state: `int`
           Current CSC state.

        Returns
        -------
        buttons : `[str | None]`
           Text for buttons. Index corresponds to order add_csc_button calls.
           If None is used, the button is disabled.
        """
        states_map: dict[int, list[str | None]] = {
            salobj.State.STANDBY: [
                self.TEXT_START,
                None,
                self.TEXT_EXIT_CONTROL,
            ],
            salobj.State.DISABLED: [
                None,
                self.TEXT_ENABLE,
                self.TEXT_STANDBY,
            ],
            salobj.State.ENABLED: [
                None,
                self.TEXT_DISABLE,
                None,
            ],
            salobj.State.FAULT: [None, None, self.TEXT_STANDBY],
            salobj.State.OFFLINE: [None, None, None],
        }
        return states_map[state]

    @Slot()
    def csc_state(self, data: salobj.BaseMsgType) -> None:
        # text mean button is enabled and given text shall be displayed. None
        # for disabled buttons.
        self.__last_enabled = None

        db_set = True
        try:
            state_data = self.get_state_buttons_map(getattr(data, self.state_field))
        except AttributeError as attrib_error:
            print(f"Cannot access {self.state_field} in {data}: {str(attrib_error)}")
            return

        try:
            for bi, b in enumerate(self.buttons_group.buttons()):
                text = state_data[bi]
                if text is None:
                    b.setEnabled(False)
                    b.setDefault(False)
                else:
                    b.setText(text)
                    b.setEnabled(True)
                    b.setDefault(db_set)
                    db_set = False
        except KeyError:
            print(
                f"Unhandled summary state {str(salobj.State(data.summaryState))} - {data.summaryState}"
            )
