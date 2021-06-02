# Python GUI for M1M3 Support System

## Applications

Applications are located in bin directory. Before running those, please make
sure that required Python packages (in python directory) are available:

python3.8 -c "from lsst.ts.cRIOpy.GUI import *"

shall pass without error.

### M1M3GUI 

GUI/EUI for M1M3 static supports. Allows to perform various M1M3 operations,
including FA bump testing and manual mirror positioning. Requires
[ts_m1m3support](https://github.com/lsst-ts/ts_m1m3support) CSC running.

### M1M3TSGUI

GUI/EUI for M1M3 thermal system. Allows TS monitoring and performing various
M1M3 thermal system operations. Requires
[ts_m1m3thermal](https://github.com/lsst-ts/ts_m1m3thermal) CSC running.

### VMSGUI

GUI/EUI for VMS (Vibration Monitoring System). Plots various graphs from VMS,
including PSD/FFT/DFT. Requires [ts_vms](https://github.com/lsst-ts/ts_vms) CSC
running.

### VMSlogger

CLI for VMS logging. Can save VMS data as cvs or, with optional
[h5py](https://www.h5py.org/), as HDF5.

## Dependencies

Python 3.8
[PySide2 (QtCore, QtGui, QtCharts, QtWidgets)](https://pypi.org/project/PySide2)
[asyncqt](https://pypi.org/project/asyncqt)
[LSST ts_salobj](https://github.com/lsst-ts/ts_salobj)

## Prerequsities

```bash
make_idl_files.py MTM1M3 MTM1M3TS MTMount MTVMS
```

## SALComm

Heart of the application is SALComm. The module links ts_salobj callbacks with
Qt Signals. Names of signals matches SAL events and telemetry topics. This
allows for simple integration of DDS/SAL and GUI widgets. Widgets in need to
receive SAL data accept SALComm as constructor parameter, and after setting up
the widget SALComm provided Qt Signals are connected to slots in the widget.

## Custom widgets

Qt Slots are decorated with @Slot and usually not documented, as the only
functions is to update widgets with data received from SAL/DDS. Please see
[PySide2 documentation](https://wiki.qt.io/Qt_for_Python_Signals_and_Slots) and
[SALComm](SALComm.py) for details how this works.
