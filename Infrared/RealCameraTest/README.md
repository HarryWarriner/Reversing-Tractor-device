# Thermal Camera

## Setup

Adjust the I2C rate, and add the speed parameter in the /boot/config.txt file. Reboot to take effect after changing. The commands are as shown below:

```
sudo nano /boot/config.txt
dtparam=i2c_arm=on,i2c_arm_baudrate=400000
```

### Using python

```
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-pil python3-pil.imagetk
sudo apt-get install python3-numpy
Enter the python directory (here users can modify the path according to their actual project location):
cd /home/pi/mlx90640/python
cd lib
sudo make clean
sudo make
cd ..
python3 mlx90640.py
```

