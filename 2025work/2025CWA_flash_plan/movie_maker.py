import cv2
import os
import time
## ========================== 參數設定 ========================== ##
img_folder_path = "/home/steven/python_data/2025CWA_flash_plan/result/one_hour_one_pic/"  # 圖片資料夾
save_video_path = "/home/steven/python_data/2025CWA_flash_plan/result/one_hour_one_pic.mp4"  # 輸出影片路徑
fps = 5  # 每秒幾張

## ========================== 讀取圖片檔名 ========================== ##
img_files = sorted([
    f for f in os.listdir(img_folder_path)
    if f.lower().endswith(('.png', '.jpg', '.jpeg'))
])

if not img_files:
    print("❌ 找不到任何圖片")
    raise SystemExit

## ========================== 讀第一張圖片取得尺寸 ========================== ##
first_img_path = os.path.join(img_folder_path, img_files[0])
first_frame = cv2.imread(first_img_path)

if first_frame is None:
    print(f"❌ 無法讀取第一張圖片：{first_img_path}")
    raise SystemExit

height, width, _ = first_frame.shape
print(f"✅ 影片尺寸設定為：width={width}, height={height}")

## ========================== 建立影片寫入器 ========================== ##
fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 可以之後換成 'XVID' 測試
video_writer = cv2.VideoWriter(save_video_path, fourcc, fps, (width, height))

if not video_writer.isOpened():
    print("❌ VideoWriter 開啟失敗，可能是路徑或 codec 問題")
    raise SystemExit
else:
    print(f"✅ 成功開啟 VideoWriter，輸出：{save_video_path}")

## ========================== 寫入所有圖片 ========================== ##
for idx, img_name in enumerate(img_files, start=1):
    img_path = os.path.join(img_folder_path, img_name)
    frame = cv2.imread(img_path)

    if frame is None:
        print(f"⚠️ 第 {idx} 張讀取失敗，跳過：{img_path}")
        continue

    h, w, _ = frame.shape
    if (w, h) != (width, height):
        print(f"⚠️ 第 {idx} 張圖片尺寸不同，期望 ({width}, {height})，實際 ({w}, {h})，跳過：{img_path}")
        continue
    else:
        print(f"🟢 正在寫入第 {idx} 張圖片：{img_path}")

    video_writer.write(frame)

video_writer.release()
print(f"🎬 完成！影片已輸出：{save_video_path}")
