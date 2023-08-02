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

# You should have received a copy of the GNU General Public License along with
# this program.If not, see <https://www.gnu.org/licenses/>.

import os

from PySide2.QtCore import Signal
from PySide2.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .gui.sal import Application
from .m1m3 import ForceCalculator, Simulator, SimulatorWidget
from .m1m3.force_actuator import GraphPageWidget
from .salcomm import warning


class ConfigDir(QWidget):
    """Widget to display and select configuration directory.

    Parameters
    ----------
    force_calculator : `ForceCalculator`
        Calculator instance whose config directory shall be set.

    Signals
    -------
    configurationChanged : Signal(str)
        Emitted when new configuration is selected. If configuration cannot be
        loaded, empty string is passed in the signal parameter.
    """

    configurationChanged = Signal(str)

    def __init__(self, force_calculator: ForceCalculator):
        super().__init__()

        self.force_calculator = force_calculator

        layout = QHBoxLayout()

        layout.addWidget(QLabel("<b>Configuration:</b>"))

        self.path = QLabel()
        self.path.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.path)

        select = QPushButton("...")
        select.clicked.connect(self.select_dir)

        layout.addWidget(select)

        self.setLayout(layout)

    def select_dir(self) -> None:
        """Display dialog to select new configuration directory."""
        new_dir = QFileDialog.getExistingDirectory(
            self,
            "Select configuration directory",
            os.path.dirname(self.path.text()),
        )
        if new_dir == "":
            return
        try:
            self.force_calculator.load_config(new_dir)
            self.path.setText(new_dir)
            self.configurationChanged.emit(new_dir)
        except Exception as ex:
            self.configurationChanged.emit("")
            warning(
                self,
                "Cannot load configuration",
                f"<center>Cannot load configuration from {new_dir}<p>{ex}</p></center>",
            )


class SIM(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("M1M3 Simulator")

        force_calculator = ForceCalculator()
        simulator = Simulator(force_calculator)

        layout = QVBoxLayout()

        config_dir = ConfigDir(force_calculator)
        config_dir.configurationChanged.connect(self.__configuration_changed)

        layout.addWidget(config_dir)

        self.graph = GraphPageWidget(simulator)
        self.simulator_widget = SimulatorWidget(simulator)
        self.simulator_widget.setDisabled(True)

        central_widget = QWidget()
        data_layout = QHBoxLayout()
        data_layout.addWidget(self.graph)
        data_layout.addWidget(self.simulator_widget)

        layout.addLayout(data_layout)

        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    def __configuration_changed(self, new_config: str) -> None:
        self.simulator_widget.setDisabled(new_config == "")


def run() -> None:
    # Create the Qt Application
    app = Application(SIM)

    app.run()
