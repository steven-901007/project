import os
from PIL import Image

def png_folder_to_gif(data_path: str, save_path: str, maker_range,duration_ms: int = 100, loop_count: int = 0):
    """
    將指定資料夾中的所有 PNG 圖片按檔名順序拼接成 GIF 動畫。

    Args:
        data_path (str): 包含 PNG 圖片的資料夾路徑。
        save_path (str): 輸出 GIF 檔案的完整路徑和名稱（例如 'output.gif'）。
        duration_ms (int): 每幀圖片的顯示持續時間（毫秒），預設為 100 毫秒。
        loop_count (int): GIF 的播放循環次數。0 表示無限循環（預設）。
                          1 表示播放一次，依此類推。
    """
    try:
        # 1. 獲取資料夾內所有 PNG 檔案路徑
        # os.listdir() 列出所有項目，然後篩選出以 .png 結尾的檔案
        image_files = [
            os.path.join(data_path, f)
            for f in os.listdir(data_path)
            if f.lower().endswith(f'{maker_range}_flash_onecolor.png')
        ]

        # 2. 依據檔案名稱進行排序，確保圖片順序正確 (e.g., frame_01, frame_02)
        # 這是動畫製作的關鍵步驟
        image_files.sort()

        if not image_files:
            print(f"錯誤：資料夾 '{data_path}' 中未找到任何 PNG 圖片。")
            return

        # 3. 讀取所有圖片
        images = []
        for file_path in image_files:
            try:
                img = Image.open(file_path).convert('RGB') # 轉換為 RGB 格式，確保相容性
                images.append(img)
            except Exception as e:
                print(f"警告：無法讀取檔案 {file_path}，已跳過。錯誤: {e}")

        if not images:
            print("錯誤：所有圖片讀取失敗，無法創建 GIF。")
            return

        # 4. 創建 GIF
        # 第一張圖片作為主要物件，使用 save() 方法創建多幀 GIF
        first_frame = images[0]
        other_frames = images[1:] # 剩餘的圖片作為附加幀

        first_frame.save(
            save_path,
            format='GIF',
            append_images=other_frames,
            save_all=True,        # 告訴 Pillow 這是一個多幀 GIF
            duration=duration_ms, # 每幀顯示時間 (毫秒)
            loop=loop_count       # 循環次數 (0=無限循環)
        )

        print(f"成功：已將 {len(images)} 張圖片拼接為 GIF，儲存至 '{save_path}'")

    except Exception as e:
        print(f"在創建 GIF 過程中發生錯誤：{e}")


# 主程式區域
data_top_path = "/home/steven/python_data/2025CWA_flash_plan/"
maker_range = 'chiayi_tainan' ##'chiayi_tainan' or 'taiwan'
# maker_range = 'taiwan'


# 圖片所在的資料夾路徑
data_paths = f'{data_top_path}/result/onecolor/'

os.makedirs(f'{data_top_path}/result/onecolor_gif/', exist_ok=True)
# 輸出 GIF 的儲存路徑和檔案名稱
save_data = f'{data_top_path}/result/onecolor_gif/{maker_range}.gif'

# 設定每幀持續時間為 150 毫秒 (即每秒 6.6 幀)
frame_duration = 500

# 呼叫函式
png_folder_to_gif(data_paths, save_data,maker_range,duration_ms=frame_duration)