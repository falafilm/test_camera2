import cv2

# check index camera
for i in range(10):
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        print(f"Camera index {i} is working.")
        cap.release()
    else:
        print(f"Camera index {i} is not working.")