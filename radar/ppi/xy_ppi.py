import numpy as np
import matplotlib.pyplot as plt
import pyart
import os
import sys

## =========================
## 參數（請確認路徑與欄位）
## =========================
data_top_path = "/home/steven/python_data/radar"
year  = sys.argv[1] if len(sys.argv) > 1 else '2021'
month = sys.argv[2] if len(sys.argv) > 2 else '05'
day   = sys.argv[3] if len(sys.argv) > 3 else '30'
hh    = sys.argv[4] if len(sys.argv) > 4 else '05'
mm    = sys.argv[5] if len(sys.argv) > 5 else '01'
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

## =========================
## 固定表：sweep_index -> 固定仰角 (degree)  # 只用這個表，不讀取經緯度與其他外部資訊
## =========================
SWEEP_ELEV_DEG = {
    0: 0.48,  1: 0.48,
    2: 0.88,  3: 0.88,
    4: 1.32,  5: 1.32,
    6: 1.80,  7: 2.42,
    8: 3.12,  9: 4.00,
    10: 5.10, 11: 6.42,
    12: 8.00, 13: 10.02,
    14: 12.00, 15: 14.02,
    16: 16.70, 17: 19.51,
}
station_altitude_m = 33.0  # 測站高度（公尺）

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

label_map_dict = {
    0: "Rain",
    1: "Melting Layer",
    2: "Wet Snow",
    3: "Dry Snow",
    4: "Graupel",
    5: "Hail",
}
colors_user_hex = ["#1FE4F3FF", "#ebff0e", "#2ca02c", "#27d638", "#f51010", "#3c00ff"]
color_for_fill = "#FFFFFF"   # -999
color_for_unk  = "#BCB8B8FF" # -1
class_values_list = [-999, -1, 0, 1, 2, 3, 4, 5]
color_list = [color_for_fill, color_for_unk, *colors_user_hex]
pid_plot_cmap = ListedColormap(color_list)
bounds_list   = [cv - 0.5 for cv in class_values_list] + [class_values_list[-1] + 0.5]
pid_plot_norm = BoundaryNorm(bounds_list, pid_plot_cmap.N)

## =========================
## 以最接近 0° 的 ray 當作 X=0 起點
## =========================
az_all_deg = radar.azimuth['data'][sweep_slice].astype(float)   # 每條 ray 的真實方位角 (deg)
idx0 = int(np.argmin(np.abs(((az_all_deg - 0.0) + 180.0) % 360.0 - 180.0)))  # 找最接近 0° 的索引
pid_roll_2d = np.roll(pid_raw_2d, -idx0, axis=0)  # (ray, bin)
az_roll_deg = np.roll(az_all_deg, -idx0)
az_shift_deg = (az_roll_deg - az_roll_deg[0]) % 360.0  # az_shift_deg[0] = 0

## =========================
## 取得固定仰角 + BIN 間距（用相鄰 BIN 0 與 1）並套用高度公式
## =========================
if sweep_index not in SWEEP_ELEV_DEG:
    raise KeyError(f"sweep_index {sweep_index} 不在固定表 SWEEP_ELEV_DEG 內")
theta_deg = float(SWEEP_ELEV_DEG[sweep_index])                     # 固定表仰角（度）
theta_rad = np.deg2rad(theta_deg)                                  # 轉弧度
range_data_m_array = radar.range['data'][:ngates_total].astype(float)  # 每個 BIN 中心距離(m)

if ngates_total < 2:
    raise ValueError("gate 數量少於 2，無法計算相鄰 BIN 間距")
bin_i_index = 0
bin_j_index = 1
distance_between_two_bins_m = float(range_data_m_array[bin_j_index] - range_data_m_array[bin_i_index])  # Δr
print(f"選用 BIN {bin_i_index} 與 BIN {bin_j_index} 之間的距離 Δr = {distance_between_two_bins_m:.3f} m")

## === 高度公式（你指定的版）：
## h(N) = sin(theta) * ((N-1) * Δr + 2125) + 33，其中 N 為 BIN數(1-based)
bin_number_1based_array = np.arange(1, ngates_total + 1, dtype=float)           # 1..ngates_total
slant_range_from_offset_m = (bin_number_1based_array - 1) * distance_between_two_bins_m + 2125.0
altitudes_m = np.sin(theta_rad) * slant_range_from_offset_m + station_altitude_m  # 海拔（m, ASL）

## =========================
## 繪圖（X=0..360 角度；Y=海拔高度 m）
## =========================
fig = plt.figure(figsize=(11, 6))
ax  = plt.axes()

im = ax.imshow(
    pid_roll_2d.T,           # (ngates, nrays)
    origin='lower',
    aspect='auto',
    interpolation='nearest',
    cmap=pid_plot_cmap,
    norm=pid_plot_norm,
    extent=[0.0, 360.0, float(altitudes_m[0]), float(altitudes_m[-1])]
)

ax.set_xlabel("Azimuth (degrees)")
ax.set_xticks([0, 45, 90, 135, 180, 225, 270, 315, 360])

ax.set_ylabel("Altitude (m)")
ax.set_ylim(0, 12000)

ax.set_title(
    f"Ray-Bin Hydrometeor Classes | {station} {time_str} | elev={theta_deg:.2f}°"
)

## === Legend（加上每類數量；只顯示 0..5） ===
class_values_used_list = [0, 1, 2, 3, 4, 5]
mask_0_5 = np.isin(pid_raw_2d, class_values_used_list)
vals, cnts = np.unique(pid_raw_2d[mask_0_5].astype(int), return_counts=True)
count_map = {int(v): int(c) for v, c in zip(vals, cnts)}

legend_handles = []
for i, cls in enumerate(class_values_used_list):
    cls_label = label_map_dict[cls]
    cls_count = count_map.get(cls, 0)
    legend_handles.append(
        Patch(facecolor=colors_user_hex[i], edgecolor='black',
              label=f"{cls_label} ({cls_count})")
    )

ax.legend(handles=legend_handles, title="PID", loc='upper right', frameon=True)

plt.tight_layout()
time_save_path  = f"{time_save_dir}/{time_str}_{pid}_sweep{sweep_index}_ray_bin_class_map.png"
sweep_save_path = f"{sweep_save_dir}/{time_str}_{pid}_sweep{sweep_index}_ray_bin_class_map.png"
plt.savefig(time_save_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
plt.savefig(sweep_save_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
print("✅", time_save_path)
# plt.show()
