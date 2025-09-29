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
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import typing

import numpy
from lsst.ts.salobj import BaseMsgType
from lsst.ts.xml.tables.m1m3 import FAIndex, FATable
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QWidget
from qasync import asyncSlot

from ...gui import WarningLabel
from ...gui.actuatorsdisplay import ForceActuatorItem
from ...gui.sal import TimeDeltaLabel, TopicData, TopicDetailWidget, TopicWindow
from ...salcomm import MetaSAL, command
from .topics import Topics
from .update_window import UpdateWindow


class DetailWidget(TopicDetailWidget):
    def __init__(self, m1m3: MetaSAL):
        super().__init__()
        self.m1m3 = m1m3

        self.update_windows: dict[str, QWidget] = {}
        self.topic: TopicData | None = None

        layout = QGridLayout()

        self.selected_actuator_id_label = QLabel()
        self.selected_actuator_value_label = QLabel()
        self.selected_actuator_warning_label = WarningLabel()
        self.last_updated_label = TimeDeltaLabel(time_delta=60)

        self.near_selected_ids_label = QLabel()
        self.near_selected_value_label = QLabel()

        self.far_selected_ids_label = QLabel()
        self.far_selected_value_label = QLabel()

        def addDetails(
            row: int, name: str, label: QLabel, nears: QLabel, fars: QLabel
        ) -> None:
            layout.addWidget(QLabel(name), row, 0)
            layout.addWidget(label, row, 1)
            layout.addWidget(nears, row, 2)
            layout.addWidget(fars, row, 3)

        addDetails(
            0,
            "<b>Variable</b>",
            QLabel("<b>Selected</b>"),
            QLabel("<b>Near Neighbors</b>"),
            QLabel("<b>Far Neighbors</b>"),
        )
        addDetails(
            1,
            "<b>Id</b>",
            self.selected_actuator_id_label,
            self.near_selected_ids_label,
            self.far_selected_ids_label,
        )
        addDetails(
            2,
            "<b>Value</b>",
            self.selected_actuator_value_label,
            self.near_selected_value_label,
            self.far_selected_value_label,
        )
        addDetails(
            3,
            "<b>Last Updated</b>",
            self.last_updated_label,
            QLabel("<b>Warning</b>"),
            self.selected_actuator_warning_label,
        )

        self.forces_moments = [
            QLabel("---"),
            QLabel("---"),
            QLabel("---"),
            QLabel("---"),
            QLabel("---"),
            QLabel("---"),
            QLabel("---"),
        ]

        layout.addWidget(QLabel("<b>Forces</b>"), 4, 0)
        layout.addWidget(self.forces_moments[6], 5, 0)
        for i, a in enumerate("XYZ"):
            layout.addWidget(QLabel(f"<b>{a}</b>"), 4, i + 1)
            layout.addWidget(self.forces_moments[i], 5, i + 1)

        layout.addWidget(QLabel("<b>Moments</b>"), 6, 0)
        for i, a in enumerate("XYZ"):
            layout.addWidget(QLabel(f"<b>{a}</b>"), 6, i + 1)
            layout.addWidget(self.forces_moments[i + 3], 7, i + 1)

        self.edit_button = QPushButton("&Modify")
        self.edit_button.clicked.connect(self.edit_values)
        self.clear_button = QPushButton("&Zero")
        self.clear_button.clicked.connect(self.zero_values)

        self.set_topic(None)

        layout.addWidget(self.edit_button, 8, 0, 1, 2)
        layout.addWidget(self.clear_button, 8, 2, 1, 2)

        self.setLayout(layout)

    def update_selected_actuator(self, selected_actuator: ForceActuatorItem) -> None:
        """
        Called from childrens to update currently selected actuator display.

        Parameters
        ----------

        selected_actuator : `ForceActuatorItem`
            Contains actuator ID (selected actuator ID), data (selected
            actuator current value) and warning (boolean, true if value is in
            warning).
        """
        if selected_actuator is None or self.topic is None or self.field is None:
            self.selected_actuator_id_label.setText("not selected")
            self.selected_actuator_value_label.setText("")
            self.selected_actuator_warning_label.setText("")
            return

        self.selected_actuator_id_label.setText(
            str(selected_actuator.actuator.actuator_id)
        )
        self.selected_actuator_value_label.setText(selected_actuator.get_value())
        self.selected_actuator_warning_label.setValue(selected_actuator.warning)

        data = self.field.get_value(self._get_data())

        # near neighbour
        near_ids = FATable[selected_actuator.actuator.index].near_neighbors
        near_indices = list(
            selected_actuator.actuator.near_neighbors_indices(self.field.value_index)
        )

        if len(near_indices) == 0:
            self.near_selected_ids_label.setText("---")
            self.near_selected_value_label.setText("---")
        else:
            self.near_selected_ids_label.setText(",".join(map(str, near_ids)))
            self.near_selected_value_label.setText(
                f"{selected_actuator.format_value(numpy.average([data[i] for i in near_indices]))}"
            )

        far_ids = filter(
            lambda f: f not in near_ids,
            FATable[selected_actuator.actuator.index].far_neighbors,
        )
        farIndices = list(
            selected_actuator.actuator.only_far_neighbors_indices(
                self.field.value_index
            )
        )
        if len(farIndices) == 0:
            self.far_selected_ids_label.setText("---")
            self.far_selected_value_label.setText("---")
        else:
            self.far_selected_ids_label.setText(",".join(map(str, far_ids)))
            self.far_selected_value_label.setText(
                f"{selected_actuator.format_value(numpy.average([data[i] for i in farIndices]))}"
            )

    def data_changed(self, data: BaseMsgType | None) -> None:
        if data is None:
            self.last_updated_label.set_unknown()
            return

        try:
            self.last_updated_label.setValue(data.timestamp)
        except AttributeError:
            self.last_updated_label.setValue(data.private_sndStamp)

    @Slot()
    def edit_values(self) -> None:
        def get_axis(topic: TopicData) -> str:
            axis = ""
            for f in topic.fields:
                if f.value_index == FAIndex.X:
                    axis += "x"
                elif f.value_index == FAIndex.Y:
                    axis += "y"
                elif f.value_index == FAIndex.Z:
                    axis += "z"
            return "".join(sorted(set(axis)))

        assert self.topic is not None
        assert self.topic.command is not None

        suffix = self.topic.command
        try:
            self.update_windows[suffix].show()
        except KeyError:
            w = UpdateWindow(self.m1m3, suffix, get_axis(self.topic))
            w.show()
            self.update_windows[suffix] = w

    @asyncSlot()
    async def zero_values(self) -> None:
        assert self.topic is not None
        assert self.topic.command is not None

        await command(self, getattr(self.m1m3.remote, "cmd_clear" + self.topic.command))

    def set_topic(self, topic: TopicData | None) -> None:
        self.topic = topic
        enabled = topic is not None and topic.command is not None
        self.edit_button.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)


class Widget(TopicWindow):
    """
    Abstract class for widget and graphics display of selected M1M3 values.
    Children classes must implement change_values and update_values(data)
    methods.

    Parameters
    ----------

    m1m3 : `SALComm`
        SALComm instance to communicate with SAL.
    user_widget : `QWidget`
        Widget to be displayed on left from value selection. Its content shall
        be update in update_values(data) method.
    """

    def __init__(self, m1m3: MetaSAL, user_widget: QWidget):
        super().__init__(m1m3, Topics(), user_widget, DetailWidget(m1m3))

        self.setCollapsible(0, False)
        self.setStretchFactor(0, 10)
        self.setStretchFactor(1, 1)

        self.topic_list.setFixedWidth(256)
        self.field_list.setFixedWidth(256)

    def change_values(self) -> None:
        """Called when new values were selected by the user."""
        raise NotImplementedError(
            "change_values method must be implemented in all Widget childrens"
        )

    def _get_data(self) -> typing.Any:
        assert self.topic is not None
        topic = self.topic.getTopic()
        if isinstance(topic, str):
            return getattr(self.comm.remote, topic).get()
        return topic

    def change_field(self, topic_index: int, field_index: int) -> BaseMsgType:
        """
        Redraw actuators with new values.
        """
        data = super().change_field(topic_index, field_index)
        if data is None:
            return

        assert self.detail_widget is not None
        self.detail_widget.set_topic(self.topic)

        self.change_values()
        self.update_values(data)

    @Slot()
    def data_changed(self, data: BaseMsgType | None) -> None:
        """
        Called when selected data are updated.

        Parameters
        ----------
        data : `class`
            Class holding data. See SALComm for details.
        """
        self.update_values(data)

        assert self.detail_widget is not None

        self.detail_widget.data_changed(data)

        if data is None:
            return

        if self.topic is not None:
            try:
                f_m_t = getattr(self.topic, "get_forces_moments")(data)

                for i, d in enumerate(f_m_t):
                    if d is None:
                        self.detail_widget.forces_moments[i].setText("-N-")
                    else:
                        self.detail_widget.forces_moments[i].setText(f"{d:.3f} N")

            except AttributeError:
                pass
