import cv2
import numpy as np
import os
from datetime import datetime

# 1. กำหนด Index ของกล้อง 2 ตัว (เช่น 0 และ 1 หรือตามที่สแกนเจอ)
CAM_INDEXES = [0, 1] 

SAVE_DIR = r"D:\DEVELOPERS\test cam\captured_images_2cam_4k"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def setup_camera_4k(cam_index):
    # ใช้ CAP_DSHOW เพื่อประสิทธิภาพที่ดีบน Windows
    cap = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
    
    # [สำคัญมาก] บังคับใช้ Codec แบบ MJPEG เพื่อประหยัด USB Bandwidth ให้เปิด 4K คู่ได้
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    
    # ตั้งค่าความละเอียดต้นฉบับเป็น 4K (3840 x 2160)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)
    
    return cap

# เริ่มต้นเชื่อมต่อกล้องทั้ง 2 ตัว
cap1 = setup_camera_4k(CAM_INDEXES[0])
cap2 = setup_camera_4k(CAM_INDEXES[1])

if not cap1.isOpened() or not cap2.isOpened():
    print("Error: ไม่สามารถเปิดกล้องครบทั้ง 2 ตัวได้ โปรดตรวจสอบสาย USB หรือ Index")
    exit()

print("=== พร้อมใช้งาน 2-Camera Multi-View (4K Mode) ===")
print("  > หน้าจอจะแสดงภาพ Preview ย่อส่วนเพื่อให้ดูพร้อมกันได้")
print("  > เมื่อกดถ่ายภาพ ไฟล์ที่ได้จะเป็นความละเอียด 4K เต็ม")
print("\nกด 'SPACEBAR' เพื่อกดถ่ายภาพ 4K ทั้ง 2 กล้องพร้อมกัน")
print("กด 'Q' เพื่อปิดโปรแกรม\n")

while True:
    # อ่านเฟรมภาพสดขนาด 4K จากกล้องทั้งสอง
    ret1, frame1 = cap1.read()
    ret2, frame2 = cap2.read()

    if not ret1 or not ret2:
        print("ไม่สามารถดึงสัญญาณภาพจากกล้องตัวใดตัวหนึ่งได้")
        break

    # --- ขั้นตอนการสร้างหน้าจอ Preview รวม ---

    # 1. ย่อขนาดภาพ 4K ลงเฉพาะตอนโชว์ (เช่น ย่อเหลือ 960x540 ต่อตัว เพื่อให้วางคู่กันแล้วไม่ล้นจอ)
    preview_h = 540
    preview_w = 960
    prev1 = cv2.resize(frame1, (preview_w, preview_h))
    prev2 = cv2.resize(frame2, (preview_w, preview_h))

    # 2. นำภาพ Preview ที่ย่อแล้วมาวางต่อกันในแนวนอน (Horizontal Stacking)
    # ผลลัพธ์จะได้ภาพเดียวขนาด (1920x540)
    combined_preview = np.hstack((prev1, prev2))

    # 3. ใส่ข้อความกำกับหัวกล้องเพื่อให้รู้ว่าตัวไหนเป็นตัวไหน
    cv2.putText(combined_preview, f"CAM 1 (Index {CAM_INDEXES[0]})", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(combined_preview, f"CAM 2 (Index {CAM_INDEXES[1]})", (preview_w + 20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # 4. แสดงผลหน้าจอ Preview รวมในหน้าต่างเดียว
    cv2.imshow("Master View: Camera 1 & 2 (Press Space to Capture 4K)", combined_preview)

    # จัดการคีย์บอร์ด
    key = cv2.waitKey(1) & 0xFF

    # สั่งถ่ายภาพ 4K เต็มพร้อมกันลงคอมพิวเตอร์เมื่อกด Spacebar
    if key == ord(' '):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # กำหนด Path ไฟล์ (ใช้ภาพขนาดเต็ม frame1, frame2)
        path1 = os.path.join(SAVE_DIR, f"Cam1_4K_{timestamp}.jpg")
        path2 = os.path.join(SAVE_DIR, f"Cam2_4K_{timestamp}.jpg")

        # เซฟภาพต้นฉบับ (frame1 และ frame2) ซึ่งเป็นขนาด 4K เต็ม (3840x2160)
        cv2.imwrite(path1, frame1)
        cv2.imwrite(path2, frame2)

        print(f"[{timestamp}] บันทึกภาพ 4K สำเร็จทั้ง 2 กล้อง:")
        print(f"  - Cam 1: {path1}")
        print(f"  - Cam 2: {path2}\n")

    # ออกจากโปรแกรมเมื่อกด 'q'
    elif key == ord('q'):
        break

# คืนค่าทรัพยากร
cap1.release()
cap2.release()
cv2.destroyAllWindows()