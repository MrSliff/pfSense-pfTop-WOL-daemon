# Python Script to wake up hosts in pfSense with pftop states

## Disclaimer
This script is still in development. As soon as its done, this disclaimer will be removed.

## Description
This script is intended to wake up my unraid server as soon as a connection is attempted to it. 

Since the Wake-On-Lan functionality is quite unreliable on my server, i had to find another way to wake it up. The problem on my server: The network adapter sometimes goes to standby when i send the server to sleep, so WOL packets are not recognized.

One solution i want to try is to combine this script with a Wemos-S2 (ESP32-S2), which emulates a HID-Keyboard and sends a keyboard input to wake up the server. The Wemos will either subsrcibe to a MQTT Topic or will provide some kind of webhook.

A functionality to send WOL packets will also be implemented.

## Installation

Instructions on how to use this script will follow as soon as its finished

## License

This script is open source with no restrictions in usage, feel free to use it in your environment.