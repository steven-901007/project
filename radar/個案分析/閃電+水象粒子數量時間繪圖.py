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
flash_path = r"C:/Users/steve/python_data/convective_rainfall_and_lighting_jump/case_study/01C400/36_EN_20210612_1100to2300/EN_flash_data.csv"

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

# ==== 整理雷達資料 ====
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

df = pd.DataFrame(all_stats)
df = df.sort_values('time')

# ==== 讀取flash_data ====
flash_df = pd.read_csv(flash_path)
flash_df['data time'] = pd.to_datetime(flash_df['data time'])

# ==== 繪圖 ====
fig, ax1 = plt.subplots(figsize=(12, 6))

# Graupel 像素數
color1 = 'tab:blue'
ax1.set_xlabel('時間')
ax1.set_ylabel('Graupel 像素數', color=color1)
ax1.plot(df['time'], df['Graupel'], marker='o', color=color1, label='Graupel 像素數')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))

# 閃電次數
ax2 = ax1.twinx()
color2 = 'tab:red'
ax2.set_ylabel('閃電次數', color=color2)
ax2.plot(flash_df['data time'], flash_df['flash_count'], color=color2, label='閃電次數')
ax2.tick_params(axis='y', labelcolor=color2)

# 標題與圖例
Time = datetime.strptime(target_date, "%Y%m%d").strftime("%Y/%m/%d")
plt.title(f'{Time} Graupel 像素數與閃電次數時間序列\n角度範圍：{az_min}° ~ {az_max}°')
fig.tight_layout()
plt.grid()
plt.show()
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
flash_path = r"C:/Users/steve/python_data/convective_rainfall_and_lighting_jump/case_study/01C400/36_EN_20210612_1100to2300/EN_flash_data.csv"

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

# ==== 整理雷達資料 ====
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

df = pd.DataFrame(all_stats)
df = df.sort_values('time')

# ==== 讀取flash_data ====
flash_df = pd.read_csv(flash_path)
flash_df['data time'] = pd.to_datetime(flash_df['data time'])

# ==== 繪圖 ====
fig, ax1 = plt.subplots(figsize=(12, 6))

# Graupel 像素數
color1 = 'tab:blue'
ax1.set_xlabel('時間')
ax1.set_ylabel('Graupel 像素數', color=color1)
ax1.plot(df['time'], df['Graupel'], marker='o', color=color1, label='Graupel 像素數')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))

# 閃電次數
ax2 = ax1.twinx()
color2 = 'tab:red'
ax2.set_ylabel('閃電次數', color=color2)
ax2.plot(flash_df['data time'], flash_df['flash_count'], color=color2, label='閃電次數')
ax2.tick_params(axis='y', labelcolor=color2)

# 標題與圖例
Time = datetime.strptime(target_date, "%Y%m%d").strftime("%Y/%m/%d")
plt.title(f'{Time} Graupel 像素數與閃電次數時間序列\n角度範圍：{az_min}° ~ {az_max}°')
fig.tight_layout()
plt.grid()
plt.show()
