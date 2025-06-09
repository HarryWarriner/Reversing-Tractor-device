# Pairing the Devices

Do on both RPiZero and RPi 4:

```
sudo apt update
sudo apt install bluetooth pi-bluetooth bluez

```

Enable Bluetooth Sevice:

```
sudo systemctl enable bluetooth
sudo systemctl start bluetooth
```

Check if Bluetooth is running:

```
bluetoothctl
```

If needed type ``` exit ``` to leave

## Pair the devices


On the Pi4:

```
bluetoothctl
power on
agent on
default-agent
scan on


```

On the other Pi, do the same. When the devices appear note the MAC addresses.
Still in ``` bluetoothctl ``` on each pi, pair and trust the other device:

```
pair <MAC_ADDRESS_OF_OTHER_PI>
trust <MAC_ADDRESS_OF_OTHER_PI>
```

After succesfully pairing, exit with ``` exit ```

## Set Up a Serial Connection (RFCOMM)

<hr>

Server Pi (Listener / Reciever)

- Waits for connections
- Listens on a known Bluetooth Channel
- Doesnt initate communication.

Client Pi (Initator / Sender)

- Initiates the Bluetooth connection to the server
- Knows the MAC address of the server
- Sends messages or requests data from the server

<hr>

On the server Pi (PiZero):<br>
Enable Serial Port profile:

```
sudo sdptool add sp
```

Bind RFCOMM to a virtual serial device:

```
sudo rfcomm listen /dev/rfcomm0
```

On the client Pi (Pi4):
Connect to the server:

```
sudo rfcomm connect 0 <MAC_ADDRESS_OF_PI_ZERO>
```

You should see:

```
Connected /dev/rfcomm0 to <MAC_ADDRESS_OF_PI_ZERO> on channel 1
```

### To fully clear the RFCOMM Device (If necessary)
Release any stuck connection:
```
sudo rfcomm release 0
```
Kill any existing rfcomm processes:
```
sudo pkill -f rfcomm
```
Remove the rfcomm device node (if it still exists):
```
sudo rm -f /dev/rfcomm0
```

## Test Communication

Open a new terminal and run: <br>

On the server Pi (PiZero):
```
cat /dev/rfcomm0
```
This will wait for and display incoming messages.

<br>
On the Client Pi (Pi4):
```
echo "Hello from client!" | sudo tee /dev/rfcomm0
```
This sends a test string across the Bluetooth serial link.

### If the server see the string repeating:

The client is sending repeatdley.
Check the client for any loop or stuck ``` tee```

```
ps aux | grep rfcomm
ps aux | grep tee

```
If you see a ```tee /dev/rfcomm0``` running in the background, it may be stuck. <br>
Kill it:
```
sudo pkill -f tee
```