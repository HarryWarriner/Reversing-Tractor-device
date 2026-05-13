## Getting the camera to work

On a new device, install libcamera:

Update system:
sudo apt update
sudo apt upgrade

Install libcamera:
sudo apt install libcamera-apps

Enable camera interface:
sudo raspi-config

    Go to interface options, camera
    Enable it and reboot

Check the camera is connected:
libcamera-hello --list-camera

Preview the camera:
libcamera-hello
