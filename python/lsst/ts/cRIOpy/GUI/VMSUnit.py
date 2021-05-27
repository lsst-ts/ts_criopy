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

__all__ = ["units"]

units = ["m/s<sup>2</sup>", "mm/s<sup>2</sup>", "g", "mg", "&micro;g"]
menuUnits = ["m/s^2", "mm/s^2", "g", "mg", "ug"]

G_TO_MS2 = 9.80665
MS2_TO_G = 1 / G_TO_MS2


def coefficients(unit):
    n_i = units.index(unit)
    _matrix = [1, 1000.0, MS2_TO_G, MS2_TO_G * 1000.0, MS2_TO_G * 1000000.0]
    return _matrix[n_i]


def deltas(current_unit, new_unit):
    return coefficients(new_unit) / coefficients(current_unit)
