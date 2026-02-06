import cv2
import time

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

cap = cv2.VideoCapture(0)
warning = 0

while True:
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Agar face detect nahi hua
    if len(faces) == 0:
        warning += 1
        print("Warning:", warning)
        time.sleep(1)

    if warning >= 3:
        print("EXAM AUTO SUBMITTED")
        break

    cv2.imshow("Student Monitoring", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
