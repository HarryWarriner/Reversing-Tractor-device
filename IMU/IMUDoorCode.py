import time
import smbus # Using the smbus library as in your working test script
from gpiozero import Servo
from collections import deque
import subprocess


# =================================================================
# --- CONFIGURATION ---
# =================================================================
# MPU6050 Settings
BUS_ID = 1 # I2C Bus ID (typically 1 for modern Raspberry Pis)
MPU_ADDR = 0x68 # MPU6050 I2C address (can be 0x68 or 0x69)

# These thresholds are in raw accelerometer "g counts" (LSB/g)
# Adjust these based on real sensor output at rest and during movement.
FORWARD_THRESHOLD_COUNTS = 2000 # Example: Adjust this based on your testing
REVERSE_THRESHOLD_COUNTS = -2000 # Example: Adjust this based on your testing

# Servo Settings
SERVO_PIN = 17
DOOR_OPEN_ANGLE = 1.0
DOOR_CLOSED_ANGLE = -1.0

# Stability and Timer Settings
DIRECTION_CONFIRMATION_COUNT = 5 # Number of consistent readings to confirm a direction change
STATIONARY_TIMEOUT_S = 20 # Time in seconds after which the door closes if stationary

# MPU6050 Register Addresses (from mpu6050_test.py)
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43 

# Test
CAMERA_TEST_FILE_PATH = "/home/harry/Reversing-Tractor-device/IMU/cameraRunCode.py" 
# =================================================================
# --- I2C/MPU6050 COMMUNICATION FUNCTIONS ---
# =================================================================

bus = smbus.SMBus(BUS_ID)

def write_reg(reg, data):
    bus.write_byte_data(MPU_ADDR, reg, data)

def read_word(reg):
    """Read 16-bit word from two consecutive registers (high, low)."""
    high = bus.read_byte_data(MPU_ADDR, reg)
    low  = bus.read_byte_data(MPU_ADDR, reg + 1)
    value = (high << 8) | low
    return value - 65536 if value > 32767 else value  # two’s-complement

def initialize_mpu6050_sensor():
        write_reg(PWR_MGMT_1, 0x00)
        time.sleep(0.1) # Small delay for sensor to wake up
        print("✅ MPU6050 sensor initial configuration complete.")
        return True

# =================================================================
# --- SERVO INITIALISATION ---
# =================================================================
# # Setup Servo
servo = Servo(SERVO_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
print(f"✅ Servo on GPIO {SERVO_PIN} initialised.")

def initialise_system():
    """Sets the door to closed at startup."""
    print("⚙️  Initialising system...")
    servo.value = DOOR_CLOSED_ANGLE # Ensures the door starts in the closed position
    print("✅ Door closed.")
    time.sleep(1) # Small delay to allow the servo to reach position

# =================================================================
# --- MAIN LOGIC ---
# =================================================================
last_vehicle_state = "FORWARD"
stationary_start_time = 0
recent_directions = deque(maxlen=DIRECTION_CONFIRMATION_COUNT)

# Set the initial system state and initialize MPU6050
initialise_system()
if not initialize_mpu6050_sensor():
    exit() # Exit if MPU6050 couldn't be initialized

print("\n🚀 Starting main loop. Monitoring for vehicle movement...")

while True:
    try:
        # Read raw accelerometer X value directly using read_word function
        accel_x_raw = read_word(ACCEL_XOUT_H)
        
        # Use the raw "g counts" for comparison based on your working test.
        # You will need to adjust FORWARD_THRESHOLD_COUNTS and REVERSE_THRESHOLD_COUNTS
        # based on the actual raw values your sensor outputs when moving.
        
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

        # --- State Change and Action Logic ---
        if confirmed_direction != "STATIONARY":
            if confirmed_direction != last_vehicle_state:
                if confirmed_direction == "REVERSING":
                    print("Vehicle is REVERSING. Opening door...")
                    servo.value = DOOR_OPEN_ANGLE
                    p = subprocess.Popen(["python3",CAMERA_TEST_FILE_PATH])

                elif confirmed_direction == "FORWARD":
                    print("Vehicle is moving FORWARD. Closing door...")
                    servo.value = DOOR_CLOSED_ANGLE
                    p.kill()
                last_vehicle_state = confirmed_direction
            
            if stationary_start_time is not None:
                print("Vehicle is moving again, cancelling stationary timer.")
                stationary_start_time = None

        else: # confirmed_direction is "STATIONARY"
            if last_vehicle_state == "REVERSING" and stationary_start_time is None:
                print(f"Vehicle stopped. Starting {STATIONARY_TIMEOUT_S}s timer...")
                stationary_start_time = time.time()
            
            if stationary_start_time is not None and (time.time() - stationary_start_time > STATIONARY_TIMEOUT_S):
                print(f"Stationary for {STATIONARY_TIMEOUT_S}s. Closing door...")
                servo.value = DOOR_CLOSED_ANGLE
                p.kill()
                last_vehicle_state = "FORWARD"
                stationary_start_time = None

        time.sleep(0.1)

    except IOError as e:
        # Catches errors specific to smbus communication (e.g., sensor disconnected, bus error).
        print(f"⚠️ Warning: Could not read from sensor via SMBus: {e}. Retrying...")
        time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Program stopped by user. Ensuring door is closed...")
        servo.value = DOOR_CLOSED_ANGLE
        time.sleep(1)
        break