import cv2
import time
from picamera2 import Picamera2
from libcamera import Transform

def main():
    picam2 = Picamera2()

    transform = Transform(hflip=False, vflip=True)

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

        # Convert to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define HSV range for red (wraps around 0, so we use two ranges)
        lower_red1 = (0, 120, 70)
        upper_red1 = (10, 255, 255)

        lower_red2 = (170, 120, 70)
        upper_red2 = (180, 255, 255)

        # Create masks for red
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        red_boxes = []

        for c in contours:
            if cv2.contourArea(c) > 300:
                x, y, w, h = cv2.boundingRect(c)
                red_boxes.append((x, y, w, h))
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if red_boxes:
            print("Detected red boxes:", red_boxes)

        # Show original frame with red boxes
        cv2.imshow("Red Object Tracking", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
