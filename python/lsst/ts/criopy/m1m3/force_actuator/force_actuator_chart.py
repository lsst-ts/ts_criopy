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

from lsst.ts.m1m3.utils import BumpTestKind
from lsst.ts.xml.tables.m1m3 import ForceActuatorData
from PySide6.QtCore import QDateTime, QItemSelection, Qt, QTimer, Slot
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from ...gui import TimeChart, TimeChartView
from ...time_cache import TimeCache
from .bump_test_status_item import BumpTestStatusItem


class ForceActuatorChart(TimeChartView):
    """Display chart with the actuator profile."""

    def __init__(self) -> None:
        super().__init__()

        self.setRubberBand(TimeChartView.RectangleRubberBand)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

    def new_data(self, applied: TimeCache, measured: TimeCache) -> None:
        """Change chart data.

        Parameters
        ----------
        applied : TimeCache
            New applied forces.
        measured : TimeCache
            New measured forces.
        """
        chart = TimeChart(
            {"Force (N)": [applied.columns()[1], None, measured.columns()[1]]},
            50 * 9,
            2,
        )
        chart.replace([applied, measured])
        self.setChart(chart)


class ChartModel(QStandardItemModel):
    """Model for storing force actuator test progress.

    Attributes
    ----------
    APPLIED_DATA : int
        Custom role of the applied data TimeCache.
    MEASURED_DATA : int
        Custom role of the measured data TimeCache.
    FREEZE_DATA : int
        Custom role turn to true when data shall not be updated.
    """

    APPLIED_DATA = Qt.UserRole + 1
    MEASURED_DATA = Qt.UserRole + 2
    FREEZE_DATA = Qt.UserRole + 3

    def __init__(self) -> None:
        super().__init__(0, 5)
        self.setHorizontalHeaderLabels(["Acc", "Kn", "State", "Start", "End"])

    def add(
        self,
        fa: ForceActuatorData,
        kind: BumpTestKind,
        applied_forces: TimeCache,
        measured_forces: TimeCache,
    ) -> None:
        """Add new row to data stored in the model.

        Parameters
        ----------
        fa : ForceActuatorData
            Force actuator being tested.
        kind : BumpTestKind
            Kind of the bump tests.
        applied_forces : TimeCache
            TimeCache with recorded applied data.
        measured_forces : TimeCache
            TimeCache with reocrded measured data.
        """
        row = [QStandardItem(s) for s in [str(fa.actuator_id), str(kind), "--", "--"]]
        row.insert(2, BumpTestStatusItem("--"))
        row[0].setData(fa)
        row[1].setData(kind)
        row[2].setData(applied_forces, self.APPLIED_DATA)
        row[2].setData(measured_forces, self.MEASURED_DATA)
        row[2].setData(False, self.FREEZE_DATA)

        self.appendRow(row)

    def end_time(self, row: int) -> float | None:
        """Returns data end time. This is usefull to see if data changed from
        some last check of the end_time.

        Parameters
        ----------
        row : int
            Calculate minimum date for that row.

        Returns
        -------
        end : float | None
            End time (maximum of know applied and measured forces).
        """
        di = self.item(row, 2)
        applied = di.data(self.APPLIED_DATA)
        measured = di.data(self.MEASURED_DATA)
        if not (applied.empty() or measured.empty()):
            return max(applied.end_time(), measured.end_time())

        return None

    def timed_update(self) -> None:
        for row in range(self.rowCount()):
            di = self.item(row, 2)
            applied = di.data(self.APPLIED_DATA)
            measured = di.data(self.MEASURED_DATA)
            if not (applied.empty() or measured.empty()):
                a_r = applied.time_range()
                m_r = measured.time_range()
                start = QDateTime.fromMSecsSinceEpoch(int(min(a_r[0], m_r[0])))
                end = QDateTime.fromMSecsSinceEpoch(int(max(a_r[1], m_r[1])))

                self.item(row, 3).setText(start.toString("hh:mm:ss"))
                self.item(row, 4).setText(end.toString("hh:mm:ss"))

    def find_latest(self, actuator_id: int, primary: bool) -> int | None:
        """Find latest entry for given actuator and kind.

        Parameters
        ----------
        actuator_id : int
            ID of searched actuator.
        primary : bool
            True if requested entry is for the primary axis/cylinder.

        Returns
        -------
        row : int | None
            Row of the latest record with the given actuator.
        """
        items = self.findItems(str(actuator_id), column=0)
        items.reverse()
        for i in items:
            row = i.index().row()
            kind = self.item(row, 1).data()
            if primary and kind in [
                BumpTestKind.CYLINDER_PRIMARY,
                BumpTestKind.AXIS_Z,
            ]:
                return row
            elif not (primary) and kind in [
                BumpTestKind.CYLINDER_SECONDARY,
                BumpTestKind.AXIS_X,
                BumpTestKind.AXIS_Y,
            ]:
                return row

        return None


class ChartView(QTreeView):
    def __init__(self) -> None:
        super().__init__()

        self.setModel(ChartModel())
        self.setSortingEnabled(True)
        for col in range(self.model().columnCount()):
            self.resizeColumnToContents(col)

        self.setSelectionBehavior(QTreeView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
        self.setMinimumWidth(270)

    def progress(self, actuator_id: int, primary: bool, state: int) -> None:
        model = self.model()
        row = model.find_latest(actuator_id, primary)
        if row is not None:
            di = model.item(row, 2)
            if not (di.data(ChartModel.FREEZE_DATA)):
                di.set_progress(state)

    @Slot(QItemSelection, QItemSelection)
    def selectionChanged(self, selected: QItemSelection, deselected: QItemSelection) -> None:
        super().selectionChanged(selected, deselected)
        if selected.count() > 0:
            row = selected.front().indexes()[0].row()
            self.parent().new_data(
                self.model().item(row, 2).data(ChartModel.APPLIED_DATA),
                self.model().item(row, 2).data(ChartModel.MEASURED_DATA),
            )


class ForceChartWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QHBoxLayout()

        cache_layout = QVBoxLayout()

        self.caches = ChartView()
        self.caches.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        reset_button = QPushButton("&Reset")
        reset_button.clicked.connect(self.reset)

        cache_layout.addWidget(self.caches)
        cache_layout.addWidget(reset_button)

        self.chart = ForceActuatorChart()

        layout.addLayout(cache_layout)
        layout.addWidget(self.chart)

        self.setLayout(layout)

        self._last_update = 0

        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self.timed_update)
        self._update_timer.start(200)

    @Slot()
    def timed_update(self) -> None:
        self.caches.model().timed_update()
        selected = self.caches.selectedIndexes()
        if len(selected) > 0 and isinstance(self.chart, ForceActuatorChart):
            end = self.caches.model().end_time(selected[0].row())
            if end is not None and end > self._last_update:
                self.chart.chart().resync()
                self._last_update = end

    def add(
        self,
        fa: ForceActuatorData,
        kind: BumpTestKind,
        applied_forces: TimeCache,
        measured_forces: TimeCache,
    ) -> None:
        self.caches.model().add(fa, kind, applied_forces, measured_forces)

    def reset(self) -> None:
        model = self.caches.model()
        model.removeRows(0, model.rowCount())

    def progress(self, fa: ForceActuatorData, primary: bool, state: int) -> None:
        self.caches.progress(fa.actuator_id, primary, state)

    def freeze(self) -> None:
        model = self.caches.model()
        for row in range(model.rowCount()):
            model.item(row, 2).setData(True, ChartModel.FREEZE_DATA)

    def new_data(self, applied: TimeChart, measured: TimeChart) -> None:
        self._update_timer.stop()

        self.chart.new_data(applied, measured)
        self._last_update = 0

        self._update_timer.start(200)
