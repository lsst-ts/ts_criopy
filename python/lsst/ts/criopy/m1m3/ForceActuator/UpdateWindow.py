# This file is part of T&S cRIO Python library
#
# Developed for the LSST Telescope and Site Systems. This product includes
# software developed by the LSST Project (https://www.lsst.org). See the
# COPYRIGHT file at the top-level directory of this distribution for details of
# code ownership.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

from PySide2.QtCore import QSettings, Qt, Signal, Slot
from PySide2.QtGui import QCloseEvent
from PySide2.QtWidgets import (
    QButtonGroup,
    QDoubleSpinBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from qasync import asyncSlot

from ...gui.actuatorsdisplay import ForceActuatorItem, MirrorWidget
from ...gui.sal import EngineeringButton
from ...M1M3FATable import FATABLE, FATABLE_XFA, FATABLE_YFA, FATABLE_ZFA
from ...salcomm import MetaSAL, command

ALL_AXIS = "xyz"
FORCES_KEYS = ["xForces", "yForces", "zForces"]


class EditWidget(QWidget):
    """Widget embedded into UpdateWindow. Provides spin box to change offset
    values.

    Parameters
    ----------
    enabled_axis : `str`
        Axis enabled for editting.
    control_boxes : `[QWidget]'
        Widgets (usually QPushButton) added after spin boxes.

    Signals
    -------
    axisChanged : `str`
        Called when new axis is selected.
    valueChanged : ``
        Called after spin box value is changed.
    """

    axisChanged = Signal(str)
    valueChanged = Signal()

    def __init__(self, enabled_axis: str, control_boxes: list[QWidget]):
        super().__init__()

        self.__editBox = {}
        self.__enabled_axis = enabled_axis

        self.__axisGroup = QButtonGroup()
        gridLayout = QGridLayout()

        layout = QVBoxLayout()

        self.__selected = QLabel()
        layout.addWidget(self.__selected)

        for row, axis in enumerate(ALL_AXIS):
            button = QRadioButton(axis.upper())
            if axis in enabled_axis:
                self.__axisGroup.addButton(button)
                button.setEnabled(True)
                button.setChecked(True)
                spin = QDoubleSpinBox()
                spin.setSuffix(" N")
                spin.setRange(-5000, 5000)
                spin.setEnabled(False)
                spin.valueChanged.connect(lambda v: self.valueChanged.emit())
                gridLayout.addWidget(spin, row + 1, 1)
                self.__editBox[axis] = spin
            else:
                button.setEnabled(False)
            gridLayout.addWidget(button, row + 1, 0)

        layout.addLayout(gridLayout)

        for cb in control_boxes:
            layout.addWidget(cb)

        layout.addStretch(1)
        self.setLayout(layout)

        self.__axisGroup.buttonClicked.connect(
            lambda b: self.axisChanged.emit(b.text().lower())
        )

    def setSelected(self, selectedId: int, forces: dict[str, float | None]) -> None:
        """Set new values to spin boxes."""
        self.__selected.setText(f"Selected {selectedId}")

        for key, value in forces.items():
            try:
                spin = self.__editBox[key[0]]
                if value is None:
                    spin.setEnabled(False)
                    spin.setValue(0)
                else:
                    spin.setEnabled(True)
                    spin.setValue(value)
            except KeyError:
                pass
        # set focus so new value can be entered; TabFocusReason as it allows to
        # type new value directly
        self.__editBox[self.getSelectedAxis()].setFocus(Qt.TabFocusReason)

    def getXYZ(self) -> dict[str, float]:
        """Returns map with forces values."""
        ret = {}
        for index, axis in enumerate(self.__enabled_axis):
            ret[axis + "Forces"] = self.__editBox[axis].value()
        return ret

    def selectedAxisButton(self) -> QPushButton:
        return self.__axisGroup.button(self.__axisGroup.checkedId())

    def getSelectedAxis(self) -> str:
        return self.selectedAxisButton().text().lower()

    @Slot()
    def changeAxis(self, button: QPushButton) -> None:
        self.axisChanged.emit(button.text().lower())


class UpdateWindow(QSplitter):
    """Window allowing updates to various offsets. Provides button to
    manipulate value.

    Parameters
    ----------
    m1m3 : `MetaSAL`
        SAL/DDS remote for M1M3.
    command : `str`
        Command suffix - string after cmd_apply.
    enabled_axis : `str`
        Axis (xyz strin) which command accepts.

    Attributes
    ----------
    offsets : `map`
        All possible offsets with values. Equals to arguments passed to
        cmd_applyXXX SAL/DDC command.
    """

    def __init__(self, m1m3: MetaSAL, command: str, enabled_axis: str):
        self.mirror_widget = MirrorWidget()
        super().__init__()

        self.offsets: dict[str, list[float]] = {}
        if "x" in enabled_axis:
            self.offsets["xForces"] = [0] * FATABLE_XFA
        if "y" in enabled_axis:
            self.offsets["yForces"] = [0] * FATABLE_YFA
        if "z" in enabled_axis:
            self.offsets["zForces"] = [0] * FATABLE_ZFA

        self.m1m3 = m1m3
        self.command = command
        self.__last_selected: ForceActuatorItem | None = None

        self.setWindowTitle(f"Values for {command}")

        self.addWidget(self.mirror_widget)

        clear = QPushButton("&Clear offsets")
        clear.clicked.connect(self.clearOffsets)

        apply = EngineeringButton("&Apply", m1m3)
        apply.clicked.connect(self.applyChanges)

        self.edit_widget = EditWidget(enabled_axis, [clear, apply])
        self.edit_widget.axisChanged.connect(self.set_axis)
        self.edit_widget.valueChanged.connect(self.valueChanged)
        self.addWidget(self.edit_widget)

        self.setStretchFactor(0, 10)
        self.setStretchFactor(1, 1)

        self.set_axis(enabled_axis[-1])

        settings = QSettings("LSST.TS", "M1M3Offsets_" + self.command)
        try:
            self.restoreGeometry(settings.value("geometry"))  # type: ignore
            self.restoreState(settings.value("windowState"))  # type: ignore
        except AttributeError:
            self.resize(700, 600)

        self.mirror_widget.mirrorView.selectionChanged.connect(self.selectionChanged)

        m1m3.reemit_remote()

    def closeEvent(self, event: QCloseEvent) -> None:
        settings = QSettings("LSST.TS", "M1M3Offsets_" + self.command)
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())

        super().closeEvent(event)

    def selectionChanged(self, selected: ForceActuatorItem) -> None:
        """Called when selected Force Actuator is changed.

        Parameters
        ----------
        selected : `ForceActuatorItem`
            Newly selected ForceActuatorItem object.
        """
        forces: dict[str, float | None] = {
            "xForces": None,
            "yForces": None,
            "zForces": None,
        }

        for key, value in self.offsets.items():
            axis = key[0]
            row = FATABLE[selected.index]
            actIndex = None
            if axis == "x":
                actIndex = row.x_index
            elif axis == "y":
                actIndex = row.y_index
            elif axis == "z":
                actIndex = row.z_index
            if actIndex is not None:
                forces[key] = value[actIndex]

        self.__last_selected = selected

        self.edit_widget.setSelected(selected.actuator_id, forces)

    def redraw(self) -> None:
        """Refresh value and gauge scale to match self.offsets"""
        self.set_axis(self.edit_widget.getSelectedAxis())

    @asyncSlot()
    async def applyChanges(self) -> None:
        if self.__last_selected is not None:
            self.selectionChanged(self.__last_selected)
        await command(
            self,
            getattr(self.m1m3.remote, "cmd_apply" + self.command),
            **self.offsets,
        )

    @Slot()
    def set_axis(self, axis: str) -> None:
        """Sets axis to properly draw disabled/enabled force actuators.

        Parameters
        ----------
        axis : `str`
            Newly selected axis.
        """
        self.mirror_widget.clear()
        minV = None
        maxV = None
        for row in FATABLE:
            if axis == "x":
                data_index = row.x_index
            elif axis == "y":
                data_index = row.y_index
            else:
                data_index = row.index

            value = None

            if data_index is not None:
                value = self.offsets[axis + "Forces"][data_index]  # type: ignore
                if minV is None:
                    minV = value
                    maxV = value
                else:
                    minV = min(value, minV)
                    maxV = max(value, maxV)

            state = (
                ForceActuatorItem.STATE_INACTIVE
                if data_index is None
                else ForceActuatorItem.STATE_ACTIVE
            )

            self.mirror_widget.mirrorView.addForceActuator(
                row,
                value,
                data_index,
                state,
            )
        if minV is None or maxV is None:
            return

        self.mirror_widget.setRange(minV, maxV)

    @Slot()
    def valueChanged(self) -> None:
        if self.__last_selected is None:
            return
        lastRow = FATABLE[self.__last_selected.index]
        values = self.edit_widget.getXYZ()

        for key, value in self.offsets.items():
            axis = key[0]
            last_index = None
            if axis == "x":
                last_index = lastRow.x_index
            elif axis == "y":
                last_index = lastRow.y_index
            elif axis == "z":
                last_index = lastRow.z_index
            if last_index is not None:
                self.offsets[key][last_index] = values[key]
        self.redraw()

    @Slot()
    def clearOffsets(self) -> None:
        for key, offset in self.offsets.items():
            self.offsets[key] = [0] * len(offset)
        self.redraw()
