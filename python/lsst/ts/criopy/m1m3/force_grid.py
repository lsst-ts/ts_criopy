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

from functools import partial

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget

from ..gui import FormatLabel
from ..gui.array_grid import AbstractColumn, ArrayFields, ArrayGrid

__all__ = ["Forces", "ForcesGrid", "PreclippedForces"]


class Forces(ArrayFields):
    """Class to display all six forces and moments components in ArrayGrid.

    Parameters
    ----------
    label : `str`
        Force label. Used for QLabel, inserted as the first item into grid.
    signal : `Signal`
        Signal issued when new data ara available.
    extra_widgets : `[QWidget]`, optional
        Widgets added to the end of the row/column. Passed to parent
        ArrayFields.
    """

    def __init__(
        self,
        label: str,
        signal: Signal,
        extra_widgets: list[QWidget] | None = None,
    ):
        super().__init__(
            ["fx", "fy", "fz", "mx", "my", "mz", "forceMagnitude"],
            label,
            partial(FormatLabel, ".02f"),
            signal,
            extra_widgets=extra_widgets,
        )


class PreclippedLabel(FormatLabel):
    def __init__(self, fmt: str = ".02f"):
        super().__init__(".02f")

    def setValue(self, value: float) -> None:
        self.setText(f"<i>{self.formator.format(value)}</i>")


class PreclippedForces(ArrayFields):
    def __init__(
        self, label: str, signal: Signal, extra_widgets: list[QWidget] | None = None
    ):
        super().__init__(
            ["fx", "fy", "fz", "mx", "my", "mz", "forceMagnitude"],
            f"<i>{label}</i>",
            PreclippedLabel,
            signal,
            extra_widgets=extra_widgets,
        )


class ForcesGrid(ArrayGrid):
    def __init__(
        self, items: list[AbstractColumn], orientation: Qt.Orientation = Qt.Horizontal
    ):
        super().__init__(
            "<b>Forces</b>",
            [
                "<b>Force X</b> (N)",
                "<b>Force Y</b> (N)",
                "<b>Force Z</b> (N)",
                "<b>Moment X</b> (Nm)",
                "<b>Moment Y</b> (Nm)",
                "<b>Moment Z</b> (Nm)",
                "<b>Magnitude</b> (N)",
            ],
            items,
            orientation,
        )
