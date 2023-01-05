# This file is part of M1M3 TS GUI.
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

from PySide2.QtWidgets import QWidget, QVBoxLayout

from ..GUI import DockWindow, DataFormWidget, DataLabel, Liter, LiterMinute


class FlowMeterWidget(DockWindow):
    """Display flowmeter values.

    Parameters
    ----------

    m1m3ts : `SALComm`
        SALComm object for MTM1M3TS.
    """

    def __init__(self, m1m3ts):
        super().__init__("Flow meter")

        layout = QVBoxLayout()
        layout.addWidget(
            DataFormWidget(
                m1m3ts.flowMeter,
                [
                    ("Signal Strength", DataLabel(field="signalStrength")),
                    ("Flow Rate", LiterMinute(field="flowRate")),
                    ("Net Total", Liter(field="netTotalizer")),
                    ("Positive Total", Liter(field="positiveTotalizer")),
                    ("Negative Total", Liter(field="negativeTotalizer")),
                ],
            )
        )

        widget = QWidget()
        widget.setLayout(layout)

        self.setWidget(widget)
