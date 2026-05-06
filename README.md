<img src="docs/_banner.svg" width="800px">

# Garden of Eden

Truly own that which is yours!

If you are interested in collaborating please review the [CONTRIBUTORS](CONTRIBUTORS.md) for commit styling guides.

## Project Status & Milestones

Work in progress. We should be picking up some steam here to give the DYI community the features you deserve.

[Milestones](https://github.com/Nomar383/garden-of-eden/milestones)

![image](https://github.com/user-attachments/assets/403248f5-b7d4-4cb1-921a-0458f515f387)


## Table of Contents

- [Garden of Eden](#garden-of-eden)
  - [Project Status \& Milestones](#project-status--milestones)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
  - [Usage](#usage)
    - [MQTT with Home Assistant](#mqtt-with-homeassistant)
    - [Testing](#testing)
    - [Quick Toggle Guide](#quick-toggle-guide)
  - [Hardware Overview](#hardware-overview)
  - [Design Decisions](#design-decisions)
    - [Python Version 3.6 \>=](#python-version-36-)
    - [Delays in Reading Temp/Humidity data](#delays-in-reading-temphumidity-data)
    - [GPIO](#gpio)
  - [Folder Structure](#folder-structure)

## Getting Started

### Prerequisites

Start with a clean install of Linux. Use the [RaspberryPi Imager](https://www.raspberrypi.com/software/). This project was developed for the **Raspberry Pi Zero 2 W** and has not been tested on the earlier Raspberry Pi Zero W. Ensure ssh and wifi is setup. Once the image is written, pop the SDcard into the pi and ssh into it.

```bash
# clone repo
git clone git@github.com:Nomar383/garden-of-eden.git
cd garden-of-eden 
```

Update the `.env` with mqtt broker info

```
cp .env-dist .env
nano .env
```

Install dependencies, and run services pigpiod, mqtt.service

```bash
./bin/setup.sh
```

Ensure the pigpiod daemon is running

```
sudo systemctl status pigpiod
sudo systemctl status mqtt.service
```

## Usage

### MQTT with Home Assistant

For broker setup, Home Assistant integration, and local testing, see **[docs/MQTT.md](docs/MQTT.md)**.

The MQTT service (`mqtt.py`) is the sole entry point for this project. It connects to an MQTT broker, publishes Home Assistant discovery messages for auto-configuration, and handles all sensor reading, light/pump control, and camera image publishing over MQTT.

### Testing

Activate python venv `source venv/bin/activate`

```bash
# unit tests
python -m unittest -v

# individual tests
python tests/test_distance.py
```

### Quick Toggle Guide

You can use the physical button to control lights and pump.

> Ensure your press is quick and within the time frame for the action to register correctly. The press time window can be modified directly in the `mqtt.py` file.

- **One Press** (within 1 second): 
  - **Action**: Toggles the **Lights** on or off. 
  - **Description**: A single, swift press will illuminate or darken your space with ease.

- **Two Presses** (within 1 second): 
  - **Action**: Toggles the **Pump** on or off.
  - **Description**: Need to water the garden or fill up the pool? Double tap for action!

## Hardware Overview

Sensors, pins, cameras, and diagrams are documented in **[docs/Hardware-Overview.md](docs/Hardware-Overview.md)**.

## Design Decisions

### Python Version 3.6 >=

Minimum python version of 3.6 to support `printf()`

### Delays in Reading Temp/Humidity data

Reading sensor values  with inherently long delays and responding to the REST API. To minimize the delay in subsequent readings the value is cached and given if another read occurs within two seconds.

### GPIO

Using `gpiozero` to leverage `pigpio` daemon which is hardware driven and more efficient.This ensures better accuracy of the distance sensor and is less cpu intensive when using PWMs.

## Folder Structure

```text
garden-of-eden/
├── config.py
├── mqtt.py
├── requirements.txt
├── app/
│   └── sensors/
│       ├── __init__.py
│       ├── temp_humidity_shared.py
│       ├── camera/
│       │   ├── __init__.py
│       │   └── camera.py
│       ├── distance/
│       │   ├── __init__.py
│       │   └── distance.py
│       ├── humidity/
│       │   ├── __init__.py
│       │   └── humidity.py
│       ├── light/
│       │   ├── __init__.py
│       │   └── light.py
│       ├── pcb_temp/
│       │   ├── __init__.py
│       │   ├── pcb_temp.py
│       │   └── over_temp_monitor.py
│       ├── pump/
│       │   ├── __init__.py
│       │   ├── pump.py
│       │   └── pump_power.py
│       └── temperature/
│           ├── __init__.py
│           └── temperature.py
├── bin/
│   ├── setup.sh
│   ├── get-sensor-data.sh
│   ├── light.sh
│   ├── water.sh
│   ├── show-mqtt-logs.sh
│   └── take-pictures.sh
├── docs/
│   ├── MQTT.md
│   ├── Hardware-Overview.md
│   └── ...
├── automations/
└── tests/
    ├── __init__.py
    ├── test_distance.py
    ├── test_light.py
    └── test_pump.py
```
