import cv2
import time
from picamera2 import Picamera2
from libcamera import Transform

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

        # Detect people
        (boxes, weights) = hog.detectMultiScale(
            resized,
            winStride=(4, 4),
            padding=(8, 8),
            scale=1.05
        )

        # Draw detection boxes
        for (x, y, w, h) in boxes:
            cv2.rectangle(resized, (x, y), (x + w, y + h), (0, 255, 0), 2)

        if len(boxes) > 0:
            print("Detected people at:", boxes)

        # Display the frame
        cv2.imshow("People Tracking", resized)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
