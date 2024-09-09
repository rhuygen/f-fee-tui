# Roadmap

## Startup of the App

- [ ] During startup we can check a number of things:
	- is the F-DPU running?
	- are the AEU CS sub-processes running?
    - What do we do when any of those fail? Report this on the screen and wait? Provide a retry button?

## Widgets

### DEB Mode

- [ ]  The DEB mode shall be updated from the DEB HK instead of the Register Map. The register map might be out of sync with the F-FEE for several reasons (mainly synchronisation issues). The DEB HK is sent on every cycle right after the timecode and accurately reflects the state of the DEB.

### DEB Commanding

- [ ] Implement Set FPGA defaults
- [ ] Implement Sync register map
- [x] Fully implement the Immediate ON Sequence

### AEB Mode

- [x] The AEB State shall be determined from the AEB HK data that is sent every cycle.

### AEB Commanding

- [x] Implement AEB Power ON/OFF commands
- [x] Implement AEB mode changing commands

### Running an SFT

### AEU State and commanding

### RMAP Protocol

- [ ] This needs specific commanding in the F-DPU to create an RMAP packet and send it over transport.

## Monitoring

- [x] Monitoring is a background thread that connects to the F-DPU and the DATA_DISTRIBUTION_PORT.
- [ ] Do we also need monitoring on the MONITORING_PORT?
- [ ] Should we provide a mechanism to request updates from the monitoring at regular intervals (say 2.5s) instead of letting the Monitoring thread handle this. We could do this with the following line (add in on_mount() after starting the thread). The poll interval can be a setting of the App.
	```python
	self.set_interval(self._poll_interval, self._monitoring_thread.schedule_update)
	```
	The Monitor Thread then would implement the `schedule_update()` method. In the while loop, check for the `_update_requested.is_set()` event and then post the messages. The Thread can gather information and only release it when an update is requested.

	```python
	def schedule_update(self) -> None:
        self._update_requested.set()
    ```
 
- [ ] Can the monitor thread handle multiple channels to monitor? Which channels would that be?
  - The core services MONITORING_PORT to report on CPU and memory usage, etc.
  - The Data Dumper MONITORING_PORT for TIMECODES, HDF5_FILENAME
  - The DPU DATA_DISTRIBUTION_PORT for Register Maps HK packets, etc.

- [ ] Shall we try to implement monitoring asynchronously instead of with threads?  

## Commanding

- [x] How are we going to implement commanding? In a similar background thread like Monitoring or with individual workers? -> Implemented a Commanding Thread.
- [x] Implement AEB Power ON/OFF commanding
- [ ] Implement AEB mode change commanding
- What about non FEE related commands that are nevertheless useful?
  - start/end observation
  - 


## Help Panel

- [ ] Add global commands to the Help panel
  - What is a good command to add? Diagnostics?
  - The Help panel is focus aware and displays help that is given in the HELP class variable.
