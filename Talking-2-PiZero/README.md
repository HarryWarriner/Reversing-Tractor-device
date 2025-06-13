
# Bluetooth RFCOMM Serial Communication Between Raspberry Pi Zero and Pi 4

## 🔧 Setup on Both Devices

Install required packages:
```bash
sudo apt update
sudo apt install bluetooth pi-bluetooth bluez
```

Enable and start the Bluetooth service:
```bash
sudo systemctl enable bluetooth
sudo systemctl start bluetooth
```

Check Bluetooth status:
```bash
bluetoothctl
```

> Type `exit` to leave `bluetoothctl` when done.

---

## 🔗 Pair the Devices

On **both** Pis, enter the Bluetooth shell:
```bash
bluetoothctl
power on
agent on
default-agent
scan on
```

Once you see the MAC address of the other Pi, note it.

Still inside `bluetoothctl`, on **both devices**, run:
```bash
pair <MAC_ADDRESS_OF_OTHER_PI>
trust <MAC_ADDRESS_OF_OTHER_PI>
```

Once pairing is successful:
```bash
exit
```

---

## 🔌 Set Up a Serial Connection (RFCOMM)

### 🔄 Roles Explained

**Server Pi** (Listener / Receiver)
- Waits for connections
- Listens on a known Bluetooth channel
- Does *not* initiate communication

**Client Pi** (Initiator / Sender)
- Starts the Bluetooth connection
- Needs the MAC address of the server Pi
- Sends messages or requests data

---

### 📡 On the Server Pi (e.g., Pi Zero)

Enable the Serial Port Profile (SPP):
```bash
sudo sdptool add SP
```

Start listening for an RFCOMM connection:
```bash
sudo rfcomm listen /dev/rfcomm0
```

### ✅ Automatically Run Receiver Script on Boot (Pi Zero)

1. **Create a script** `/home/pi/run_receiver.sh`:
```bash
#!/bin/bash

# Bind to client MAC address (replace with your actual sender MAC)
rfcomm release 0
rfcomm bind 0 00:11:22:33:44:55 1

sleep 2

# Run the Python script
python3 /home/pi/your_receiver_script.py
```

Make it executable:
```bash
chmod +x /home/pi/run_receiver.sh
```

2. **Create a systemd service** `/etc/systemd/system/receiver.service`:
```ini
[Unit]
Description=Bluetooth RFCOMM Receiver and GPIO Handler
After=multi-user.target bluetooth.service

[Service]
ExecStart=/home/pi/run_receiver.sh
WorkingDirectory=/home/pi
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

3. **Enable and start it**:
```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable receiver.service
sudo systemctl start receiver.service
```

This will bind `/dev/rfcomm0` and run your script automatically on startup.

---

### 📲 On the Client Pi (e.g., Pi 4)

Connect to the server:
```bash
sudo rfcomm connect 0 <MAC_ADDRESS_OF_PI_ZERO>
```
Example for your project:
```bash
sudo rfcomm connect 0 B8:27:EB:09:1E:8E
```

Expected output:
```
Connected /dev/rfcomm0 to <MAC_ADDRESS_OF_PI_ZERO> on channel 1
```

---

## 🧼 Reset RFCOMM if Things Break

If you get errors like “Address already in use” or “Connection refused”, reset with:

```bash
sudo rfcomm release 0
sudo pkill -f rfcomm
sudo rm -f /dev/rfcomm0
```

Optionally restart Bluetooth:
```bash
sudo systemctl restart bluetooth
```

---

## 🧪 Test Communication

### On the Server Pi:
```bash
cat /dev/rfcomm0
```
This will wait for and display incoming messages.

### On the Client Pi:
```bash
echo "Hello from client!" | sudo tee /dev/rfcomm0
```

The message should appear on the server Pi.

---

## 🔁 If the Server Sees Repeating Messages

The client may have a `tee` command stuck in a loop.

Check running processes:
```bash
ps aux | grep rfcomm
ps aux | grep tee
```

If you see an old `tee /dev/rfcomm0` process, kill it:
```bash
sudo pkill -f tee
```
