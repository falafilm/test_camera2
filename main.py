import cv2
import numpy as np
import os
import sys
from datetime import datetime

# check index camera
# 1. ฟังก์ชันสแกนหา Index กล้องที่ต่ออยู่และส่งสัญญาณภาพได้จริง
def get_available_camera_indices(needed_count=2, max_test=10):
    available_indices = []
    print("กำลังสแกนหา Index ของกล้องในระบบ...")
    
    for idx in range(max_test):
        cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                print(f" -> พบกล้องที่ใช้งานได้ที่ Index {idx}")
                available_indices.append(idx)
            cap.release()
            
            # ถ้าเจอจำนวนกล้องตามที่ต้องการแล้ว ให้หยุดสแกนทันทีเพื่อประหยัดเวลา
            if len(available_indices) == needed_count:
                break

    return available_indices

# --- เริ่มสแกนหากล้อง 2 ตัวที่ใช้งานได้ ---
CAM_INDEXES = get_available_camera_indices(needed_count=2)

if len(CAM_INDEXES) < 2:
    print(f"\n Error: พบกล้องที่ใช้งานได้เพียง {len(CAM_INDEXES)} ตัว (ต้องการ 2 ตัว)")
    print(" โปรดตรวจสอบว่าปิดโปรแกรมอื่นที่ใช้กล้องอยู่หรือยัง หรือย้ายพอร์ต USB")
    sys.exit()

print(f"\n เลือกใช้งานกล้อง Index: {CAM_INDEXES}\n")


# CAM_INDEXES = [0, 1] --. index

SAVE_DIR = r"D:\SAVECAM\captured_images_2cam_4k"

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

CAM_DIR = []
for i in range(len(CAM_INDEXES)):
    cam_folder = os.path.join(SAVE_DIR, f"CAM_{i+1}")
    os.makedirs(cam_folder, exist_ok=True)
    CAM_DIR.append(cam_folder)
    
def setup_camera_4k(cam_index):
    cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
    cap.set(cv2.CAP_PROP_FPS, 30)
    return cap

cam1 = setup_camera_4k(CAM_INDEXES[0])
cam2 = setup_camera_4k(CAM_INDEXES[1])

if not cam1 or not cam2 or not cam1.isOpened() or not cam2.isOpened():
    print("ไม่สมารถเปิดกล้องครบทั้งสองได้")
    sys.exit()
    
while True:
    ret1, frame1 = cam1.read()
    ret2, frame2 = cam2.read()
    
    if not ret1 or not ret2:
        print("อ่านค่าจากกล้องไม่ได้")
        break
    
    preview_h = 540
    preview_w = 960
    
    prev1 = cv2.resize(frame1, (preview_w, preview_h))
    prev2 = cv2.resize(frame2, (preview_w, preview_h))
    
    combined_preview = np.hstack((prev1, prev2))
    
    cv2.putText(combined_preview, f"CAM 1", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(combined_preview, f"CAM 2", (preview_w + 20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    cv2.imshow("2-Combined Preview", combined_preview)
    
    # กด 1 วิ และแปลงรหัสเป็น ascii
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord(' '):
        
        # ✅ แก้เป็นแบบนี้
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        cv2.imwrite(os.path.join(CAM_DIR[0], f"CAM1_{timestamp}.jpg"), frame1)
        cv2.imwrite(os.path.join(CAM_DIR[1], f"CAM2_{timestamp}.jpg"), frame2)

    elif key == ord('q'):
        break

cam1.release()
cam2.release()

cv2.destroyAllWindows()
    
            