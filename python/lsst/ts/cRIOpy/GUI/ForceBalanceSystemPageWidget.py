# from .QTHelpers import setBoolLabelYesNo
from .SALComm import SALCommand
from .CustomLabels import Clipped
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
        self.hardpointFxLabel = QLabel("0.0")
        self.hardpointFyLabel = QLabel("0.0")
        self.hardpointFzLabel = QLabel("0.0")
        self.hardpointMxLabel = QLabel("0.0")
        self.hardpointMyLabel = QLabel("0.0")
        self.hardpointMzLabel = QLabel("0.0")
        self.hardpointMagLabel = QLabel("0.0")
        self.balanceFxLabel = QLabel("0.0")
        self.balanceFyLabel = QLabel("0.0")
        self.balanceFzLabel = QLabel("0.0")
        self.balanceMxLabel = QLabel("0.0")
        self.balanceMyLabel = QLabel("0.0")
        self.balanceMzLabel = QLabel("0.0")
        self.balanceMagLabel = QLabel("0.0")
        self.totalFxLabel = QLabel("0.0")
        self.totalFyLabel = QLabel("0.0")
        self.totalFzLabel = QLabel("0.0")
        self.totalMxLabel = QLabel("0.0")
        self.totalMyLabel = QLabel("0.0")
        self.totalMzLabel = QLabel("0.0")
        self.totalMagLabel = QLabel("0.0")

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
        col = 0
        dataLayout.addWidget(QLabel("Fx (N)"), row, col + 1)
        dataLayout.addWidget(QLabel("Fy (N)"), row, col + 2)
        dataLayout.addWidget(QLabel("Fz (N)"), row, col + 3)
        dataLayout.addWidget(QLabel("Mx (Nm)"), row, col + 4)
        dataLayout.addWidget(QLabel("My (Nm)"), row, col + 5)
        dataLayout.addWidget(QLabel("Mz (Nm)"), row, col + 6)
        dataLayout.addWidget(QLabel("Mag (N)"), row, col + 7)
        row += 1
        dataLayout.addWidget(QLabel("Total"), row, col)
        dataLayout.addWidget(self.totalFxLabel, row, col + 1)
        dataLayout.addWidget(self.totalFyLabel, row, col + 2)
        dataLayout.addWidget(self.totalFzLabel, row, col + 3)
        dataLayout.addWidget(self.totalMxLabel, row, col + 4)
        dataLayout.addWidget(self.totalMyLabel, row, col + 5)
        dataLayout.addWidget(self.totalMzLabel, row, col + 6)
        dataLayout.addWidget(self.totalMagLabel, row, col + 7)
        row += 1
        dataLayout.addWidget(QLabel("Corrected"), row, col)
        dataLayout.addWidget(self.balanceFxLabel, row, col + 1)
        dataLayout.addWidget(self.balanceFyLabel, row, col + 2)
        dataLayout.addWidget(self.balanceFzLabel, row, col + 3)
        dataLayout.addWidget(self.balanceMxLabel, row, col + 4)
        dataLayout.addWidget(self.balanceMyLabel, row, col + 5)
        dataLayout.addWidget(self.balanceMzLabel, row, col + 6)
        dataLayout.addWidget(self.balanceMagLabel, row, col + 7)
        row += 1
        dataLayout.addWidget(QLabel("Remaining"), row, col)
        dataLayout.addWidget(self.hardpointFxLabel, row, col + 1)
        dataLayout.addWidget(self.hardpointFyLabel, row, col + 2)
        dataLayout.addWidget(self.hardpointFzLabel, row, col + 3)
        dataLayout.addWidget(self.hardpointMxLabel, row, col + 4)
        dataLayout.addWidget(self.hardpointMyLabel, row, col + 5)
        dataLayout.addWidget(self.hardpointMzLabel, row, col + 6)
        dataLayout.addWidget(self.hardpointMagLabel, row, col + 7)
        row += 1
        dataLayout.addWidget(QLabel(" "), row, col)
        row += 1
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

        row = 0
        col = 0
        warningLayout.addWidget(self.balanceForcesClipped)
        warningLayout.addStretch()

        plotLayout.addWidget(self.balanceChartView)

        self.m1m3.appliedBalanceForces.connect(self.appliedBalanceForces)
        self.m1m3.preclippedBalanceForces.connect(self.preclippedBalanceForces)
        self.m1m3.forceActuatorState.connect(self.forceActuatorState)
        self.m1m3.hardpointActuatorData.connect(self.hardpointActuatorData)

    @Slot(map)
    def appliedBalanceForces(self, data):
        self.balanceFxLabel.setText("%0.1f" % data.fx)
        self.balanceFyLabel.setText("%0.1f" % data.fy)
        self.balanceFzLabel.setText("%0.1f" % data.fz)
        self.balanceMxLabel.setText("%0.1f" % data.mx)
        self.balanceMyLabel.setText("%0.1f" % data.my)
        self.balanceMzLabel.setText("%0.1f" % data.mz)
        self.balanceMagLabel.setText("%0.1f" % data.forceMagnitude)

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
        self.hardpointFxLabel.setText("%0.1f" % data.fx)
        self.hardpointFyLabel.setText("%0.1f" % data.fy)
        self.hardpointFzLabel.setText("%0.1f" % data.fz)
        self.hardpointMxLabel.setText("%0.1f" % data.mx)
        self.hardpointMyLabel.setText("%0.1f" % data.my)
        self.hardpointMzLabel.setText("%0.1f" % data.mz)
        self.hardpointMagLabel.setText("%0.1f" % data.forceMagnitude)

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

    def _setTotalForces(self):
        if self._balanceData is None or self._hardpointData is None:
            return

        self.totalFxLabel.setText(
            "%0.1f" % (self._balanceData.fx + self._hardpointData.fx)
        )
        self.totalFyLabel.setText(
            "%0.1f" % (self._balanceData.fy + self._hardpointData.fy)
        )
        self.totalFzLabel.setText(
            "%0.1f" % (self._balanceData.fz + self._hardpointData.fz)
        )
        self.totalMxLabel.setText(
            "%0.1f" % (self._balanceData.mx + self._hardpointData.mx)
        )
        self.totalMyLabel.setText(
            "%0.1f" % (self._balanceData.my + self._hardpointData.my)
        )
        self.totalMzLabel.setText(
            "%0.1f" % (self._balanceData.mz + self._hardpointData.mz)
        )
        self.totalMagLabel.setText(
            "%0.1f"
            % (self._balanceData.forceMagnitude + self._hardpointData.forceMagnitude)
        )
