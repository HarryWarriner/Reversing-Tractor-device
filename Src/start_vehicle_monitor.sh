#!/bin/bash

# Release any existing rfcomm connections
sudo rfcomm release 0

# Connect to the RPi Zero's Bluetooth MAC address
sudo rfcomm connect 0 B8:27:EB:09:1E:8E 1 &

# Wait for /dev/rfcomm0 to be created (max 10 seconds)
for i in {1..10}; do
    if [ -e /dev/rfcomm0 ]; then
        echo "✅ Connected to /dev/rfcomm0"
        break
    fi
    echo "⌛ Waiting for /dev/rfcomm0..."
    sleep 1
done

# Run the vehicle monitoring script
python3 /home/harry/Reversing-Tractor-device/Code/Run.py
