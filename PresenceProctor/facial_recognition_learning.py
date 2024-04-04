import threading
import cv2
from deepface import DeepFace
import os

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
files = os.listdir("images_data")
image_files = [f for f in files if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]


# Initialize variables
face_match = False
counter = 0
lock = threading.Lock()

def check_face(frame, filename):
    global face_match
    try:
        verified = DeepFace.verify(frame, reference_img)["verified"]

        with lock:
            if verified:
                face_match = True
                print("Match found with image:", filename)  # Print the filename on match
            else:
                face_match = False
    except ValueError:
        pass

def do_face_matching():
    global face_match, counter, reference_img
    while True:

        # Get the current image filename
        current_image_filename = image_files[counter % len(image_files)]
        reference_img = cv2.imread("images_data/" + current_image_filename)

        ret, frame = cap.read()
        if ret:
            counter += 1
            if counter % 30 == 0:  # Check every 30 frames
                try:
                    # Pass the current image filename to check_face function
                    threading.Thread(target=check_face, args=(frame.copy(), current_image_filename)).start()
                except RuntimeError:
                    pass

            with lock:
                if face_match:
                    cv2.putText(frame, "MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

                else:
                    cv2.putText(frame, "NO MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

            cv2.imshow("the_window", frame)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()








if __name__ == "__main__":
    do_face_matching()