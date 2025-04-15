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

import asyncio

from lsst.ts.m1m3.utils import BumpTestKind
from lsst.ts.xml.tables.m1m3 import ForceActuatorData
from PySide6.QtCore import QItemSelection, Qt, Slot
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QTreeView, QWidget

from ...gui import TimeChart, TimeChartView
from ...time_cache import TimeCache


class ForceActuatorChart(TimeChartView):
    def __init__(
        self,
        fa: ForceActuatorData,
        kind: BumpTestKind,
        applied: TimeCache,
        measured: TimeCache,
    ):
        super().__init__()

        axis = str(kind)

        def add_chart() -> None:
            self.setChart(
                TimeChart(
                    {"Force (N)": [f"Applied {axis}", f"Measured {axis}"]}, 50 * 9, 2
                )
            )

        asyncio.get_event_loop().call_soon(add_chart)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        # self.chart().append(data.timestamp, chart_data,
        # cache_index=0, update=True)
        # self.chart().append(data.timestamp,
        # chart_data, cache_index=1, update=True)


class ChartModel(QStandardItemModel):

    def __init__(self):
        super().__init__(0, 5)
        self.setHorizontalHeaderLabels(["Actuator ID", "Kind", "State", "Start", "End"])


class ChartView(QTreeView):
    def __init__(self):
        super().__init__()

        self.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTreeView.SelectionMode.SingleSelection)

    def add(
        self,
        fa: ForceActuatorData,
        kind: BumpTestKind,
        applied_forces: TimeCache,
        measured_forces: TimeCache,
    ) -> None:
        row = [
            QStandardItem(s) for s in [str(fa.actuator_id), str(kind), "--", "--", "--"]
        ]
        row[0].setData(fa)
        row[1].setData(kind)
        row[2].setData(applied_forces, Qt.UserRole + 1)
        row[2].setData(measured_forces, Qt.UserRole + 2)

        self.model().appendRow(row)

    @Slot(QItemSelection, QItemSelection)
    def selectionChanged(
        self, selected: QItemSelection, deselected: QItemSelection
    ) -> None:
        super().selectionChanged(selected, deselected)
        if selected.count() > 0:
            row = selected.front().indexes()[0].row()
            self.parent().new_data(
                self.model().item(row, 0).data(),
                self.model().item(row, 1).data(),
                self.model().item(row, 2).data(Qt.UserRole + 1),
                self.model().item(row, 2).data(Qt.UserRole + 2),
            )


class ForceChartWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        self.caches = ChartView()
        self.caches.setModel(ChartModel())
        self.caches.setSortingEnabled(True)
        self.caches.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.chart = QWidget()
        self.chart.setSizePolicy(
            QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding
        )

        layout.addWidget(self.caches)
        layout.addWidget(self.chart)

        self.setLayout(layout)

    def add(
        self,
        fa: ForceActuatorData,
        kind: BumpTestKind,
        applied_forces: TimeCache,
        measured_forces: TimeCache,
    ) -> None:
        self.caches.add(fa, kind, applied_forces, measured_forces)

    def clear(self) -> None:
        self.caches.setModel(ChartModel())

    def new_data(
        self,
        fa: ForceActuatorData,
        kind: BumpTestKind,
        applied: TimeChart,
        measured: TimeChart,
    ) -> None:
        new_chart = ForceActuatorChart(fa, kind, applied, measured)
        self.layout().replaceWidget(self.chart, new_chart)
        self.chart = new_chart
