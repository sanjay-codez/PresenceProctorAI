import cv2
from deepface import DeepFace
import os
from multiprocessing.dummy import Pool as ThreadPool

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Load reference images from the directory
reference_images = {}
directory = "images_data"
for filename in os.listdir(directory):
    if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
        reference_images[filename.split('.')[0]] = cv2.imread(os.path.join(directory, filename))

# Initialize variables
lock = threading.Lock()

def check_face(frame):
    matches = []
    try:
        resized_frame = cv2.resize(frame, (300, 300))  # Resize frame for DeepFace
        for name, reference_img in reference_images.items():
            verified = DeepFace.verify(resized_frame, reference_img)["verified"]
            if verified:
                matches.append(name)
        with lock:
            return matches
    except ValueError:
        pass

def do_face_matching():
    while True:
        ret, frame = cap.read()
        if ret:
            matches = check_face(frame)
            if matches:
                print("Match found for:", matches)
            else:
                print("No match found.")

            cv2.imshow("the_window", frame)

        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    do_face_matching()
