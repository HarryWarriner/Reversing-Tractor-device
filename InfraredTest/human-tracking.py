import cv2
import time
import os
from picamera2 import Picamera2
from libcamera import Transform
RFCOMM_DEVICE = "/dev/rfcomm0"
def main():
    picam2 = Picamera2()

    transform = Transform(hflip=False, vflip=True)
    
    # Force RGB888 format for compatibility with OpenCV
    config = picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"},
        transform=transform
    )
    picam2.configure(config)
    picam2.start()
    time.sleep(2)

    # Setup the HOG descriptor/person detector
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    while True:
        frame = picam2.capture_array()

        # Ensure 8-bit format
        frame = cv2.convertScaleAbs(frame)

        # Resize to improve performance
        resized = cv2.resize(frame, (640, 480))

        gray = cv2.cvtColor(resized, cv2.COLOR_RGB2GRAY)

        # Detect people
        (boxes, weights) = hog.detectMultiScale(
            gray,
            winStride=(8, 8),
            padding=(16, 16),
            scale=1.03
        )

        # Draw detection boxes
        for (box, weight) in zip(boxes, weights):
            if weight > 0.6:
                x, y, w, h = box
                cv2.rectangle(resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(resized, f'{weight:.2f}', (x, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)


        for (box, weight) in zip(boxes, weights):
            if weight > 0.6:
                x, y, w, h = box
                print(f"Detected person at x={x}, y={y}, confidence={weight:.2f}")
                os.system(f'echo {x} | sudo tee {RFCOMM_DEVICE}')


        # Display the frame
        cv2.imshow("People Tracking", resized)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
