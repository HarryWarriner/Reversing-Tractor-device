import cv2
import time
from picamera2 import Picamera2
from libcamera import Transform

import RPi.GPIO as GPIO
from time import sleep

def main():
    picam2 = Picamera2()

    transform = Transform(hflip=False, vflip=True)

    # Set up 640x480 preview
    config = picam2.create_preview_configuration(
        main={"size": (640, 480)},
        transform=transform
    )
    picam2.configure(config)

    picam2.start()
    time.sleep(2)

    while True:
        # Grab the latest frame
        frame = picam2.capture_array()

        # Convert to grayscale then blur
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Apply fake infrared colormap
        infrared_frame = cv2.applyColorMap(gray, cv2.COLORMAP_JET)

        # Define red threshold in JET colormap range
        lower_red = (0, 0, 150)   # B, G, R
        upper_red = (50, 50, 255)
        mask = cv2.inRange(infrared_frame, lower_red, upper_red)

        # Find all red contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            if cv2.contourArea(c) > 300:  # threshold area
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(infrared_frame, (x, y), (x + w, y + h), (255, 255, 255), 2)

        # Show result
        cv2.imshow("Fake Infrared - Red Boxed", infrared_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
