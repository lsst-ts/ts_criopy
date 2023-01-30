from functools import partial

from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PySide2.QtCore import Qt

from ..GUI import ArrayFields, ArrayGrid, UnitLabel

from ..GUI.TimeChart import SALAxis, SALChartWidget


class Forces(ArrayFields):
    def __init__(self, label, signal):
        super().__init__(
            ["fx", "fy", "fz", "mx", "my", "mz", "forceMagnitude"],
            label,
            partial(UnitLabel, ".02f"),
            signal,
        )


class ActuatorOverviewPageWidget(QWidget):
    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3

        layout = QVBoxLayout()
        dataLayout = QGridLayout()
        dataLayout.addWidget(
            ArrayGrid(
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
                [
                    Forces("<b>Applied</b>", m1m3.appliedForces),
                    Forces("<b>Measured</b>", m1m3.forceActuatorData),
                    Forces("<b>Hardpoints</b>", m1m3.hardpointActuatorData),
                    Forces(
                        "<b>Applied Acceleration</b>", m1m3.appliedAccelerationForces
                    ),
                    ArrayFields(
                        [None, None, "fz", "mx", "my"],
                        "<b>Applied Active Optics</b>",
                        partial(UnitLabel, ".02f"),
                        m1m3.appliedActiveOpticForces,
                    ),
                    Forces("<b>Applied Azimuth</b>", m1m3.appliedAzimuthForces),
                    Forces("<b>Applied Balance</b>", m1m3.appliedBalanceForces),
                    Forces("<b>Applied Elevation</b>", m1m3.appliedElevationForces),
                    Forces("<b>Applied Offset</b>", m1m3.appliedOffsetForces),
                    Forces("<b>Applied Static</b>", m1m3.appliedStaticForces),
                    Forces("<b>Applied Thermal</b>", m1m3.appliedThermalForces),
                    Forces("<b>Applied Velocity</b>", m1m3.appliedVelocityForces),
                ],
                Qt.Horizontal,
            )
        )

        plotLayout = QVBoxLayout()

        layout.addLayout(dataLayout)
        layout.addLayout(plotLayout)

        chartForces = SALChartWidget(
            SALAxis("Force (N)", self.m1m3.appliedForces).addValue(
                "Total Mag", "forceMagnitude"
            ),
            maxItems=50 * 5,
        )
        chartPercentage = SALChartWidget(
            SALAxis("Percentage", self.m1m3.forceActuatorState).addValue(
                "Support Percentage", "supportPercentage"
            ),
            maxItems=50 * 5,
        )

        plotLayout = QHBoxLayout()

        plotLayout.addWidget(chartForces)
        plotLayout.addWidget(chartPercentage)

        layout.addLayout(plotLayout)

        self.setLayout(layout)
