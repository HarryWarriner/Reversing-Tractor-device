import time
import board
import adafruit_mpu6050
from gpiozero import Servo, Relay  
from collections import deque

# =================================================================
# --- CONFIGURATION ---
# =================================================================
# MPU6050 Settings
FORWARD_THRESHOLD_MS2 = 1.5
REVERSE_THRESHOLD_MS2 = -1.5

# Servo Settings
SERVO_PIN = 17
DOOR_OPEN_ANGLE = 90
DOOR_CLOSED_ANGLE = 0

# Relay Pin for Camera Power
CAMERA_POWER_PIN = 26  # GPIO pin connected to the relay's IN pin

# Stability and Timer Settings
DIRECTION_CONFIRMATION_COUNT = 5
STATIONARY_TIMEOUT_S = 30

# =================================================================
# --- INITIALISATION ---
# We can get rid of this whole section once we have tested it works. (other than the system initialising)
# =================================================================
# Setup I2C and MPU6050 Sensor
i2c = board.I2C()
mpu = adafruit_mpu6050.MPU6050(i2c)
print("✅ MPU6050 sensor setup complete.")

# Setup Servo
servo = Servo(SERVO_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
print(f"✅ Servo on GPIO {SERVO_PIN} initialised.")

# Setup Relay for Camera Power
try:
    # Most relay modules turn ON with a LOW signal, so active_high=False is common.
    # If your relay clicks ON when the script starts, change this to True.
    camera_power = Relay(CAMERA_POWER_PIN, active_high=False) 
    print(f"✅ Camera power relay on GPIO {CAMERA_POWER_PIN} initialised.")
except Exception as e:
    print(f"❌ Failed to initialise relay: {e}. Exiting.")
    exit()

def initialise_system():
    """Sets the door to closed and ensures camera is off at startup."""
    print("⚙️  Initialising system...")
    servo.angle = DOOR_CLOSED_ANGLE
    camera_power.off()  # <-- Ensure camera is off
    print("✅ Door closed and camera powered OFF.")
    time.sleep(1)

# =================================================================
# --- MAIN LOGIC ---
# =================================================================
last_vehicle_state = "FORWARD"
stationary_start_time = None
recent_directions = deque(maxlen=DIRECTION_CONFIRMATION_COUNT)

# Set the initial system state
initialise_system()

print("\n🚀 Starting main loop. Monitoring for vehicle movement...")

while True:
    try:
        # (This includes the accel_x reading, immediate_direction, recent_directions buffer, etc.)
        accel_x, _, _ = mpu.acceleration
        immediate_direction = "STATIONARY"
        if accel_x > FORWARD_THRESHOLD_MS2: immediate_direction = "FORWARD"
        elif accel_x < REVERSE_THRESHOLD_MS2: immediate_direction = "REVERSING"
        recent_directions.append(immediate_direction)
        if len(recent_directions) < DIRECTION_CONFIRMATION_COUNT: continue
        confirmed_direction = recent_directions[0] if all(d == recent_directions[0] for d in recent_directions) else None
        if confirmed_direction is None: continue

        # State Change and Action Logic
        if confirmed_direction != "STATIONARY":
            if confirmed_direction != last_vehicle_state:
                if confirmed_direction == "REVERSING":
                    print("Vehicle is REVERSING. Opening door and turning ON camera...")
                    servo.angle = DOOR_OPEN_ANGLE
                    camera_power.on()  # <-- Turn camera ON
                elif confirmed_direction == "FORWARD":
                    print("Vehicle is moving FORWARD. Closing door and turning OFF camera...")
                    servo.angle = DOOR_CLOSED_ANGLE
                    camera_power.off() # <-- Turn camera OFF
                last_vehicle_state = confirmed_direction
            if stationary_start_time is not None:
                print("Vehicle is moving again, cancelling stationary timer.")
                stationary_start_time = None

        else: # Vehicle is stationary
            if last_vehicle_state == "REVERSING" and stationary_start_time is None:
                print(f"Vehicle stopped. Starting {STATIONARY_TIMEOUT_S}s timer...")
                stationary_start_time = time.time()
            
            if stationary_start_time is not None and (time.time() - stationary_start_time > STATIONARY_TIMEOUT_S):
                print(f"Stationary for {STATIONARY_TIMEOUT_S}s. Closing door and turning OFF camera...")
                servo.angle = DOOR_CLOSED_ANGLE
                camera_power.off() # <-- Turn camera OFF
                last_vehicle_state = "FORWARD"
                stationary_start_time = None

        time.sleep(0.1)

    except OSError as e:
        print(f"⚠️ Warning: Could not read from sensor: {e}. Retrying...")
        time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Program stopped by user. Ensuring door is closed and camera is off...")
        servo.angle = DOOR_CLOSED_ANGLE
        camera_power.off() # <-- Important: Turn camera OFF on exit
        time.sleep(1)
        break
