## 每 1 分鐘自動截圖一次（抓整個虛擬桌面）
## 依時間命名存檔到 ./screenshots 資料夾
## 按 Ctrl+C 可停止

import os
import time
from datetime import datetime
import mss
import mss.tools

## 參數設定
save_dir_path = r"C:\Users\steve\python_data\PC_temp" # 截圖儲存資料夾路徑_str
shot_interval_sec_int = 60                                 # 截圖間隔（秒）_int

os.makedirs(save_dir_path, exist_ok=True)  # 若資料夾不存在就建立

print(f"開始截圖，每 {shot_interval_sec_int} 秒一次。儲存到：{save_dir_path}")
print("按 Ctrl+C 可停止。")

try:
    with mss.mss() as sct:
        monitor_all = sct.monitors[2]  # 0 = 全部螢幕（虛擬桌面）；想只抓主螢幕可改成 sct.monitors[1]

        while True:
            start_monotonic_float = time.monotonic()  # 計時起點_float

            now_dt = datetime.now()
            file_name_str = now_dt.strftime("%Y%m%d_%H%M%S.png")  # 例如 20250903_134500.png
            save_path = os.path.join(save_dir_path, file_name_str)

            img = sct.grab(monitor_all)  # 擷取畫面
            mss.tools.to_png(img.rgb, img.size, output=save_path)  # 寫檔

            print(f"[{now_dt.strftime('%Y-%m-%d %H:%M:%S')}] 已存檔 -> {save_path}")

            ## 精準間隔控制：扣掉執行時間，維持接近整分鐘的頻率
            elapsed_sec_float = time.monotonic() - start_monotonic_float
            sleep_sec_float = max(0.0, shot_interval_sec_int - elapsed_sec_float)
            time.sleep(sleep_sec_float)

except KeyboardInterrupt:
    print("\n已停止截圖。")
# 每 1 分鐘截圖指定 APP 視窗
