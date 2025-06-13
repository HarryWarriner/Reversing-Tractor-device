import sys
sys.path.append('/usr/lib/python3/dist-packages')

import cv2
import time
import os
from picamera2 import Picamera2
from libcamera import Transform

# Path to MobileNet SSD files
PROTO_PATH = "deploy.prototxt.txt"
MODEL_PATH = "mobilenet_iter_73000.caffemodel"
RFCOMM_DEVICE = "/dev/rfcomm0"

# Load pre-trained MobileNet SSD model
net = cv2.dnn.readNetFromCaffe(PROTO_PATH, MODEL_PATH)

# Class ID 15 = 'person'
PERSON_CLASS_ID = 15
CONF_THRESHOLD = 0.5

def main():
    picam2 = Picamera2()
    transform = Transform(hflip=False, vflip=True)

    config = picam2.create_still_configuration(
        main={"size": (640, 480), "format": "RGB888"},
        transform=transform,
        display=None
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(2)

    while True:
        frame = picam2.capture_array()
        frame = cv2.convertScaleAbs(frame)
        resized = cv2.resize(frame, (300, 300))
        (h, w) = frame.shape[:2]

        # Convert frame to blob for DNN input
        blob = cv2.dnn.blobFromImage(resized, 0.007843, (300, 300), 127.5)
        net.setInput(blob)
        detections = net.forward()

        person_detected = False

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            class_id = int(detections[0, 0, i, 1])

            if confidence > CONF_THRESHOLD and class_id == PERSON_CLASS_ID:
                box = detections[0, 0, i, 3:7] * [w, h, w, h]
                (startX, startY, endX, endY) = box.astype("int")
                person_detected = True
                print(f"Detected person at x={startX}, confidence={confidence:.2f}")

                try:
                    with open(RFCOMM_DEVICE, 'w') as serial:
                        serial.write(f"{startX}\n")
                except Exception as e:
                    print(f"Error writing to RFCOMM: {e}")
                break  # Use only the first detection

        time.sleep(0.1)

if __name__ == "__main__":
    main()
