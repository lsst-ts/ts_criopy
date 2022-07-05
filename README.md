# Python EUI/GUI for M1M3 Support System

Engineering / User Graphical Interface for cRIO systems. Provides generics GUI
classes as well as SALobj specific classes.

## Directory structure

Under python/lsst/ts/cRIOpy, the directories are:

* __AirCompressor__ widget for M1M3-ComCam air compressor
* __GUI__ Generic GUI widgets
  * __ActuatorsDisplay__ contains widgets to plot actuators
  * __CustomLabels__ contains plenty of QLabel childs to be used building up user interface
  * __SAL__ contains SAL bindend Labels. Please see __SALComm__ for details
  * __TimeChart__ contains QtCharts.QChart subclasses to build up real-time graphs
* __M1M3__ widgets for M1M3 support system
* __M1M3TS__ widgets for M1M3 thermal system
* __VMS__ graphs for [ts_VMS](https://github.com/lsst-ts/ts_VMS)

## Applications

Applications are located in bin directory. Before running those, please make
sure that required Python packages (in python directory) are available:

```
python3.8 -c "from lsst.ts.cRIOpy.GUI import *"
```

shall pass without error.


```
pip install .
```

shall install those commands and packages needed for running them for you.

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

# SAL binding

The GUI/EUI

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
[SALComm](tree/main/python/lsst/ts/cRIOpy/GUI/SAL/SALComm.py) for details how
this works.
