
This terminal tool allows you to monitor and command the Fast Front-End Electronics of the PLATO F-CAM. 


## Global keys

| Key         | Command                  |
|-------------|--------------------------|
| `F1`        | This help                |
| `CTRL-c, q` | Quit the application     |
| `d`         | Toggle dark/light theme  |
| `CTRL-k`    | Toggle commanding mode   | 



On the top of the terminal there are the state monitoring panels. The top left panel is the DEB State and shows in which mode the DEB currently is. The middle panel is the AEB State and shows – for each of the AEBs – in which state it is or transfers to. The top right panel visualises the settings of the `DTC_IN_MOD` parameter and shows which SpaceWire link is used and which AEB CCD side is transferred over that SpaceWire link.

The lower part of the terminal is dedicated to simple commanding of the F-FEE. You can change the DEB mode by pressing the corresponding button. Please remember that there is a strict flow of control to go from one DEB mode to the next. 

The commanding buttons are disabled by default when the App is started. This is done to prevent accidentally commanding the F-FEE. Commanding can be toggled ON/OFF with `CTRL-k`. 

TBW
