from functools import partial

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QWidget

from ..GUI import ArrayFields, ArrayGrid, UnitLabel
from ..GUI.TimeChart import SALAxis, SALChartWidget


class Forces(ArrayFields):
    def __init__(self, label, signal):
        super().__init__(
            ["fx", "fy", "fz", "mx", "my", "mz", "forceMagnitude"],
            f"{label}",
            partial(UnitLabel, ".02f"),
            signal,
        )


class PreclippedLabel(UnitLabel):
    def __init__(self, fmt: str = ".02f"):
        super().__init__(".02f")

    def setValue(self, value):
        self.setText(f"<i>{(value * self.scale):{self.fmt}}{self.unit_name}</i>")


class PreclippedForces(ArrayFields):
    def __init__(self, label, signal):
        super().__init__(
            ["fx", "fy", "fz", "mx", "my", "mz", "forceMagnitude"],
            f"<i>{label}</i>",
            PreclippedLabel,
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
                    PreclippedForces("Pre-clipped", m1m3.preclippedForces),
                    Forces("Applied", m1m3.appliedForces),
                    Forces("Measured", m1m3.forceActuatorData),
                    Forces("Hardpoints", m1m3.hardpointActuatorData),
                    PreclippedForces(
                        "Pre-clipped Acceleration", m1m3.preclippedAccelerationForces
                    ),
                    Forces("Applied Acceleration", m1m3.appliedAccelerationForces),
                    ArrayFields(
                        [None, None, "fz", "mx", "my"],
                        "<i>Pre-clipped Active Optics</i>",
                        PreclippedLabel,
                        m1m3.preclippedActiveOpticForces,
                    ),
                    ArrayFields(
                        [None, None, "fz", "mx", "my"],
                        "Applied Active Optics",
                        partial(UnitLabel, ".02f"),
                        m1m3.appliedActiveOpticForces,
                    ),
                    PreclippedForces(
                        "Pre-clipped Azimuth", m1m3.preclippedAzimuthForces
                    ),
                    Forces("Applied Azimuth", m1m3.appliedAzimuthForces),
                    PreclippedForces(
                        "Pre-clipped Balance", m1m3.preclippedBalanceForces
                    ),
                    Forces("Applied Balance", m1m3.appliedBalanceForces),
                    PreclippedForces(
                        "Pre-clipped Elevation", m1m3.preclippedElevationForces
                    ),
                    Forces("Applied Elevation", m1m3.appliedElevationForces),
                    PreclippedForces("Pre-clipped Offset", m1m3.preclippedOffsetForces),
                    Forces("Applied Offset", m1m3.appliedOffsetForces),
                    PreclippedForces("Pre-clipped Static", m1m3.preclippedStaticForces),
                    Forces("Applied Static", m1m3.appliedStaticForces),
                    PreclippedForces(
                        "Pre-clipped Thermal", m1m3.preclippedThermalForces
                    ),
                    Forces("Applied Thermal", m1m3.appliedThermalForces),
                    PreclippedForces(
                        "Pre-clipped Velocity", m1m3.preclippedVelocityForces
                    ),
                    Forces("Applied Velocity", m1m3.appliedVelocityForces),
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
            SALAxis("Percentage", self.m1m3.raisingLoweringInfo).addValue(
                "Weight Support Percentage", "weightSupportedPercent"
            ),
            maxItems=50 * 5,
        )

        plotLayout = QHBoxLayout()

        plotLayout.addWidget(chartForces)
        plotLayout.addWidget(chartPercentage)

        layout.addLayout(plotLayout)

        self.setLayout(layout)
