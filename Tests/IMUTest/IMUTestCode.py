#!/usr/bin/env python3
"""
mpu6050_test.py – simplest possible readout demo
Works on Raspberry Pi with an MPU-6050 at I2C address 0x68
"""

import smbus
import time

BUS_ID        = 1        # 1 on all modern Pi boards
MPU_ADDR      = 0x68
PWR_MGMT_1    = 0x6B
ACCEL_XOUT_H  = 0x3B
GYRO_XOUT_H   = 0x43

bus = smbus.SMBus(BUS_ID)

def write_reg(reg, data):
    bus.write_byte_data(MPU_ADDR, reg, data)

def read_word(reg):
    """Read 16-bit word from two consecutive registers (high, low)."""
    high = bus.read_byte_data(MPU_ADDR, reg)
    low  = bus.read_byte_data(MPU_ADDR, reg + 1)
    value = (high << 8) | low
    return value - 65536 if value > 32767 else value  # two’s-complement

# ---- initialise chip ----
write_reg(PWR_MGMT_1, 0x00)        # wake up device

print("MPU-6050 initialised, reading raw data (Ctrl-C to stop)…\n")

try:
    while True:
        ax = read_word(ACCEL_XOUT_H)
        ay = read_word(ACCEL_XOUT_H + 2)
        az = read_word(ACCEL_XOUT_H + 4)

        gx = read_word(GYRO_XOUT_H)
        gy = read_word(GYRO_XOUT_H + 2)
        gz = read_word(GYRO_XOUT_H + 4)

        print(f"Accel [g counts]  x:{ax:6}  y:{ay:6}  z:{az:6}   "
              f"Gyro [°/s counts]  x:{gx:6}  y:{gy:6}  z:{gz:6}")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nBye!")
