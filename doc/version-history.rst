.. _Version_History:

===============
Version History
===============

v0.14.0
-------

* M1M3 Thermal Scanner Thermocouples ("Glass Temperature") display in M1M3TSGUI.

v0.13.1
-------

* Fix multiple axis plotting.

v0.13.0
-------

* Show occurrence of ilcWarning messages.
* Fix data reload - issue only one request to load data.

v0.12.1
-------

* Show warning in M1M3 Support System's "Slew controller" page when slew is active.

v0.12.0
-------

* Replay widget - replays historic data in GUIs, displays replay progress.
* Allow user select the EFD instance, create EfdClient in async thread.
* Confirm mirror raising and lowering.

v0.11.0
-------

* Display FCU values in M1M3TSGUI
* Show mirror boundaries (M1, M3, center hole)
* Improved M1M3TSGUI Mixing valve display
* M1M3TSGUI table backgrounds colors for FCU with problems
* Show Glycol/EGW pump errors
* Display far neighbor factor

v0.10.0
-------

* M1M3 FA parallel bump tests
* WaitCompression state

v0.9.0
------

* Support for automatic FCU's heaters PWM (~power) control.
* VMSLogger Kafka
* Hardpoint Compression waiting state

v0.8.3
------

* M1M3 support system remote parameters for swifter Kafka connection
* More code refactoring
* Update conda builder version for conda package

v0.8.2
------

* Add elevation forces to M1M3SIMGUI (so also to ForceCalculator class)
* Add ApplySetpoint command support to the M1M3TSGUI
* Balance forces can be switched on/off only in engineering mode
* Show time deltas on M1M3 TS glycol circulation page
* Move simulator & aceleration tools into ts_m1m3_utils
* Bug-fixes (EUI labels, omitted API changes)

v0.8.1
------

* Correctly show small values (= calibrations)
* Improve hardpoint display
* Improve IMS display
* Display outerLoop data
* Fixed mypy issues

v0.8.0
------

* Migrated to PySide6
* Changes to conda/test builds

v0.7.0
------

* ForceActuatorForces class for data access
* Fix DCA Gain display
* fixed Conda build

v0.6.2
------

* show forces distribution per quadrant and with XYZ forces off
* BumpTestTImes class, script to retrieve bump tests runs
* fix for new qasync library
* shows heartbeats in VMSGUI
* Tools for DC accelerometers transformations
* Disable slew controller changes when slew flag is active
* improved acceleration - forces fits
* improved unit displays
* improved command line processing

v0.6.1
------

* fix conda package build

v0.6.0
------

* M1M3 Thermal System GUI (M1M3TSGUI) changed to use M1M3 SS look & feel
* Commands to pause and resume mirror raising or lowering
* Fix M1M3 tests, remove bin scripts
* FATable moved to ts_xml

v0.5.0
------
* LVDT and Slew Controller pages

v0.4.1
------
* Fix conda recipe.

v0.4.0
------
* Common EUI mechanism - EUIWindow, CSCControlWidget classes
* LTGUI
* Code MyPy compliant
* use lowercase for directory/modules names
* asyncqt (Qt async loop) replaced with qasync

v0.3.0
------

* displays improvements

v0.2.0
------

* UnitsClasses, various data binding classes
* formalized execution
* VMSLogger

v0.1.0
------

* Initial working version.
