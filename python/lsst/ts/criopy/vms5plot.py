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

import argparse
import re

import h5py
import matplotlib.pyplot as plt


def type_h5file(filename: str) -> h5py.File:
    try:
        return h5py.File(filename)
    except FileNotFoundError:
        raise argparse.ArgumentTypeError(f"Cannot open {filename}!")
    except IsADirectoryError:
        raise argparse.ArgumentTypeError(
            f"{filename} is a directory, filename expected!"
        )


def type_axis(axis: str) -> str:
    if re.match("[\\d%] [XYZ%]", axis) is None:
        raise argparse.ArgumentTypeError(f"Invalid axis name {axis}!")
    return axis


def run() -> None:
    parser = argparse.ArgumentParser(description="Plot H5py datafiles")
    parser.add_argument(
        "-a",
        type=type_axis,
        dest="axes",
        help="Axis to plot",
        default=[],
        action="append",
    )
    parser.add_argument("--frequency", type=float, help="Sampling frequency")
    parser.add_argument(
        "--NFFT",
        type=int,
        default=1024,
        help="Number of data points used in each block for the FFT",
    )
    parser.add_argument(
        "--raw", type=int, help="Number of raw datapoints to plot", default=-1
    )
    parser.add_argument(
        "h5py", type=type_h5file, nargs="+", help="HDF5 file(s) to plot"
    )

    args = parser.parse_args()

    if args.frequency is None:
        ts = args.h5py[0]["timestamp"]
        args.frequency = 1 / (ts[2] - ts[1])
        print(f"Frequency wasn't specified, calculated {args.frequency}.")

    all_axes = list(args.h5py[0].keys())[:-1]

    axes = []

    if args.axes == []:
        axes = list(args.h5py[0].keys())[:-1]
        print(f"Axes not specified, add all ({', '.join(axes)}).")
    else:
        for a in args.axes:
            if "%" in a:
                c_axes = []
                p = re.compile(a.replace("%", "."))
                for t_a in all_axes:
                    if p.match(t_a) is not None:
                        c_axes.append(t_a)
                print(f"{a} -> {', '.join(c_axes)}")
                axes += c_axes
            else:
                axes.append(a)

    fig, ax = plt.subplots(len(args.h5py), 1 + len(axes))

    for i, f in enumerate(args.h5py):
        if len(args.h5py) > 1:
            c_a = ax[i]
        else:
            c_a = ax
        print(f"Sub-plot {i} ({f.filename}).")
        c_a[0].set_title(f"Raw {f.filename}")
        c_a[0].plot(f["timestamp"][: args.raw], f["1 X"][: args.raw])
        for j, a in enumerate(axes):
            print(f"Sub-plot {i}, {j+1} ({a}).")
            c_a[j + 1].set_title(f"PSD {a}")
            c_a[j + 1].psd(f[a], NFFT=args.NFFT, Fs=args.frequency)

    plt.show()
