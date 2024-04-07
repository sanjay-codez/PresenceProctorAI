import threading
import cv2
from deepface import DeepFace
import os
import sys
import time

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0
face_match = False
reference_img = cv2.imread(os.path.join("images_data", "Sanjay.jpg"))

lock = threading.Lock()
last_match_time = time.time()  # Initialize the last match time

def check_face(frame):
    global face_match
    global last_match_time
    try:
        result = DeepFace.verify(img1_path=frame, img2_path=reference_img, enforce_detection=True)
        with lock:
            if result['verified']:
                face_match = True
                last_match_time = time.time()  # Update the last match time on success
            else:
                face_match = False
    except:
        pass

while True:
    ret, frame = cap.read()
    if ret:
        if counter % 30 == 0:
            threading.Thread(target=check_face, args=(frame.copy(),)).start()
        counter += 1

        with lock:
            match_text = "match!" if face_match else "no match!"
            if face_match:
                cv2.putText(frame, match_text, (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            else:
                cv2.putText(frame, match_text, (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                # Check if the last match was more than 7 seconds ago
                if time.time() - last_match_time > 7:
                    print("No match for over 7 seconds. Exiting.")
                    cap.release()
                    cv2.destroyAllWindows()
                    sys.exit()  # Terminate the program

        cv2.imshow("video", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()