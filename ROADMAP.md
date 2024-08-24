# Roadmap

## Startup of the App

- During startup we can check a number of things:
	- is the F-DPU running?
	- are the AEU CS sub-processes running?
    - What do we do when any of those fail?

## Widgets

### DEB Mode

### DEB Commanding

### AEB Mode

### AEB Commanding

### Running an SFT

### AEU State and commanding

### RMAP Protocol

- This needs specific commanding in the F-DPU to create an RMAP packet and send it over transport.

### Monitoring

- Monitoring is a background thread that currently connects to the F-DPU and the DATA_DISTRIBUTION_PORT. We also need monitoring on the MONITORING_PORT

### Commanding

- How are we going to implement commanding? In a similar background thread like Monitoring or with individual workers?
- 
