#!/bin/bash

BT_MAC="B8:27:EB:09:1E:8E"
RFCOMM_DEV="/dev/rfcomm0"
PROGRAM_PATH="/home/harry/Reversing-Tractor-device/Code/Run.py"

echo "🔌 Releasing any existing rfcomm connection..."
sudo rfcomm release 0

echo "🔗 Trying to connect to $BT_MAC on channel 1..."
sudo rfcomm connect 0 "$BT_MAC" 1 &

# Wait up to 10 seconds for /dev/rfcomm0
for i in {1..10}; do
    if [ -e "$RFCOMM_DEV" ]; then
        echo "✅ Connected: $RFCOMM_DEV is ready"
        break
    fi
    echo "⌛ Waiting for $RFCOMM_DEV... ($i/10)"
    sleep 1
done

# Warn if connection failed
if [ ! -e "$RFCOMM_DEV" ]; then
    echo "⚠️ Warning: Failed to detect $RFCOMM_DEV — continuing anyway"
fi

# Always run the Python program
echo "🚀 Running program: $PROGRAM_PATH"
python3 "$PROGRAM_PATH"
