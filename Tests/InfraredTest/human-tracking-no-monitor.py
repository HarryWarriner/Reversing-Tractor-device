import sys
sys.path.append('/usr/lib/python3/dist-packages')

import cv2
import time
import os
from picamera2 import Picamera2
from libcamera import Transform

RFCOMM_DEVICE = "/dev/rfcomm0"

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

    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    while True:
        frame = picam2.capture_array()
        frame = cv2.convertScaleAbs(frame)
        resized = cv2.resize(frame, (640, 480))

        (boxes, weights) = hog.detectMultiScale(
            resized, winStride=(4, 4), padding=(8, 8), scale=1.05
        )

        if len(boxes) > 0:
            print("Detected people at:", boxes)
            x, y, w, h = boxes[0]
            try:
                with open(RFCOMM_DEVICE, 'w') as serial:
                    serial.write(f"{x}\n")
            except Exception as e:
                print(f"Error writing to RFCOMM: {e}")

        time.sleep(0.1)

if __name__ == "__main__":
    main()
