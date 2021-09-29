# from .QTHelpers import setBoolLabelYesNo
from .SALComm import SALCommand
from .CustomLabels import Force, Moment, Clipped
from .StateEnabled import StateEnabledButton
from .TimeChart import TimeChart, TimeChartView
from PySide2.QtWidgets import (
    QLabel,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
)
from PySide2.QtCore import Slot
from asyncqt import asyncSlot
from lsst.ts.idl.enums.MTM1M3 import DetailedState


class ForceBalanceSystemPageWidget(QWidget):
    def __init__(self, m1m3):
        super().__init__()
        self.m1m3 = m1m3

        self._balanceData = None
        self._hardpointData = None

        layout = QVBoxLayout()
        dataLayout = QGridLayout()
        warningLayout = QHBoxLayout()
        commandLayout = QVBoxLayout()
        plotLayout = QHBoxLayout()
        layout.addLayout(commandLayout)
        layout.addSpacing(20)
        layout.addLayout(dataLayout)
        layout.addSpacing(20)
        layout.addLayout(warningLayout)
        layout.addSpacing(20)
        layout.addLayout(plotLayout)
        self.setLayout(layout)

        self.enableHardpointCorrectionsButton = StateEnabledButton(
            "Enable Hardpoint Corrections",
            m1m3,
            [DetailedState.ACTIVE],
        )
        self.enableHardpointCorrectionsButton.clicked.connect(
            self.issueCommandEnableHardpointCorrections
        )
        self.enableHardpointCorrectionsButton.setFixedWidth(256)
        self.disableHardpointCorrectionsButton = StateEnabledButton(
            "Disable Hardpoint Corrections",
            m1m3,
            [DetailedState.ACTIVE],
        )
        self.disableHardpointCorrectionsButton.clicked.connect(
            self.issueCommandDisableHardpointCorrections
        )
        self.disableHardpointCorrectionsButton.setFixedWidth(256)

        self.balanceForcesClipped = Clipped("Balance")

        self.balanceChart = TimeChart(
            {
                "Balance Force (N)": ["Force X", "Force Y", "Force Z", "Magnitude"],
                "Moment (N/m)": ["Moment X", "Moment Y", "Moment Z"],
            }
        )
        self.balanceChartView = TimeChartView(self.balanceChart)

        commandLayout.addWidget(self.enableHardpointCorrectionsButton)
        commandLayout.addWidget(self.disableHardpointCorrectionsButton)

        row = 0

        values = [
            "Fx",
            "Fy",
            "Fz",
            "Mx",
            "My",
            "Mz",
            "Mag",
        ]

        for d in range(7):
            dataLayout.addWidget(QLabel(f"<b>{values[d]}</b>"), row, d + 1)

        row += 1

        def createXYZ():
            return {
                "fx": Force(),
                "fy": Force(),
                "fz": Force(),
                "mx": Moment(),
                "my": Moment(),
                "mz": Moment(),
                "forceMagnitude": Force(),
            }

        def addDataRow(variables, row, col=1):
            for k, v in variables.items():
                dataLayout.addWidget(v, row, col)
                col += 1

        self.totals = createXYZ()

        dataLayout.addWidget(QLabel("<b>Total</b>"), row, 0)
        addDataRow(self.totals, row)

        row += 1
        self.corrected = createXYZ()
        dataLayout.addWidget(QLabel("<b>Corrected</b>"), row, 0)
        addDataRow(self.corrected, row)

        row += 1
        self.remaing = createXYZ()
        dataLayout.addWidget(QLabel("<b>Remaining</b>"), row, 0)
        addDataRow(self.remaing, row)

        row += 1
        dataLayout.addWidget(QLabel(" "), row, 0)
        row += 1

        hardpoints = [f"HP{x}" for x in range(1, 7)] + ["Mag"]

        for d in range(7):
            dataLayout.addWidget(QLabel(f"<b>{hardpoints[d]}</b>"), row, d + 1)

        row += 1

        dataLayout.addWidget(QLabel("<b>Measured Force</b>"), row, 0)

        self.hardpoints = [Force() for x in range(7)]
        for c in range(7):
            dataLayout.addWidget(self.hardpoints[c], row, c + 1)

        warningLayout.addWidget(self.balanceForcesClipped)
        warningLayout.addStretch()

        plotLayout.addWidget(self.balanceChartView)

        self.m1m3.appliedBalanceForces.connect(self.appliedBalanceForces)
        self.m1m3.preclippedBalanceForces.connect(self.preclippedBalanceForces)
        self.m1m3.forceActuatorState.connect(self.forceActuatorState)
        self.m1m3.hardpointActuatorData.connect(self.hardpointActuatorData)

    def _fillRow(self, variables, data):
        for k, v in variables.items():
            v.setValue(getattr(data, k))

    @Slot(map)
    def appliedBalanceForces(self, data):
        self._fillRow(self.corrected, data)

        self.balanceChart.append(
            data.timestamp,
            [data.fx, data.fy, data.fz, data.forceMagnitude],
            axis_index=0,
        )
        self.balanceChart.append(
            data.timestamp, [data.mx, data.my, data.mz], axis_index=1
        )

        self._balanceData = data
        self._setTotalForces()

        self.preclippedBalanceForces(data)

    @Slot(map)
    def preclippedBalanceForces(self, data):
        try:
            self.balanceForcesClipped.setClipped(
                self.m1m3.remote.evt_balanceForcesApplied.get().timestamp
                == self.m1m3.remote.evt_preclippedBalanceForces.get().timestamp
            )
        except AttributeError:
            self.balanceForcesClipped.setClipped(False)

    @Slot(map)
    def forceActuatorState(self, data):
        self.enableHardpointCorrectionsButton.setDisabled(data.balanceForcesApplied)
        self.disableHardpointCorrectionsButton.setEnabled(data.balanceForcesApplied)

    @Slot(map)
    def hardpointActuatorData(self, data):
        for hp in range(6):
            self.hardpoints[hp].setValue(data.measuredForce[hp])
        self.hardpoints[6].setValue(sum(data.measuredForce))

        self._fillRow(self.remaing, data)

        self._hardpointData = data
        self._setTotalForces()

    @asyncSlot()
    async def issueCommandEnableHardpointCorrections(self):
        await self._issueCommandEnableHardpointCorrections()

    @SALCommand
    def _issueCommandEnableHardpointCorrections(self, **kwargs):
        return self.m1m3.remote.cmd_enableHardpointCorrections

    @asyncSlot()
    async def issueCommandDisableHardpointCorrections(self):
        await self._issueCommandDisableHardpointCorrections()

    @SALCommand
    def _issueCommandDisableHardpointCorrections(self, **kwargs):
        return self.m1m3.remote.cmd_disableHardpointCorrections

    def _fillRowSum(self, variables, d1, d2):
        for k, v in variables.items():
            v.setValue(getattr(d1, k) + getattr(d2, k))

    def _setTotalForces(self):
        if self._balanceData is None or self._hardpointData is None:
            return

        self._fillRowSum(self.totals, self._balanceData, self._hardpointData)
