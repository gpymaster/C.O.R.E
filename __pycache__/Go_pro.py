import cv2

# Initialize video capture object for the GoPro (assuming it's the default webcam)
cap = cv2.VideoCapture(2) 

if not cap.isOpened():
    print("Error: Could not open GoPro camera.")
else:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame.")
            break

        cv2.imshow("GoPro Webcam Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()