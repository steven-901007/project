import numpy as np
import matplotlib.pyplot as plt
import pyart
import os
import sys

## =========================
## 參數（請確認路徑與欄位）
## =========================
data_top_path = "/home/steven/python_data/radar"
year = sys.argv[1] if len(sys.argv) > 1 else '2024'
month = sys.argv[2] if len(sys.argv) > 2 else '06'
day = sys.argv[3] if len(sys.argv) > 3 else '02'
hh = sys.argv[4] if len(sys.argv) > 4 else '08'
mm = sys.argv[5] if len(sys.argv) > 5 else '24'
pid = 'park'  # park or way(魏) 使用哪個PID

ss = '00'
station = 'RCWF'
vol_file_path = f"{data_top_path}/PID/{year}{month}{day}_{station}_{pid}/{year}{month}{day}{hh}{mm}{ss}.nc"  # 檔案路徑
sweep_index = int(sys.argv[6]) if len(sys.argv) > 6 else 0  # 要畫第幾個 sweep（0 起算）
field_name = "hydro_class"  # ['velocity','reflectivity','differential_reflectivity','differential_phase','cross_correlation_ratio','spectrum_width','kdp_maesaka','hydro_class']
time_str = f"{year}{month}{day}{hh}{mm}{ss}"

## （可選）點大小參數：近小遠大（單位：points^2）
dot_size_min = 0.001
dot_size_max = 5.0

time_save_dir = f"{data_top_path}/PID_PPI/{year}{month}{day}/{time_str}/ppi"
os.makedirs(time_save_dir, exist_ok=True)
sweep_save_dir = f"{data_top_path}/PID_PPI/{year}{month}{day}/sweep{sweep_index}/ppi"
os.makedirs(sweep_save_dir, exist_ok=True)

## 讀檔
radar = pyart.io.read(vol_file_path)
if field_name not in radar.fields:
    raise KeyError(f"檔案內找不到欄位 {field_name}，可用欄位：{list(radar.fields.keys())}")

## 取出該 sweep 的資料 + 印原始值（不遮罩、不改值；保留原本輸出格式）
sweep_slice = radar.get_slice(sweep_index)
pid_data_2d_array = radar.fields[field_name]["data"][sweep_slice]  # shape: (nrays, ngates)

if isinstance(pid_data_2d_array, np.ma.MaskedArray):
    pid_raw_2d = pid_data_2d_array.astype(float).filled(np.nan)  # 先變 float 再填 NaN
else:
    pid_raw_2d = pid_data_2d_array.astype(float)  # 後續要用 isfinite，統一用 float

nrays_sweep, ngates_total = pid_raw_2d.shape
# print("ray_index,bin_index,value")
for ray_idx in range(nrays_sweep):
    row = pid_raw_2d[ray_idx]
    for bin_idx in range(ngates_total):
        v = row[bin_idx]
        # if not np.isnan(v):
        #     print(f"{ray_idx},{bin_idx},{v}")

## =========================
## PPI：每個 bin 畫成圓點（距離線性縮放），加台灣地圖與類別圖例
## =========================
from pyart.graph import RadarMapDisplay
import cartopy.crs as ccrs
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from cartopy.io.shapereader import Reader

## 類別對應表（只保留 0–5 六類）
label_map_dict = {
    0: "Rain",
    1: "Melting Layer",
    2: "Wet Snow",
    3: "Dry Snow",
    4: "Graupel",
    5: "Hail",
}

## 顏色（你的 hex；順序對應 0..5）
colors_user_hex = ["#1FE4F3FF", "#ebff0e", "#2ca02c", "#27d638", "#f51010", "#3c00ff"]

## 要顯示的類別順序（僅 0..5）
class_values_used_list = [0, 1, 2, 3, 4, 5]

## 建立離散 colormap 與 norm（這裡用在 scatter 的 c/norm）
pid_plot_cmap = ListedColormap(colors_user_hex)
bounds_list = [cv - 0.5 for cv in class_values_used_list] + [class_values_used_list[-1] + 0.5]
pid_plot_norm = BoundaryNorm(bounds_list, pid_plot_cmap.N)

## 地圖座標軸（台灣邊界）
display = RadarMapDisplay(radar)
fig = plt.figure(figsize=(10, 8))
ax = plt.axes(projection=ccrs.PlateCarree())

shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
ax.add_geometries(
    Reader(shapefile_path).geometries(),
    crs=ccrs.PlateCarree(),
    facecolor='none',
    edgecolor='black',
    linewidth=1,
)

## 設定視窗（以雷達位置與最大量測距離）
rad_lat = float(radar.latitude['data'][0])
rad_lon = float(radar.longitude['data'][0])
deg_buf = 2
ax.set_extent([rad_lon - deg_buf, rad_lon + deg_buf,
               rad_lat - deg_buf, rad_lat + deg_buf], crs=ccrs.PlateCarree())

## 取得每個 bin 的經緯度與距離（與 sweep 對齊）
gate_lat_2d, gate_lon_2d, gate_alt_2d = radar.get_gate_lat_lon_alt(sweep_index)  # shape: (nrays, ngates)

# range_1d: 每個 gate 中心到雷達的距離（公尺）
range_1d = radar.range["data"][:gate_lon_2d.shape[1]]  # ngates 長度
# 擴展成與 (nrays, ngates) 相同形狀
range_2d = np.broadcast_to(range_1d, gate_lon_2d.shape)

## 扁平化
gate_lon_1d = gate_lon_2d.reshape(-1)
gate_lat_1d = gate_lat_2d.reshape(-1)
pid_flat_1d = pid_raw_2d.reshape(-1)
range_flat_1d = range_2d.reshape(-1)

## 僅保留 0..5 類（其餘類別與 NaN 不畫）
valid_mask_bool = np.isin(pid_flat_1d, class_values_used_list) & np.isfinite(pid_flat_1d)
lon_valid_1d = gate_lon_1d[valid_mask_bool]
lat_valid_1d = gate_lat_1d[valid_mask_bool]
pid_valid_1d = pid_flat_1d[valid_mask_bool].astype(float)
range_valid_1d = range_flat_1d[valid_mask_bool]

## 按距離做線性大小縮放：近小遠大（先檢查是否有任何有效資料）
if range_valid_1d.size == 0:
    print("[WARN] 此 sweep 沒有有效資料，畫空白圖。")
    size_arr = np.array([], dtype=float)  # 空
    # （可選）標註提示；如不需要可刪除下一段
    ax.text(0.5, 0.5, "No valid data", ha="center", va="center",
            fontsize=16, color="red", transform=ax.transAxes)
else:
    r_min = np.nanmin(range_valid_1d)
    r_max = np.nanmax(range_valid_1d)

    # 避免除以 0 或非有限數
    if not np.isfinite(r_min) or not np.isfinite(r_max) or r_max <= r_min:
        size_arr = np.full_like(range_valid_1d, (dot_size_min + dot_size_max) * 0.5, dtype=float)
    else:
        w = (range_valid_1d - r_min) / (r_max - r_min)  # 0..1
        size_arr = dot_size_min + w * (dot_size_max - dot_size_min)

## 以 scatter 分類分層疊圖：數字越大越上層
for cls in sorted(class_values_used_list):  # 0,1,2,3,4,5；後面較大會畫在上面
    mask_cls_bool = (pid_valid_1d == cls)
    if not np.any(mask_cls_bool):
        continue
    ax.scatter(
        lon_valid_1d[mask_cls_bool],
        lat_valid_1d[mask_cls_bool],
        c=np.full(np.count_nonzero(mask_cls_bool), cls, dtype=float),  # 用 colormap/norm 上色
        cmap=pid_plot_cmap,
        norm=pid_plot_norm,
        s=size_arr[mask_cls_bool],   # 距離縮放後的點大小（你前面已算好）
        marker='o',
        linewidths=0,
        alpha=1.0,
        transform=ccrs.PlateCarree(),
        zorder=10 + cls              # 類別值越大 zorder 越高 → 越在上層
    )

## 輸出 sweep 仰角資訊
print(radar.fixed_angle['data'])
elev_deg = float(radar.fixed_angle['data'][sweep_index])
print(f"Sweep {sweep_index} 固定仰角 = {elev_deg}°")

## 標出雷達位置
ax.plot(rad_lon, rad_lat, marker='o', markersize=2, color='orange', transform=ccrs.PlateCarree())

## === Legend（含每類數量） ===
vals_used_1d, counts_used_1d = np.unique(pid_valid_1d.astype(int), return_counts=True) if pid_valid_1d.size > 0 else (np.array([], dtype=int), np.array([], dtype=int))
count_map_dict = {int(v): int(c) for v, c in zip(vals_used_1d, counts_used_1d)}

legend_handles_list = []
for i, cls in enumerate(class_values_used_list):
    label = label_map_dict[cls]
    n = count_map_dict.get(cls, 0)
    legend_handles_list.append(
        Patch(facecolor=colors_user_hex[i], edgecolor='black', label=f"{label} ({n})")
    )

ax.legend(handles=legend_handles_list, title="Hydrometeor Class", loc='lower left', frameon=True)

## 標題與外觀
ax.set_title(f"PID scatter (distance-scaled dots) | {station} {time_str} | sweep={sweep_index}")
ax.set_xticks([])  # 不顯示座標刻度
ax.set_yticks([])

plt.tight_layout()

## 存檔
time_save_path = f"{time_save_dir}/{time_str}_{pid}_sweep{sweep_index}_map.png"
plt.savefig(time_save_path, dpi=600, bbox_inches="tight", pad_inches=0.1)
print("✅", time_save_path)
sweep_save_path = f"{sweep_save_dir}/{time_str}_{pid}_sweep{sweep_index}_map.png"
plt.savefig(sweep_save_path, dpi=600, bbox_inches="tight", pad_inches=0.1)
# plt.show()
