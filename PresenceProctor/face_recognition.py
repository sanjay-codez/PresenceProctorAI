# Save this in a file named face_detect.py
import threading
import cv2
from deepface import DeepFace
import os
import sys
import time

# Load the cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_face_in_video(file_path):
    """
        Detects a face in a live video stream and compares it with a reference image.

        This function captures live video from the default webcam (index 0) and continuously checks for the presence
        of a face. It draws rectangles around detected faces in the video stream. It compares the detected face with
        a reference image provided as the `file_path` parameter using the DeepFace library. If a match is found within
        10 seconds, it returns True; otherwise, it returns False.

        Args:
            file_path (str): The file path of the reference image.

        Returns:
            bool: True if a matching face is detected within 10 seconds, False otherwise.

        Note:
            This function requires the OpenCV and DeepFace libraries.

        Example:
            To use this function, provide the file path of the reference image. For example:
                detect_face_in_video('path_to_reference_image.jpg')
    """
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    counter = 0
    face_match = False
    reference_img_path = file_path

    lock = threading.Lock()
    last_match_time = time.time()  # Initialize the last match time

    def check_face(frame, reference_img_path):
        """
            Checks if a face in a frame matches a reference image.

            This function compares a face in the provided frame with a reference image using the DeepFace library.
            It sets the `face_match` flag to True if the face in the frame matches the reference image, and updates
            the `last_match_time`. If no match is found, it sets `face_match` to False.

            Args:
                frame: The frame containing the face to be checked.
                reference_img_path (str): The file path of the reference image.

            Returns:
                None

            Note:
                This function assumes the existence of a `face_match` flag and a `last_match_time` variable.
                It also relies on the DeepFace library for face verification.

            Example:
                This function is typically called within a video processing loop to check if a detected face matches
                a reference image. For example:
                    check_face(frame, 'path_to_reference_image.jpg')
        """
        nonlocal face_match
        nonlocal last_match_time
        try:
            result = DeepFace.verify(img1_path=frame, img2_path=reference_img_path, enforce_detection=True)
            with lock:
                if result['verified']:
                    face_match = True
                    last_match_time = time.time()  # Update the last match time on success
                else:
                    face_match = False
        except:
            pass

    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if ret:
            # Convert frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # Detect faces in the frame
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            # Draw rectangles around each face
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            if counter % 30 == 0:
                threading.Thread(target=check_face, args=(frame.copy(), reference_img_path)).start()
            counter += 1

            # Display the frame
            cv2.imshow("Video", frame)

            with lock:
                if face_match:
                    cap.release()
                    cv2.destroyAllWindows()
                    return True

                # Check if the last match was more than 10 seconds ago or 10 seconds have passed since the start without a match
                if time.time() - last_match_time > 10 or time.time() - start_time > 10:
                    cap.release()
                    cv2.destroyAllWindows()
                    return False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return False  # Ensure function returns False if exited early

