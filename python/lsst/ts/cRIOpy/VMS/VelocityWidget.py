# This file is part of cRIO/VMS GUI.
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

__all__ = ["VelocityWidget"]

from .CacheTimeWidget import CacheTimeWidget

import numpy as np


class VelocityWidget(CacheTimeWidget):
    """Display signal as velocity (single acceleration integral).

    Parameters
    ----------
    title : `str`
        QDockWidget title and object name.
    cache : `VMSCache`
        Data cache.
    toolBar : `ToolBar`
        Provides getFrequencyRange() method.
    channels : `[(sensor, axis)]`
        Enabled channels.
    """

    def __init__(self, title, cache, SAMPLE_TIME, toolBar, channels=[]):
        super().__init__(title, cache, SAMPLE_TIME, toolBar, channels)

    def calculateValues(self, timestamps, signal):
        if len(signal) <= self.integralBinning:
            return (None, None)

        velocity = np.trapz(
            np.reshape(
                signal[: len(signal) - len(signal) % self.integralBinning],
                (-1, self.integralBinning),
            ),
            axis=1,
        )

        return (
            [
                (
                    timestamps[r * self.integralBinning]
                    + timestamps[(r + 1) * self.integralBinning - 1]
                )
                / 2.0
                for r in range(len(velocity))
            ],
            velocity,
        )
