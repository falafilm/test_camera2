import cv2
import numpy as np

# 1. กำหนด Index ของกล้องทั้ง 4 ตัว (เช่น 0, 1, 2, 3)
CAM_INDEXES = [0, 1, 2, 3]

# กำหนดขนาดหน้าต่าง Preview รวมที่จะแสดงบนจอโน้ตบุ๊ก (เช่น Full HD)
PREVIEW_WIDTH = 1280
PREVIEW_HEIGHT = 720

# ขนาดของกล้องแต่ละตัวในตาราง 2x2 (คือขนาดพรีวิวรวมหารสอง)
SUB_WIDTH = PREVIEW_WIDTH // 2   # 640
SUB_HEIGHT = PREVIEW_HEIGHT // 2 # 360

# 2. เชื่อมต่อกล้องทุกตัว
caps = []
for idx in CAM_INDEXES:
    # แนะนำใช้ CAP_DSHOW บน Windows เพื่อให้เปิดกล้องได้เร็ว
    cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
    
    # เพื่อให้พรีวิวสดลื่นไหล ไม่กินแบนด์วิดท์ USB มากเกินไป
    # เราจะตั้งความละเอียดตอนพรีวิวไว้แค่พอดีดู (เช่น HD)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if cap.isOpened():
        print(f"เชื่อมต่อ Cam {idx} สำเร็จ")
        caps.append((idx, cap))
    else:
        print(f"Error: ไม่สามารถเปิด Cam {idx} ได้")

if len(caps) < 4:
    print("Error: พบกล้องไม่ครบ 4 ตัว โปรดตรวจสอบการเชื่อมต่อ")
    # แม้ไม่ครบก็ทำงานต่อเท่าที่พบ หรือจะ exit() ก็ได้
    # exit()

print("\n=== ระบบ Live Preview 4 กล้อง พร้อมใช้งาน ===")
print("มองที่หน้าต่าง '4-Camera Master Preview' เพื่อดูภาพสดพร้อมกัน")
print("กด 'Q' เพื่อปิดโปรแกรม\n")

while True:
    previews = []
    
    # 3. [Loop อ่านและจัดเตรียมภาพพรีวิว]
    for idx, cap in caps:
        ret, frame = cap.read()
        if ret:
            # ย่อขนาดภาพสดของกล้องตัวนี้ให้พอดีกับช่องในตาราง 2x2
            resized_frame = cv2.resize(frame, (SUB_WIDTH, SUB_HEIGHT))
            
            # ใส่หมายเลขกล้องกำกับไว้มุมภาพ จะได้รู้ว่าตัวไหนเป็นตัวไหน
            cv2.putText(resized_frame, f"CAM {idx}", (20, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            previews.append(resized_frame)
        else:
            # หากกล้องบางตัวดึงภาพไม่ได้ ให้สร้างภาพสีดำเปล่าๆ มาวางแทน
            black_frame = np.zeros((SUB_HEIGHT, SUB_WIDTH, 3), np.uint8)
            cv2.putText(black_frame, f"CAM {idx} LOST", (20, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            previews.append(black_frame)

    # 4. [STACKING - รวมภาพเป็นตาราง 2x2]
    # (ต้องมั่นใจว่ามีภาพครบ 4 ภาพใน list previews)
    if len(previews) >= 4:
        # ต่อภาพคู่บน (Cam1 + Cam2) ในแนวนอน
        top_row = np.hstack((previews[0], previews[1]))
        
        # ต่อภาพคู่ล่าง (Cam3 + Cam4) ในแนวนอน
        bottom_row = np.hstack((previews[2], previews[3]))
        
        # นำแถวบนและแถวล่างมาต่อกันในแนวตั้ง -> ได้ตาราง 2x2 สมบูรณ์
        grid_preview = np.vstack((top_row, bottom_row))

        # 5. [แสดงผล] นำภาพตารางรวมไปแสดงในหน้าต่างเดียว
        cv2.imshow("4-Camera Master Preview", grid_preview)

    # กด 'q' เพื่อออกจากลูปและปิดโปรแกรม
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ปิดกล้องและหน้าต่างทั้งหมด
for _, cap in caps:
    cap.release()
cv2.destroyAllWindows()