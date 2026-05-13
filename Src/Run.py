import time
import smbus
from gpiozero import Servo
from collections import deque
import subprocess

'''
========== CONFIGURATION ==========
'''
# MPU6050 Settings
BUS_ID = 1
MPU_ADDR = 0x68

# Thresholds in raw accelerometer "g counts" (LSB/g)
FORWARD_THRESHOLD_COUNTS = 2000
REVERSE_THRESHOLD_COUNTS = -2000

# Servo Settings
SERVO_PIN = 17
OPPOSITE_SERVO_PIN = 18
DOOR_OPEN_ANGLE = 1.0
DOOR_CLOSED_ANGLE = -1.0

# Stability and Timer Settings
DIRECTION_CONFIRMATION_COUNT = 5
STATIONARY_TIMEOUT_S = 20

# MPU6050 Register Addresses
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43 

# Camera Script
CAMERA_TEST_FILE_PATH = "/home/harry/Reversing-Tractor-device/Code/camera-tracking.py"

'''
========== I2C/MPU6050 COMMUNICATION FUNCTIONS ==========
'''

bus = smbus.SMBus(BUS_ID)

def write_reg(reg, data):
    bus.write_byte_data(MPU_ADDR, reg, data)

def read_word(reg):
    high = bus.read_byte_data(MPU_ADDR, reg)
    low  = bus.read_byte_data(MPU_ADDR, reg + 1)
    value = (high << 8) | low
    return value - 65536 if value > 32767 else value

def initialize_mpu6050_sensor():
    write_reg(PWR_MGMT_1, 0x00)
    time.sleep(0.1)
    print("✅ MPU6050 sensor initial configuration complete.")
    return True

'''
========== SERVO INITIALISATION ==========
'''

servo = Servo(SERVO_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servo2 = Servo(OPPOSITE_SERVO_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
print(f"✅ Servos on GPIO {SERVO_PIN} and GPIO {OPPOSITE_SERVO_PIN} initialised.")

def set_servos(value):
    """Set main servo and inverse the second one."""
    servo.value = value
    servo2.value = -value

def initialise_system():
    print("⚙️  Initialising system...")
    set_servos(DOOR_CLOSED_ANGLE)
    print("✅ Door closed.")
    time.sleep(1)

'''
========== MAIN LOGIC ==========
'''

last_vehicle_state = "FORWARD"
stationary_start_time = 0
recent_directions = deque(maxlen=DIRECTION_CONFIRMATION_COUNT)

initialise_system()
if not initialize_mpu6050_sensor():
    exit()

print("\n🚀 Starting main loop. Monitoring for vehicle movement...")

p = None  # placeholder for camera process

while True:
    try:
        accel_x_raw = read_word(ACCEL_XOUT_H)

        immediate_direction = "STATIONARY"
        if accel_x_raw > FORWARD_THRESHOLD_COUNTS:
            immediate_direction = "FORWARD"
        elif accel_x_raw < REVERSE_THRESHOLD_COUNTS:
            immediate_direction = "REVERSING"
        
        recent_directions.append(immediate_direction)

        if len(recent_directions) < DIRECTION_CONFIRMATION_COUNT:
            continue

        confirmed_direction = recent_directions[0] if all(d == recent_directions[0] for d in recent_directions) else None
        if confirmed_direction is None:
            continue

        if confirmed_direction != "STATIONARY":
            if confirmed_direction != last_vehicle_state:
                if confirmed_direction == "REVERSING":
                    print("Vehicle is REVERSING. Opening door...")
                    set_servos(DOOR_OPEN_ANGLE)
                    p = subprocess.Popen(["python3", CAMERA_TEST_FILE_PATH])

                elif confirmed_direction == "FORWARD":
                    print("Vehicle is moving FORWARD. Closing door...")
                    set_servos(DOOR_CLOSED_ANGLE)
                    if p: p.kill()

                last_vehicle_state = confirmed_direction
            
            if stationary_start_time is not None:
                print("Vehicle is moving again, cancelling stationary timer.")
                stationary_start_time = None

        else:  # STATIONARY
            if last_vehicle_state == "REVERSING" and stationary_start_time is None:
                print(f"Vehicle stopped. Starting {STATIONARY_TIMEOUT_S}s timer...")
                stationary_start_time = time.time()
            
            if stationary_start_time is not None and (time.time() - stationary_start_time > STATIONARY_TIMEOUT_S):
                print(f"Stationary for {STATIONARY_TIMEOUT_S}s. Closing door...")
                set_servos(DOOR_CLOSED_ANGLE)
                if p: p.kill()
                last_vehicle_state = "FORWARD"
                stationary_start_time = None

        time.sleep(0.1)

    except IOError as e:
        print(f"⚠️ Warning: Could not read from sensor via SMBus: {e}. Retrying...")
        time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Program stopped by user. Ensuring door is closed...")
        set_servos(DOOR_CLOSED_ANGLE)
        time.sleep(1)
        break
