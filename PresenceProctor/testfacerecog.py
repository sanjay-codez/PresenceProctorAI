import cv2
from deepface import DeepFace
import os
from multiprocessing.dummy import Pool as ThreadPool

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


image_files = [f for f in os.listdir("images_data") if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]

# Load reference image
global reference_img = None
global counter =  0



# Initialize variables
face_match = False
lock = threading.Lock()

def check_face(frame):
    global face_match
    try:
        resized_frame = cv2.resize(frame, (300, 300))  # Resize frame for DeepFace
        verified = DeepFace.verify(resized_frame, reference_img)["verified"]
        with lock:
            face_match = verified
    except ValueError:
        pass

def do_face_matching():
    global face_match
    pool = ThreadPool(4)  # Number of threads
    while True:

        reference_img = cv2.imread("images_data/" + image_files[counter % len(image_files)])


        ret, frame = cap.read()
        if ret:
            counter += 1
            pool.map(check_face, [frame])  # Perform face verification in parallel
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
