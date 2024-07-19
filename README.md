# Python EUI/GUI for M1M3 Support System

Engineering / User Graphical Interface for cRIO systems. Provides generic GUI
classes as well as SALobj specific classes.

## Directory structure

Under python/lsst/ts/criopy, the directories are:

* __aircompressor__ widget for M1M3-ComCam air compressor
* __gui__ generic GUI widgets
  * __actuatorsdisplay__ contains widgets to plot actuators
  * __custom_labels__ contains plenty of QLabel childs to be used building up user interface
  * __sal__ contains SAL bindend Labels. Please see __SALComm__ for details
  * __timechart__ contains QtCharts.QChart subclasses to build up real-time graphs
* __m1m3__ widgets for M1M3 support system
* __m1m3ts__ widgets for M1M3 thermal system
* __vms__ graphs for [ts_VMS](https://github.com/lsst-ts/ts_VMS)

## Applications

Applications are located in bin directory. Before running those, please make
sure that required Python packages (in python directory) are available:

```bash
python3.8 -c "from lsst.ts.criopy.gui import *"
```

shall pass without error.

The following command shall install those commands and packages needed for
running them for you.

```bash
pip install .
```

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

* Python 3.8 or later
* [numpy](https://numpy.org)
* [astropy](https://astropy.org)
* [PySide6 (QtCore, QtGui, QtCharts, QtWidgets)](https://pypi.org/project/PySide6)
* [qasync](https://pypi.org/project/qasync/)

For SAL etc:

* [LSST ts\_salobj](https://github.com/lsst-ts/ts_salobj)


# SAL binding

The GUI/EUI contains code which depends on ts\_salobj and related
infrastructure. Files in (and only in) python/lsst/ts/criopy/GUI directory are
generics and don't depend on ts\_salobj. All other code usually depends on
ts\_salobj, including code in GUI subdirectories (ActuatorsDisplay, SAL).

You shall be able to:

```python
from lsst.ts.criopy.gui import *
```

to get access to common GUI widgets (UnitLabel & friends, various improved
layouts,..).


## Prerequsities

```bash
make_idl_files.py MTM1M3 MTM1M3TS MTMount MTVMS
```

### PySide6 and qasync

On systems with both PySide2 and PySide6 installed, qasync library needs
QT\_API environmental variable set to pyside6.

## SALComm

Heart of the application is SALComm. The module links ts\_salobj callbacks with
Qt Signals. Names of signals matches SAL events and telemetry topics. This
allows for simple integration of DDS/SAL and GUI widgets. Widgets in need to
receive SAL data accept SALComm as constructor parameter, and after setting up
the widget SALComm provided Qt Signals are connected to slots in the widget.

## Custom widgets

Qt Slots are decorated with @Slot and usually not documented, as the only
functions is to update widgets with data received from SAL/DDS. Please see
[PySide6 documentation](https://wiki.qt.io/Qt_for_Python_Signals_and_Slots) and
[SALComm](tree/main/python/lsst/ts/criopy/SALComm/MetaSAL.py) for details how
this works.

## Running GUIs from Docker container

It's perfectly fine to run GUIs from docker container. For that, a host machine
must contain some X11 server. Docker container must be started with DISPLAY
pointing to the X11 server display, such as this:

```
docker run -ti -e DISPLAY=127.0.0.1:0.0 <container>
```
