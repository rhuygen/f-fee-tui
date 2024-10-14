# CHANGELOG for the F-FEE TUI Project

## Version 0.6.1 — 14/10/2024

- [0.6.1] updated the help screen content.
- [0.6.0] maintenance release to solve refactoring problems and keep Command thread running even when no DPU CS is running.
  - Command thread would crash when the proxies could not connect to their control servers. That has been solved now by catching the exception and retrying to connect after 10 seconds.
  - Solved the problem of the Queue join() when the queue contained commands at app termination. Those commands are printed to the console on exit.
  - Several `post_message()` calls were sent to the App instead of the master screen and were not visible.
  - Added a button to end the current observation.
  - Some code refactoring/simplification in `InfoBar`.

## Version 0.5.6 — 01/10/2024

- [0.5.6] the monitoring panels for DEB mode, AEB state, and DTC_IN_MOD will now be cleared after 10s of inactivity.

## Version 0.5.5 — 30/09/2024

- [0.5.5] the DEB mode is now not set to ON by default at startup.
- [0.5.4] fix a bug where I used `setsockopt_string` instead of `setsockopt`

## Version 0.5.3 — 29/09/2024

- [0.5.3] Make sure the Help screen is pushed / showed only once
- [0.5.2] In the workers Monitor class, the subscription to the data distribution channel is restricted to the RegisterMap and HK data. 
- [0.5.2] Updates to the in-app help.

## Version 0.5.1 — 25/09/2024

The definition of left and right side of the CCD have been changed from:

- 1: left — E into 0: left — F
- 0: right — F into 1: right — E


- [0.5.0] Fixed the labeling on the DTC_IN_MOD panel, i.e. F = LEFT, E = RIGHT
- [0.5.1] Fixed the rest of the DTC_IN_MOD panel 

## Version 0.4.3 — 24/09/2024

The frame errors are represented as a Sparkline at the bottom of the DTC_IN_MOD panel. It represents accumulated errors for the SpW transfer buffer overflow. The accumulation is for the entire lifetime of the app. You can reset the error count using the command 'Reset frame errors' from the command palette.

- [0.4.3] Added the command 'Reset frame errors' to the command palette.
- [0.4.2] Fix the mapping of OUTBUFF_x to AEB/DTC_IN_MOD. This is what is contained in the Setup in `camera.fee.ccd_numbering.AEB_TO_T_IN_MOD`
- [0.4.1] Put `outbuff` accumulated values in Sparkline tooltip.
- [0.4.0] Added a sparkline to the DTC_IN_MOD panel with accumulated errors on the SpW transmit buffer.

## Version 0.3.0 — 22/09/2024

- Added an info bar at the bottom of the screen with status LEDs for the core services and some important other processes. 
- Added a help screen behind the F1 key. Further help needs to be written.

## Version 0.2.1 — 20/09/2024

- [0.2.1] fix name of message handling function: on_dtc_in_mod_changed()
- [0.2.0] Introduce monitoring and reporting of the DTC_IN_MOD settings in a new monitoring panel

## Version 0.1.17 — 10/09/2024

- Added a general command TAB with a button to set the FPGA defaults.
- Hitting 'q' will now also quit the app.

## Version 0.1.16 — 09/09/2024

- The IMMEDIATE ON commands now implements the Immediate ON Sequence (Section 9.2 in F-FEE CD ICD v2.6). It will bring the DEB to ON mode, then command the AEBs to INIT mode, wait for 6.0s, then Power OFF the AEBs.

## Version 0.1.15 — 09/09/2024

- Added POWER-UP and POWER-DOWN states for the AEB State widget

## Version 0.1.14 — 04/09/2024

- Added --version commandline option
- Fixed a typo OPER_MODE -> OPER_MOD

## Version 0.1.13 — 03/09/2024

- Implemented the commanding of the AEB mode/state
- Monitoring is now done based on the DEB and AEB HK data instead of the register map (which might be wrong when synchronisation problems occur)
- Again, fixed a bug in the AEB ON/OFF state setting

## Version 0.1.12 — 02/09/2024

- Fix a problem when AEB state is OFF, other states were not cleared

## Version 0.1.11 — 02/09/2024

- The AEB State panel is now fully functional, i.e. also the INIT, CONFIG, IMAGE, and PATTERN states are reported.

## Version 0.1.10 — 29/08/2024

- Added platform information in subtitle

## Version 0.1.9 — 29/08/2024

- Added tooltips for DEB and AEB commanding

## Version 0.1.8 — 28/08/2024

- Added AEB Commanding widget
- AEB Commanding for powering ON/OFF AEBs 

## Version 0.1.7 — 28/08/2024

- Added ProblemDetected message for reporting a problem
- Updated TimeoutReached message with a message argument
- Added a new widget representing the AEB states
- Added AebStateChange message and the Monitor Thread now handle AEB state changes
- LEDs now can take a states argument to set the ON and OFF representation

## Version 0.1.6 — 27/08/2024

- Removed the example where the STANDBY LED would toggle if you pressed the 's' key. The DEB modes are now handled by the Monitoring Thread.
- Added a Commanding Thread. The App passes commands with their arguments to this thread through a Queue. The thread reads the commands from the queue and executes the command. 
- Added DEB Commanding panel with buttons to set the mode of the DEB.

## Version 0.1.5 — 24/08/2024

- Added the `CHANGELOG.md` and a `ROADMAP.md`.
- As an example how to change the LED color, I added a 's' toggle to change to STANDBY mode. This will set the STANDBY led to green and the ON mode led back to red.
- Refactored a bit by putting classes in their own module file.
- Implemented a background thread that will monitor the F-DPU DATA_DISTRIBUTION message channel and report changes to the TUI. Changes are posted to the main App that will update the DEB Mode Settings. Currently only DEB mode changes. 

## Version 0.1.4 — 23/08/2024

- The App is now a Textual app.
- It doesn't do anything yet, except show a DEB mode widget with labels and state LEDs.
- There is no logic behind the widget yet, e.g. to change the mode depending on the real DEB mode.

## Version 0.1.0 — 22/08/2024

- This is the initial version of the Project.
- This is only the skeleton for the project itself with a `pyproject.toml`.
- The project is ready to be uploaded to PyPI.
