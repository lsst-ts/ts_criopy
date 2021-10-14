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

## Installing packages

The most troublesome is dds. That can be build from source, or a wheel package
needs to be copied from previously build package.

GUI requires Python 3.8, which is best build from source.

[Download Python3.8](https://www.python.org/ftp/python/3.8.8/Python-3.8.8.tar.xz)

```bash
curl -O https://www.python.org/ftp/python/3.8.8/Python-3.8.8.tar.xz
tar xJf Python-3.8.8.tar.xz
cd Python-3.8.8
./configure
make
make test
sudo make install
```

Most of the remaining packages can be installed through pip:

```bash
pip3.8 install boto3 moto pyaml asyncqt PySide2 jsonschema
```

dds package can be build from OSPL source (installed from RPM from nexus), 
see [instructions](https://istkb.adlinktech.com/article/using-opensplice-dds-with-python/).

QtWayland needs to be installed so GUI/EUI can launch (otherwise you will see
complains about missing plugin, _"qt.qpa.plugin: Could not load the Qt platform
plugin "xcb" in "" even though it was found."_

```bash
sudo yum install qt5-qtwayland
```

SAL needs to be setup. For that, ts_xml, ts_sal, ts_salobj, ts_idl,
ts_ddsconfig and ts_utils modules shall be cloned from GitHub (with appropriate
version) and put into PYTHONPATH. Environmental values needs to be setup for
that. The base minimum is (assuming all packages are cloned into $HOME, and
OpenSpliceDDS V6.10.4 is installed from RPM):

```bash
export OSPL_HOME=/opt/OpenSpliceDDS/V6.10.4/HDE/x86_64.linux
export LSST_DDS_DOMAIN_ID=0
export OSPL_URI=file://$HOME/ts_ddsconfig/config/ospl-shmem.xml
export LSST_DDS_QOS=file://$HOME/ts_ddsconfig/qos/QoS.xml
export LSST_DDS_PARTITION_PREFIX=summit
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$OSPL_HOME/lib

cd $HOME
source ts_sal/setup.env

export PYTHONPATH=:$HOME/ts_xml/python/:$HOME/ts_ddsconfig/python/:$HOME/ts_salobj/python/:$HOME/ts_idl/python:$HOME/ts_sal/python:$HOME/ts_utils/python:$HOME/ts_cRIOpy/python
```

```bash
make_idl_files.py MTM1M3 MTM1M3TS MTMount MTVMS
```

Only after that ospl can be started and M1M3GUI can be run (_ospl start doesn't
need to issued if it's already running):

```bash
ospl start
cd ts_cRIOpy
./bin/M1M3GUI
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
