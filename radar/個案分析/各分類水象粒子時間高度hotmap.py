import pyart
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from glob import glob
from datetime import datetime
import os
import sys
from tqdm import tqdm

# ==== 參數設定 ====
time = "20210612"
data_top_path = f"C:/Users/steve/python_data/radar"
# data_top_path = "/home/steven/python_data/radar"
target_date =  sys.argv[1] if len(sys.argv) > 1 else "20210612"  # yyyymmdd
file_pattern = f"{data_top_path}/PID/{time}/*.nc"

## ==== 想畫的水象粒子類型 ====
## 0: Rain、1: Melting Layer、2: Wet Snow、3: Dry Snow、4: Graupel、5: Hail
target_class = 4  # 你可以改這個變數選擇要畫的類別

## 類別對應名稱
class_name_map = {
    0: 'Rain',
    1: 'Melting Layer',
    2: 'Wet Snow',
    3: 'Dry Snow',
    4: 'Graupel',
    5: 'Hail'
}

## ==== 中文字型 ====
plt.rcParams['font.sans-serif'] = ['MingLiu']  # '細明體'
plt.rcParams['axes.unicode_minus'] = False

# ==== 整理資料 ====
all_data = []

file_list = sorted(glob(file_pattern))

for file_path in tqdm(file_list):
    time_str = os.path.basename(file_path).split(".")[0]
    time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")

    radar = pyart.io.read(file_path)
    grid = pyart.map.grid_from_radars(
        radar,
        grid_shape=(21, 400, 400),
        grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
        fields=['hydro_class'],
        gridding_algo='map_gates_to_grid',
        weighting_function='Barnes',
        roi_func='dist_beam',
    )

    z_levels = grid.z['data']
    hydro_data = grid.fields['hydro_class']['data']

    for z_idx, z in enumerate(z_levels):
        layer_data = hydro_data[z_idx]
        class_count = np.sum(layer_data == target_class)

        all_data.append({
            'time': time_dt,
            'height': z,
            'class_count': class_count
        })

# ==== 整理成 DataFrame ====
df = pd.DataFrame(all_data)

# ==== 製作 pivot 資料表 ====
pivot_df = df.pivot_table(index='height', columns='time', values='class_count', fill_value=0)
pivot_df = pivot_df.sort_index()

# ==== 繪圖 ====
plt.figure(figsize=(12, 6))
time_labels = [t.strftime("%H:%M") for t in pivot_df.columns]

data_array = pivot_df.values.astype(float)

plt.imshow(data_array, aspect='auto', origin='lower',
           extent=[-0.5, len(time_labels)-0.5, pivot_df.index.min(), pivot_df.index.max()],
           cmap='hot')

plt.colorbar(label=f'{class_name_map[target_class]} 像素數量')
plt.xticks(ticks=np.arange(len(time_labels)), labels=time_labels, rotation=90)
plt.yticks(np.arange(pivot_df.index.min(), pivot_df.index.max() + 500, 1000))
plt.xlabel("時間 (hh:mm)")
plt.ylabel("高度 (m)")
plt.title(f"{class_name_map[target_class]} 像素數量 高度-時間熱圖")
plt.tight_layout()
# plt.show()
plt.savefig(rf"{data_top_path}/hydrometeor_time_height_hotmap/{time}_{class_name_map[target_class]}", dpi=300)

# ==== 存 CSV ====
# 確保資料夾存在
save_folder = f"{data_top_path}/hydrometeor_time_height_hotmap"
os.makedirs(save_folder, exist_ok=True)

# 存檔路徑
csv_path = f"{save_folder}/{time}_{class_name_map[target_class].lower()}_data.csv"

# 存檔
df_sorted = df.sort_values(['time', 'height'])  # 時間、高度排序比較好閱讀
df_sorted.to_csv(csv_path, index=False)

print(f"✅ 圖片與 CSV 檔已儲存至 {save_folder}")