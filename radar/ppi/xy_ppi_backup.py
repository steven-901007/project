##這是繪製PID ppi xy 的code 並且Y軸為bin數


import numpy as np
import matplotlib.pyplot as plt
import pyart
import os
import sys

## =========================
## 參數（請確認路徑與欄位）
## =========================
data_top_path = "/home/steven/python_data/radar"
year  = sys.argv[1] if len(sys.argv) > 1 else '2024'
month = sys.argv[2] if len(sys.argv) > 2 else '06'
day   = sys.argv[3] if len(sys.argv) > 3 else '02'
hh    = sys.argv[4] if len(sys.argv) > 4 else '08'
mm    = sys.argv[5] if len(sys.argv) > 5 else '16'
pid   = 'park'  # park or way(魏)

ss = '00'
station = 'RCWF'
vol_file_path = f"{data_top_path}/PID/{year}{month}{day}_{station}_{pid}/{year}{month}{day}{hh}{mm}{ss}.nc"
sweep_index = int(sys.argv[6]) if len(sys.argv) > 6 else 0
field_name = "hydro_class"
time_str = f"{year}{month}{day}{hh}{mm}{ss}"

time_save_dir  = f"{data_top_path}/PID_PPI/{year}{month}{day}/{time_str}/xy_ppi"
sweep_save_dir = f"{data_top_path}/PID_PPI/{year}{month}{day}/sweep{sweep_index}/xy_ppi"
os.makedirs(time_save_dir, exist_ok=True)
os.makedirs(sweep_save_dir, exist_ok=True)

## 讀檔
radar = pyart.io.read(vol_file_path)
if field_name not in radar.fields:
    raise KeyError(f"檔案內找不到欄位 {field_name}，可用欄位：{list(radar.fields.keys())}")

## 取出該 sweep 的資料（原貌：不統計/不改值）
sweep_slice = radar.get_slice(sweep_index)
pid_data_2d_array = radar.fields[field_name]["data"][sweep_slice]
pid_raw_2d = pid_data_2d_array.data if isinstance(pid_data_2d_array, np.ma.MaskedArray) else pid_data_2d_array
nrays_sweep, ngates_total = pid_raw_2d.shape  # (ray, bin)

## =========================
## 類別→顏色（固定）
## =========================
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch

# 類別對應（只在 legend 顯示 0..5）
label_map_dict = {
    0: "Rain",
    1: "Melting Layer",
    2: "Wet Snow",
    3: "Dry Snow",
    4: "Graupel",
    5: "Hail",
}
# 0..5 顏色（你的 hex）
colors_user_hex = ["#1FE4F3FF", "#ebff0e", "#2ca02c", "#27d638", "#f51010", "#3c00ff"]

# -999/-1 顏色（畫面用；不進 legend）
color_for_fill = "#FFFFFF"  # -999
color_for_unk  = "#BCB8B8FF"  # -1

class_values_list = [-999, -1, 0, 1, 2, 3, 4, 5]
color_list = [color_for_fill, color_for_unk, *colors_user_hex]
pid_plot_cmap = ListedColormap(color_list)
bounds_list   = [cv - 0.5 for cv in class_values_list] + [class_values_list[-1] + 0.5]
pid_plot_norm = BoundaryNorm(bounds_list, pid_plot_cmap.N)

## =========================
## 以最接近 0° 的 ray 當作 X=0 起點
## =========================
az_all_deg = radar.azimuth['data'][sweep_slice].astype(float)   # 每條 ray 的真實方位角 (deg)
# 找最接近 0° 的索引（考慮 0/360 環狀距離）
idx0 = int(np.argmin(np.abs(((az_all_deg - 0.0) + 180.0) % 360.0 - 180.0)))

# 沿 ray 方向重排，讓該 ray 成為第一條
pid_roll_2d = np.roll(pid_raw_2d, -idx0, axis=0)  # (ray, bin)
az_roll_deg = np.roll(az_all_deg, -idx0)

# 平移 az，使起點對齊 0 度並單調遞增到 <360
az_shift_deg = (az_roll_deg - az_roll_deg[0]) % 360.0  # az_shift_deg[0] = 0

## =========================
## 繪圖（X=0..360 角度；Y=bin index）
## =========================
fig = plt.figure(figsize=(11, 6))
ax  = plt.axes()

# imshow 需規則格，雷達常見等角解析度 → 直接用 extent 固定 0..360
im = ax.imshow(
    pid_roll_2d.T,           # (ngates, nrays)
    origin='lower',
    aspect='auto',
    interpolation='nearest',
    cmap=pid_plot_cmap,
    norm=pid_plot_norm,
    extent=[0.0, 360.0, 0.0, float(ngates_total)]
)

# X 軸主刻度
ax.set_xlabel("Azimuth (degrees)")
ax.set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])

# Y 軸為 bin index
ax.set_ylabel("Bin index along each ray")
ax.set_ylim(0, ngates_total)

# 標題
ax.set_title(f"Ray-Bin Hydrometeor Classes | {station} {time_str} | sweep={sweep_index}")

## === Legend（加上每類數量；只顯示 0..5） ===
# 計數：只統計 0..5 類
class_values_used_list = [0, 1, 2, 3, 4, 5]  # 要顯示在 legend 的類別
mask_0_5 = np.isin(pid_raw_2d, class_values_used_list)  # 只挑 0..5 的像素
vals, cnts = np.unique(pid_raw_2d[mask_0_5].astype(int), return_counts=True)
count_map = {int(v): int(c) for v, c in zip(vals, cnts)}  # 類別值 -> 數量

legend_handles = []
for i, cls in enumerate(class_values_used_list):
    cls_label = label_map_dict[cls]                 # 類別中文名
    cls_count = count_map.get(cls, 0)               # 若沒出現則為 0
    legend_handles.append(
        Patch(facecolor=colors_user_hex[i], edgecolor='black',
              label=f"{cls_label} ({cls_count})")   # 顯示「名稱 (數量)」
    )

ax.legend(handles=legend_handles, title="PID", loc='upper right', frameon=True)


plt.tight_layout()
time_save_path  = f"{time_save_dir}/{time_str}_{pid}_sweep{sweep_index}_ray_bin_class_map.png"
sweep_save_path = f"{sweep_save_dir}/{time_str}_{pid}_sweep{sweep_index}_ray_bin_class_map.png"
plt.savefig(time_save_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
plt.savefig(sweep_save_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
print("✅", time_save_path)
# plt.show()
