# Yamaha YNC Python Controller

A Python wrapper for controlling Yamaha Audio/Video Receivers via the Yamaha Network Control (YNC) protocol over HTTP.
Still a work in progress: not all the features of the API have been implemented yet.
Tested on the RX-V481.

## Features:

- Power Management: Toggle system power and set sleep timers.
- Volume Control: Decibel-based volume setting, relative adjustments, and muting.
- Input Selection: Switch between inputs such as HDMI, Tuner, Net Radio, and Bluetooth.
- DSP & Audio: Change Sound Programs (e.g., "5ch Stereo", "Sci-Fi"), toggle Straight mode, and adjust Bass/Treble.
- Smart Status: Parses the receiver's XML state into a Python dictionary.
- Safety : By default, caps volume to prevent accidental damage.

## Installation:

You will need the requests library:
`pip install requests`

## Quick start & example:

```python

from yamaha_controller import YamahaReceiver

# Initialize the receiver with its IP address

amp = YamahaReceiver("192.168.51.156")

# Power on and switch to a specific input

amp.set_power("On")
amp.set_input("HDMI2")

# Set volume to -45.0 dB

amp.set_volume(-45.0)

# Get full system status

status = amp.get_status()
print(f"Current Input: {status['input']['friendly_name']}")
```
