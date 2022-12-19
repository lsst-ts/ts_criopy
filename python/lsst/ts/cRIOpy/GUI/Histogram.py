# This file is part of cRIOpy package.
#
# Developed for the LSST Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https: //www.lsst.org).
# See the COPYRIGHT file at the top - level directory of this distribution
# for details of code ownership.
#
# This program is free software : you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.If not, see < https:  // www.gnu.org/licenses/>.

import numpy as np

from PySide2.QtCore import Qt
from PySide2.QtCharts import QtCharts


class Histogram(QtCharts.QChart):
    def __init__(self, parent=None, wFlags=Qt.WindowFlags(), nbins=50):
        """
        Parameters
        ----------
        nbins : `int`, optional
            Number of bins to plot. Default to None - autoscale bins.
        """
        super().__init__(parent, wFlags)
        self.nbins = nbins

        self.set = QtCharts.QBarSet("Data")

        self.serie = QtCharts.QBarSeries()
        self.serie.append(self.set)

        self.addSeries(self.serie)

        self.yAxis = QtCharts.QValueAxis()
        self.addAxis(self.yAxis, Qt.AlignLeft)

        self.xAxis = QtCharts.QBarCategoryAxis()
        self.addAxis(self.xAxis, Qt.AlignBottom)

        self.legend().setVisible(True)
        self.legend().setAlignment(Qt.AlignBottom)

    def update(self, values):
        hist, bin_edges = np.histogram(values, self.nbins)
        self.set = QtCharts.QBarSet("Data")
        self.set.append(list(hist))

        self.removeSeries(self.serie)

        self.serie = QtCharts.QBarSeries()
        self.serie.setBarWidth(1)
        self.serie.append(self.set)
        self.addSeries(self.serie)

        self.xAxis.setCategories([str(c) for c in bin_edges[:-1]])

        self.yAxis.setRange(0, max(hist))

        self.serie.attachAxis(self.yAxis)
        self.serie.attachAxis(self.xAxis)
