# CHANGELOG for the F-FEE TUI Project

## Version 0.1.5 — 23/08/2024

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
