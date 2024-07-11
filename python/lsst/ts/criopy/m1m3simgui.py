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
import sys

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
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

    config_dir: str = ""

    def __init__(self, force_calculator: ForceCalculator):
        super().__init__()

        self.force_calculator = force_calculator

        layout = QHBoxLayout()

        layout.addWidget(QLabel("<b>Configuration:</b>"))

        self.path = QLabel()
        self.path.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self.path)

        self.reload = QPushButton("&Reload")
        self.reload.clicked.connect(self.reload_config)

        layout.addWidget(self.reload)
        self.reload.setDisabled(True)

        select = QPushButton("...")
        select.clicked.connect(self.select_dir)

        layout.addWidget(select)

        self.setLayout(layout)

    @Slot()
    def reload_config(self) -> None:
        self.force_calculator.load_config(self.config_dir)
        self.configurationChanged.emit(self.config_dir)

    @Slot()
    def select_dir(self) -> None:
        """Display dialog to select new configuration directory."""
        config_dir = QFileDialog.getExistingDirectory(
            self,
            "Select configuration directory",
            os.path.dirname(self.path.text()),
        )
        if config_dir == "":
            return
        self.load_config(config_dir)

    def load_config(self, config_dir: str) -> None:
        """Load new configuration. Can be called from application to load
        configuration.

        Parameters
        ----------
        config_dir : `str`
            New configuration directory to load.
        """
        self.config_dir = config_dir
        try:
            self.reload_config()
            self.path.setText(self.config_dir)
            self.reload.setDisabled(False)
        except Exception as ex:
            self.config_dir = ""
            self.configurationChanged.emit("")
            warning(
                self,
                "Cannot load configuration",
                f"<center>Cannot load configuration from {config_dir}<p>{ex}</p></center>",
            )


class SIM(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("M1M3 Simulator")

        self.force_calculator = ForceCalculator()
        simulator = Simulator(self.force_calculator)

        layout = QVBoxLayout()

        self.config_dir_widget = ConfigDir(self.force_calculator)
        self.config_dir_widget.configurationChanged.connect(
            self.__configuration_changed
        )

        layout.addWidget(self.config_dir_widget)

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
        self.simulator_widget.recalculate()

    def load_config(self, config_dir: str) -> None:
        """Load new configuration.

        Parameters
        ----------
        config_dir : `str`
            New configuration directory.
        """
        self.config_dir_widget.load_config(config_dir)
        self.__configuration_changed(config_dir)


class SIMApplication(Application):
    def process_command_line(self) -> None:
        """Called to process command line arguments."""
        positional_arguments = self.parser.positionalArguments()
        if len(positional_arguments) == 1:
            assert self.eui is not None
            self.eui.load_config(positional_arguments[0])


def run() -> None:
    # Create the Qt Application
    app = SIMApplication(SIM, config=("Configuration directory", ""))
    if len(app.parser.positionalArguments()) > 1:
        print("Only one config directory can be specified!", file=sys.stderr)
        sys.exit(1)

    app.run()
