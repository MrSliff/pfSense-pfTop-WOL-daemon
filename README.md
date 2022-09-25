# Python Script to wake up hosts in with pftop states

## Disclaimer
This script is still in development. As soo as its done, this disclaimer will be removed.

## Description
This script is intended to wake up my unraid server as soon as a connection is attempted to it. 

Since the Wake-On-Lan functionality is quite unreliable on my server, i had to find another way to wake it up. The problem on my server: The network adapter sometimes goes to standby too when i send the server to sleep, so WOL packets are not recognized.

One solution i want to try is to combine this script with an Wemos S2 (ESP32-S2), which emulates a HID-Keyboard and sends a keyboard input to wake up the server.

## License

This script is open source with no restrictions in usage, feel free to use it in your environment.