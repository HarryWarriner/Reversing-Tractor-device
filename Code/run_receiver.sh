#!/bin/bash

# Bind RFCOMM channel 1
sudo rfcomm release 0
sudo rfcomm bind 0 D8:3A:DD:20:E3:25

# Small delay to ensure bind completed
sleep 2

# Run your Python script
python3 /home/harry/Reversing-Tractor-device/Code/LED-Remote-Cam.py
