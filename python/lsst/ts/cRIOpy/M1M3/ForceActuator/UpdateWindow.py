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

from PySide2.QtCore import Qt, Signal, Slot, QSettings
from PySide2.QtWidgets import (
    QSplitter,
    QWidget,
    QButtonGroup,
    QRadioButton,
    QGridLayout,
    QVBoxLayout,
    QDoubleSpinBox,
    QLabel,
    QPushButton,
)

from asyncqt import asyncSlot

from ...M1M3FATable import (
    FATABLE,
    FATABLE_ID,
    FATABLE_INDEX,
    FATABLE_XINDEX,
    FATABLE_YINDEX,
    FATABLE_XPOSITION,
    FATABLE_YPOSITION,
    FATABLE_ORIENTATION,
    FATABLE_XFA,
    FATABLE_YFA,
    FATABLE_ZFA,
)
from ...GUI.ActuatorsDisplay import MirrorWidget, ForceActuator
from ...GUI.SAL import SALCommand, EngineeringButton

ALL_AXIS = "xyz"
FORCES_KEYS = ["xForces", "yForces", "zForces"]


class EditWidget(QWidget):

    axisChanged = Signal(str)
    valueChanged = Signal()

    def __init__(self, enabledAxis, controlBoxes):
        super().__init__()

        self.editBox = {}
        self.enabledAxis = enabledAxis

        self.axisGroup = QButtonGroup()
        gridLayout = QGridLayout()

        self.selected = QLabel()
        gridLayout.addWidget(self.selected, 0, 0, 1, 2)

        for (row, axis) in enumerate(ALL_AXIS):
            button = QRadioButton(axis.upper())
            if axis in enabledAxis:
                self.axisGroup.addButton(button)
                button.setEnabled(True)
                button.setChecked(True)
                spin = QDoubleSpinBox()
                spin.setSuffix(" N")
                spin.setRange(-5000, 5000)
                spin.setEnabled(False)
                spin.valueChanged.connect(lambda v: self.valueChanged.emit())
                gridLayout.addWidget(spin, row + 1, 1)
                self.editBox[axis] = spin
            else:
                button.setEnabled(False)
            gridLayout.addWidget(button, row + 1, 0)

        layout = QVBoxLayout()
        layout.addLayout(gridLayout)

        for cb in controlBoxes:
            layout.addWidget(cb)

        layout.addStretch(1)
        self.setLayout(layout)

        self.axisGroup.buttonClicked.connect(
            lambda b: self.axisChanged.emit(b.text().lower())
        )

    def setSelected(self, selectedId, forces):
        self.selected.setText(f"Selected {selectedId}")

        for (key, value) in forces.items():
            try:
                spin = self.editBox[key[0]]
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
        self.editBox[self.getSelectedAxis()].setFocus(Qt.TabFocusReason)

    def getXYZ(self):
        ret = {}
        for (index, axis) in enumerate(self.enabledAxis):
            ret[axis + "Forces"] = self.editBox[axis].value()
        return ret

    def selectedAxisButton(self):
        return self.axisGroup.button(self.axisGroup.checkedId())

    def getSelectedAxis(self):
        return self.selectedAxisButton().text().lower()

    @Slot()
    def changeAxis(self, button):
        self.axisChanged.emit(button.text().lower())


class UpdateWindow(QSplitter):
    def __init__(self, m1m3, command, enabledAxis):
        self.mirrorWidget = MirrorWidget()
        super().__init__()

        self.offsets = {}
        if "x" in enabledAxis:
            self.offsets["xForces"] = [0] * FATABLE_XFA
        if "y" in enabledAxis:
            self.offsets["yForces"] = [0] * FATABLE_YFA
        if "z" in enabledAxis:
            self.offsets["zForces"] = [0] * FATABLE_ZFA

        self.m1m3 = m1m3
        self.command = command
        self.enabledAxis = enabledAxis
        self.__lastSelected = None

        self.setWindowTitle(f"Values for {command}")

        self.addWidget(self.mirrorWidget)

        clear = QPushButton("&Clear offsets")
        clear.clicked.connect(self.clearOffsets)

        apply = EngineeringButton("&Apply", m1m3)
        apply.clicked.connect(self.applyChanges)

        self.editWidget = EditWidget(enabledAxis, (clear, apply))
        self.editWidget.axisChanged.connect(self.setAxis)
        self.editWidget.valueChanged.connect(self.valueChanged)
        self.addWidget(self.editWidget)

        self.setStretchFactor(0, 10)
        self.setStretchFactor(1, 1)

        self.setAxis(self.enabledAxis[-1])

        settings = QSettings("LSST.TS", "M1M3Offsets_" + self.command)
        try:
            self.restoreGeometry(settings.value("geometry"))
            self.restoreState(settings.value("windowState"))
        except AttributeError:
            self.resize(700, 600)

        self.mirrorWidget.mirrorView.selectionChanged.connect(self.selectionChanged)

        m1m3.reemit_remote()

    def closeEvent(self, event):
        settings = QSettings("LSST.TS", "M1M3Offsets_" + self.command)
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())

        super().closeEvent(event)

    def selectionChanged(self, sel):
        forces = {"xForces": None, "yForces": None, "zForces": None}

        for (key, value) in self.offsets.items():
            index = ALL_AXIS.index(key[0])
            row = FATABLE[sel.index]
            actIndex = row[FATABLE_XINDEX + index]
            if actIndex is not None:
                forces[key] = value[actIndex]

        self.__lastSelected = sel

        self.editWidget.setSelected(sel.id, forces)

    def redraw(self):
        self.setAxis(self.editWidget.getSelectedAxis())

    @asyncSlot()
    async def applyChanges(self):
        if self.__lastSelected is not None:
            self.selectionChanged(self.__lastSelected)
        await SALCommand(
            self, getattr(self.m1m3.remote, "cmd_apply" + self.command), **self.offsets
        )

    @Slot(str)
    def setAxis(self, axis):
        self.mirrorWidget.mirrorView.clear()
        minV = None
        maxV = None
        for row in FATABLE:
            if axis == "x":
                dataIndex = row[FATABLE_XINDEX]
            elif axis == "y":
                dataIndex = row[FATABLE_YINDEX]
            else:
                dataIndex = row[FATABLE_INDEX]

            value = None

            if dataIndex is not None:
                value = self.offsets[axis + "Forces"][dataIndex]
                if minV is None:
                    minV = value
                    maxV = value
                else:
                    minV = min(value, minV)
                    maxV = max(value, maxV)

            state = (
                ForceActuator.STATE_INACTIVE
                if dataIndex is None
                else ForceActuator.STATE_ACTIVE
            )

            self.mirrorWidget.mirrorView.addForceActuator(
                row[FATABLE_ID],
                row[FATABLE_INDEX],
                row[FATABLE_XPOSITION] * 1000,
                row[FATABLE_YPOSITION] * 1000,
                row[FATABLE_ORIENTATION],
                value,
                dataIndex,
                state,
            )
        self.mirrorWidget.setRange(minV, maxV)

    @Slot()
    def valueChanged(self):
        if self.__lastSelected is None:
            return
        lastRow = FATABLE[self.__lastSelected.index]
        values = self.editWidget.getXYZ()

        for (key, value) in self.offsets.items():
            index = ALL_AXIS.index(key[0])
            lastIndex = lastRow[FATABLE_XINDEX + index]
            if lastIndex is not None:
                self.offsets[key][lastIndex] = values[key]
        self.redraw()

    @Slot()
    def clearOffsets(self):
        for (key, offset) in self.offsets.items():
            self.offsets[key] = [0] * len(offset)
        self.redraw()
