
This terminal tool allows you to monitor and command the Fast Front-End Electronics of the PLATO F-CAM. 


## Global keys

| Key         | Command                  |
|-------------|--------------------------|
| `F1`        | This help                |
| `CTRL-c, q` | Quit the application     |
| `d`         | Toggle dark/light theme  |
| `CTRL-k`    | Toggle commanding mode   | 


## Brief description

At the top part of the terminal there are the state monitoring panels. The top left panel is the DEB State and shows in which mode the DEB currently is. The middle panel is the AEB State and shows – for each of the AEBs – in which state it is or to which state it transfers to. The top right panel visualises the settings of the `DTC_IN_MOD` parameter and shows which SpaceWire link is used and which AEB CCD side is transferred over that SpaceWire link.

The lower part of the terminal is dedicated to simple commanding of the F-FEE. You can change the DEB mode by pressing the corresponding button. Please remember that there is a strict flow of control to go from one DEB mode to the next. In the middle panel 'AEB Commanding' you can – per AEB unit – power ON/OFF the AEB and change its state. Select the TAB for the AEB that you want to command. Also for the AEBs there is a strict flow control for changing their state.

In the lower right 'General Commanding' panel we will provide more generic commands to configure or reset the F-FEE.

The commanding buttons are disabled by default when the App is started. This is done to prevent accidental commanding of the F-FEE. Commanding can be toggled ON/OFF with `CTRL-k`. 

## Detailed Panel descriptions

### DEB mode

This panel indicates the mode of the DEB. This is a translation of the `OPER_MOD` parameter from the DEB housekeeping. Housekeeping data is requested after ever timecode and will therefore be updated every 2.5s.

### AEB State

This panel indicates the state of each of the AEBs. This is a translation of the `AEB_STATUS` parameter from the AEB housekeeping. Also AEB housekeeping data is requested after every timecode and updated accordingly. 

### DTC_IN_MOD

This panel shows which CCD image data is send over which SpaceWire link. It is a translation of the DTC_IN_MOD `Tx_IN_MOD` parameters in the Register Map. The possible combinations are shown in light grey, i.e. AEB1 and AEB2 share the SpW 1 and SpW 2 links, while AEB3 and AEB4 share the SpW 3 and SpW 4 links. In our current commanding strategy, we can only read from one SpaceWire link at a time. The active SpW link will be indicated by a `x` when set. At the bottom of this panel is a sparkline that shows the accumulated errors that were detected in the `OUTBUFF_x` parameters. If this sparkline shows red boxes, it means a SpaceWire transmit buffer overflow was detected for that AEB. If you hover the sparkline, it will show the actual number of errors detected. You can reset these errors by executing the command `Reset frame errors` from the command panel `CTRL-p`.
