import pyart
import numpy as np
from datetime import datetime
from pyart.retrieve import kdp_maesaka
import os

# ==== 時間與路徑設定 ====
data_top_path = "C:/Users/steve/python_data/radar"
year, month, day = '2024', '05', '23'
hh, mm, ss = '00', '02', '00'
time_str = f"{year}{month}{day}{hh}{mm}{ss}"

# ==== 檔案路徑 ====
vol_path = f"{data_top_path}/{year}{month}{day}_u.RCWF/{time_str}.VOL"
output_path = f"{data_top_path}/PID/{time_str}.nc"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# ==== 讀取原始 VOL ====
radar = pyart.io.read(vol_path)

# ==== 計算 KDP（Maesaka 方法） ====
print("⚙️ 正在計算 KDP（Maesaka 方法），請稍候...")
kdp_dict, _, _ = kdp_maesaka(radar)
radar.add_field('kdp_maesaka', kdp_dict)

# ==== 儲存為 NetCDF VOL 格式 ====

# 再進行寫入
pyart.io.write_cfradial(output_path, radar)
print(f"✅ 儲存成功：{output_path}")
