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

        self.hardpoint1ForceLabel = QLabel("0.0")
        self.hardpoint2ForceLabel = QLabel("0.0")
        self.hardpoint3ForceLabel = QLabel("0.0")
        self.hardpoint4ForceLabel = QLabel("0.0")
        self.hardpoint5ForceLabel = QLabel("0.0")
        self.hardpoint6ForceLabel = QLabel("0.0")
        self.hardpointMagForceLabel = QLabel("0.0")

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

        col = 0
        dataLayout.addWidget(QLabel("HP1 (N)"), row, col + 1)
        dataLayout.addWidget(QLabel("HP2 (N)"), row, col + 2)
        dataLayout.addWidget(QLabel("HP3 (N)"), row, col + 3)
        dataLayout.addWidget(QLabel("HP4 (N)"), row, col + 4)
        dataLayout.addWidget(QLabel("HP5 (N)"), row, col + 5)
        dataLayout.addWidget(QLabel("HP6 (N)"), row, col + 6)
        dataLayout.addWidget(QLabel("Mag (N)"), row, col + 7)
        row += 1
        dataLayout.addWidget(QLabel("Measured Force"), row, col)
        dataLayout.addWidget(self.hardpoint1ForceLabel, row, col + 1)
        dataLayout.addWidget(self.hardpoint2ForceLabel, row, col + 2)
        dataLayout.addWidget(self.hardpoint3ForceLabel, row, col + 3)
        dataLayout.addWidget(self.hardpoint4ForceLabel, row, col + 4)
        dataLayout.addWidget(self.hardpoint5ForceLabel, row, col + 5)
        dataLayout.addWidget(self.hardpoint6ForceLabel, row, col + 6)
        dataLayout.addWidget(self.hardpointMagForceLabel, row, col + 7)

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
        self.hardpoint1ForceLabel.setText("%0.1f" % data.measuredForce[0])
        self.hardpoint2ForceLabel.setText("%0.1f" % data.measuredForce[1])
        self.hardpoint3ForceLabel.setText("%0.1f" % data.measuredForce[2])
        self.hardpoint4ForceLabel.setText("%0.1f" % data.measuredForce[3])
        self.hardpoint5ForceLabel.setText("%0.1f" % data.measuredForce[4])
        self.hardpoint6ForceLabel.setText("%0.1f" % data.measuredForce[5])
        self.hardpointMagForceLabel.setText("%0.1f" % (sum(data.measuredForce)))

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
