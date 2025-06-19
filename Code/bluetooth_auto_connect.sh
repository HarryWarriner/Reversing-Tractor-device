#!/bin/bash

BT_MAC="B8:27:EB:09:1E:8E"
RFCOMM_DEV="/dev/rfcomm0"

# Check if already connected
if [ ! -e "$RFCOMM_DEV" ]; then
    echo "Connecting to $BT_MAC..."
    sudo rfcomm connect 0 "$BT_MAC" &
    sleep 10  # Give it time to connect
else
    echo "$RFCOMM_DEV already exists"
fi
/home/harry/Reversing-Tractor-device/Code/bluetooth_auto_connect.sh