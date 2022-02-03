# Python GUI for M1M3 Support System

## Applications

Applications are located in bin directory.
Before running those, please make sure that required Python packages (in python directory) are available:

```bash
python3.8 -c "from lsst.ts.cRIOpy.GUI import *"
```

The above command shall pass without error.

### M1M3GUI

GUI/EUI for M1M3 static supports.
Allows to perform various M1M3 operations, including FA bump testing and manual mirror positioning.
Requires [ts_m1m3support](https://github.com/lsst-ts/ts_m1m3support) CSC running.

#### Run M1M3GUI with the Simulator

To run the GUI with the CSC in simulation mode under the docker container, you can build the docker image of CSC first by:

```bash
git clone https://github.com/lsst-ts/ts_m1m3support.git
cd ts_m1m3support
docker build -t m1m3sim .
```

Enter the container with the display setting (use Mac OS as an example):

```bash
xhost +
IP=$(ifconfig en0 | grep inet | awk '$1=="inet" {print $2}')
docker run -it --rm -e DISPLAY=${IP}:0 -v ${path_to_local_ts_cRIOpy}:/home/saluser/ts_cRIOpy -v /tmp/.X11-unix:/tmp/.X11-unix m1m3sim:latest
```

Please note XQuartz settings should allow any client: [Running GUI’s with Docker on Mac OS X](https://cntnr.io/running-guis-with-docker-on-mac-os-x-a14df6a76efc).

Inside the container, do:

```
conda install -y pyside2 asyncqt h5py
cd ts_cRIOpy/
setup -kr .
export LSST_DDS_PARTITION_PREFIX=test
cd bin/
M1M3GUI
```

You have to set **LSST_DDS_PARTITION_PREFIX** variable to match your environment. 

After the EUI is running, you can use another terminal session to enter the same container by:

```bash
docker exec -it ${container_id} bash
```


Built the M1M3 simulator by following: [ts_m1m3support](https://github.com/lsst-ts/ts_m1m3support/blob/main/README.md).
Inside the container, do:

```bash
source ~/.setup_dev.sh
cd repos/ts_m1m3support
export LSST_DDS_PARTITION_PREFIX=test
./ts-M1M3supportd -c SettingFiles/ -f
```

**LSST_DDS_PARTITION_PREFIX** variable in simulator must match EUI settings.
Please run the EUI first.
Only after EUI is running, run the simulator.
You can then restart the simulator as needed.

### M1M3TSGUI

GUI/EUI for M1M3 thermal system.
Allows TS monitoring and performing various M1M3 thermal system operations.
Requires [ts_m1m3thermal](https://github.com/lsst-ts/ts_m1m3thermal) CSC running.

### VMSGUI

GUI/EUI for VMS (Vibration Monitoring System).
Plots various graphs from VMS, including PSD/FFT/DFT.
Requires [ts_vms](https://github.com/lsst-ts/ts_vms) CSC running.

### VMSlogger

CLI for VMS logging.
Can save VMS data as cvs or, with optional [h5py](https://www.h5py.org/), as HDF5.

## Dependencies

* Python 3.8
* [PySide2 (QtCore, QtGui, QtCharts, QtWidgets)](https://pypi.org/project/PySide2)
* [asyncqt](https://pypi.org/project/asyncqt)
* [LSST ts_salobj](https://github.com/lsst-ts/ts_salobj)
* [h5py](https://pypi.org/project/h5py/)

## Prerequsities

```bash
make_idl_files.py MTM1M3 MTM1M3TS MTMount MTVMS
```

## SALComm

Heart of the application is SALComm. The module links ts_salobj callbacks with Qt Signals.
Names of signals matches SAL events and telemetry topics. This allows for simple integration of DDS/SAL and GUI widgets. Widgets in need to receive SAL data accept SALComm as constructor parameter, and after setting up the widget SALComm provided Qt Signals are connected to slots in the widget.

## Custom widgets

Qt Slots are decorated with @Slot and usually not documented, as the only
functions is to update widgets with data received from SAL/DDS. Please see [PySide2 documentation](https://wiki.qt.io/Qt_for_Python_Signals_and_Slots) and [SALComm](SALComm.py) for details how this works.
