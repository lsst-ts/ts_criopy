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

from PySide2.QtWidgets import (
    QWidget,
    QGridLayout,
    QPushButton,
    QStyle,
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QFormLayout,
    QDoubleSpinBox,
    QSizePolicy,
)
from PySide2.QtCore import Signal

import astropy.units as u

__all__ = ["DirectionPadWidget"]


class DirectionPadWidget(QWidget):
    """Widget displaying direction pad - allows to move and rotate XYZ.

    Shows buttons to translate and rotate shape in 3D space. Translation is in
    meters, with step size set in mm. Rotation is set in degrees, with step
    size in arcseconds. Defaults are reasonable for mirror movement - 1mm step
    in translation, and 10 arcsec step in rotation. Ranges are assumed to be
    7mm for translation (M1M3 maximum is 6mm) and 60arcsec for rotation (where
    max range is about 1arcmin).
    """

    """Emitted when user push a button/changes target position. Only parameter

    Parameters
    ----------
    list : `list`
        6 member array, holding new X Y Z translations and X Y Z
        rotations.
    """
    positionChanged = Signal(list)

    def __init__(self):
        super().__init__()

        self.position = [0.0] * 6

        def _positionChanged(index, change):
            self.position[index] += change
            self.positionChanged.emit(self.position)

        def positionButton(icon, text, index, delta, deltaScale):
            but = QPushButton(icon, text)
            but.clicked.connect(
                lambda: _positionChanged(index, delta.value() * deltaScale)
            )
            return but

        style = QApplication.instance().style()

        def addArrowsBox(title, indexOffset, scale):
            layout = QGridLayout()

            deltaSB = QDoubleSpinBox()
            deltaSB.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)

            if title == "Translation":
                deltaSB.setRange(-7, 7)
                deltaSB.setDecimals(3)
                deltaSB.setValue(1.0)
            else:
                deltaSB.setRange(-60, 60)
                deltaSB.setDecimals(2)
                deltaSB.setValue(10.0)

            setattr(self, "delta_" + title, deltaSB)

            deltaF = QFormLayout()
            deltaF.addRow("Delta", deltaSB)

            layout.addLayout(deltaF, 0, 0, 1, 3)

            layout.addWidget(
                positionButton(
                    style.standardIcon(QStyle.SP_ArrowUp),
                    "X+",
                    0 + indexOffset,
                    deltaSB,
                    scale,
                ),
                1,
                1,
            )
            layout.addWidget(
                positionButton(
                    style.standardIcon(QStyle.SP_ArrowDown),
                    "X-",
                    0 + indexOffset,
                    deltaSB,
                    -scale,
                ),
                3,
                1,
            )
            layout.addWidget(
                positionButton(
                    style.standardIcon(QStyle.SP_ArrowLeft),
                    "Y-",
                    1 + indexOffset,
                    deltaSB,
                    -scale,
                ),
                2,
                0,
            )
            layout.addWidget(
                positionButton(
                    style.standardIcon(QStyle.SP_ArrowRight),
                    "Y+",
                    1 + indexOffset,
                    deltaSB,
                    scale,
                ),
                2,
                2,
            )
            layout.addWidget(
                positionButton(
                    style.standardIcon(QStyle.SP_ArrowUp),
                    "Z+",
                    2 + indexOffset,
                    deltaSB,
                    scale,
                ),
                1,
                4,
            )
            layout.addWidget(
                positionButton(
                    style.standardIcon(QStyle.SP_ArrowDown),
                    "Z-",
                    2 + indexOffset,
                    deltaSB,
                    -scale,
                ),
                3,
                4,
            )

            ret = QGroupBox(title)
            ret.setLayout(layout)
            return ret

        layout = QHBoxLayout()
        layout.addWidget(addArrowsBox("Translation", 0, u.mm.to(u.meter)))
        layout.addWidget(addArrowsBox("Rotation", 3, u.arcsec.to(u.deg)))

        self.setLayout(layout)

    def setPosition(self, position):
        """Set current pad position.

        Parameters
        ----------
        position : `iterable`
            New position. Button offsets would take this position as starting
            point.
        """
        self.position = list(position)
