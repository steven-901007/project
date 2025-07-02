import pyart
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from glob import glob
from datetime import datetime
from tqdm import tqdm

# ==== 參數設定 ====
target_date = "20210612"
data_folder = f"C:/Users/steve/python_data/radar/PID/{target_date}"

# 想統計的分類
target_classes = [4]  # 0:Rain、2:Wet Snow、4:Graupel
class_name_map = {
    0: 'Rain',
    1: 'Melting Layer',
    2: 'Wet Snow',
    3: 'Dry Snow',
    4: 'Graupel',
    5: 'Hail'
}

# 角度範圍設定（單位：度，0 度為正北，順時針）
az_min = 180
az_max = 290

# ==== 中文設定 ====
plt.rcParams['font.sans-serif'] = ['MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# ==== 整理資料 ====
all_stats = []
file_list = sorted(glob(os.path.join(data_folder, "*.nc")))

for file_path in tqdm(file_list):
    time_str = os.path.basename(file_path).split(".")[0]
    time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")

    radar = pyart.io.read(file_path)

    if 'hydro_class' not in radar.fields:
        print(f"{time_str} 沒有 hydro_class，跳過")
        continue

    azimuth = radar.azimuth['data']
    hydro_data = radar.fields['hydro_class']['data']

    row = {"time": time_dt}

    # 針對每個分類計算指定角度內的像素數
    for class_code in target_classes:
        mask = (azimuth >= az_min) & (azimuth <= az_max)
        selected_hydro = hydro_data[mask, :]

        pixel_count = np.sum(selected_hydro == class_code)
        row[class_name_map[class_code]] = pixel_count

    all_stats.append(row)

# ==== 整理成 DataFrame ====
df = pd.DataFrame(all_stats)
df = df.sort_values('time')

# ==== 繪圖 ====
plt.figure(figsize=(12, 6))

for class_code in target_classes:
    class_name = class_name_map[class_code]
    plt.plot(df['time'], df[class_name], marker='o', label=class_name)

ax = plt.gca()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))

Time = datetime.strptime(target_date, "%Y%m%d").strftime("%Y/%m/%d")
plt.title(f'{Time} 各分類像素數量時間序列\n角度範圍：{az_min}° ~ {az_max}°')
plt.xlabel('時間')
plt.ylabel('像素數量')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
