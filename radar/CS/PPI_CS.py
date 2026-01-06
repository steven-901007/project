'''
繪製CS 但只支援PPI畫法
選擇某個角度的PPI來畫CS截面
並且附上那個角度的CV圖
'''

import numpy as np
import matplotlib.pyplot as plt
import pyart
import os
import sys
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
import cartopy.crs as ccrs
from cartopy.geodesic import Geodesic  # 修正：正確的匯入方式

## =========================
## 參數設定
## =========================
data_top_path = "/home/steven/python_data/radar"
year  = sys.argv[1] if len(sys.argv) > 1 else '2021'
month = sys.argv[2] if len(sys.argv) > 2 else '05'
day   = sys.argv[3] if len(sys.argv) > 3 else '30'
hh    = sys.argv[4] if len(sys.argv) > 4 else '05'
mm    = sys.argv[5] if len(sys.argv) > 5 else '01'
pid   = 'park'  # park or way

# 要切 CS 的方位角 (例如 90 度)
target_azimuth = float(sys.argv[6]) if len(sys.argv) > 6 else 315.0

# ✅ 新增：CS 觀看距離範圍（單位：公尺）
cs_r_min_m = float(sys.argv[7]) if len(sys.argv) > 7 else 0000       # 距離測站幾公尺開始
cs_r_max_m = float(sys.argv[8]) if len(sys.argv) > 8 else 250000       # 距離測站幾公尺結束

# 轉成 km（方便後面用）
cs_r_min_km = cs_r_min_m / 1000.0
cs_r_max_km = cs_r_max_m / 1000.0

ss = '00'
station = 'RCWF'
vol_file_path = f"{data_top_path}/PID/{year}{month}{day}_{station}_{pid}/{year}{month}{day}{hh}{mm}{ss}.nc"
field_name = "hydro_class"
time_str = f"{year}{month}{day}{hh}{mm}{ss}"

# 存檔路徑
save_dir = f"{data_top_path}/PID_CS/{year}{month}{day}/{time_str}"
os.makedirs(save_dir, exist_ok=True)

from matplotlib.font_manager import FontProperties
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
plt.rcParams['axes.unicode_minus'] = False

##測站名
if station == 'RCWF':
    station_realname = '五分山'
elif station == 'RCCG':
    station_realname = '七股'
elif station == 'RCKT':
    station_realname = '墾丁'
elif station == 'RCHL':
    station_realname = '花蓮'
else:
    station_realname = station  # 萬一有其他站名

## =========================
## 1. 讀檔與準備顏色
## =========================
if not os.path.exists(vol_file_path):
    print(f"File not found: {vol_file_path}")
    sys.exit(1)

radar = pyart.io.read(vol_file_path)

# --- 顏色定義 (沿用你的設定，補上 Unknown) ---
label_map_dict = {
    -1: "Unknown",
    0: "Rain",
    1: "Melting Layer",
    2: "Wet Snow",
    3: "Dry Snow",
    4: "Graupel",
    5: "Hail",
}

colors_user_hex = ["#1FE4F3FF", "#ebff0e", "#2ca02c", "#27d638", "#f51010", "#3c00ff"]
color_for_fill = "#FFFFFF"
color_for_unk  = "#BCB8B8FF"

class_values_list = [-999, -1, 0, 1, 2, 3, 4, 5]  # 包含 fill, Unknown, 0~5
color_list = [color_for_fill, color_for_unk, *colors_user_hex]
pid_plot_cmap = ListedColormap(color_list)
bounds_list   = [cv - 0.5 for cv in class_values_list] + [class_values_list[-1] + 0.5]
pid_plot_norm = BoundaryNorm(bounds_list, pid_plot_cmap.N)

## =========================
## 2. 提取 Cross-Section 資料 (Pseudo-RHI)
## =========================
r_matrix = []   # 距離 (km)
z_matrix = []   # 高度 (km)
v_matrix = []   # 數值 (PID)
used_sweeps = []

n_bins = radar.ngates
print(f"Extracting Azimuth {target_azimuth} from {radar.nsweeps} sweeps...")

for sw_idx in range(radar.nsweeps):
    sweep_slice = radar.get_slice(sw_idx)
    azimuths = radar.azimuth['data'][sweep_slice]

    # 與 target_azimuth 的差（考慮 0/360）
    diff = np.abs(azimuths - target_azimuth)
    diff = np.where(diff > 180, 360 - diff, diff)
    ray_local_idx = np.argmin(diff)

    # 若偏差太大，略過這層
    if diff[ray_local_idx] > 5.0:
        continue

    full_idx = sweep_slice.start + ray_local_idx

    # PID 值
    ray_data = radar.fields[field_name]['data'][full_idx]

    # 幾何
    r_m = radar.range['data']  # m
    ele_deg = float(radar.elevation['data'][full_idx])
    ele_rad = np.deg2rad(ele_deg)

    # 地面投影距離與高度（簡化幾何）
    dist_km = (r_m * np.cos(ele_rad)) / 1000.0  # km
    height_km = (r_m * np.sin(ele_rad) + radar.altitude['data'][0]) / 1000.0  # km

    r_matrix.append(dist_km)
    z_matrix.append(height_km)
    v_matrix.append(ray_data)
    used_sweeps.append(sw_idx)

# 轉陣列
if len(r_matrix) == 0:
    print("⚠️ 這個體掃檔在各層都找不到足夠接近的方位角（>5°），請換一個 azimuth。")
    sys.exit(0)

r_arr = np.array(r_matrix)  # (nsweeps_used, nbins) 單位 km
z_arr = np.array(z_matrix)
v_arr = np.array(v_matrix)

# Mask 填補
if isinstance(v_arr, np.ma.MaskedArray):
    v_arr = v_arr.filled(-999)

## =========================
## 3. 繪圖 (1 row, 2 cols)
## =========================
fig = plt.figure(figsize=(16, 7))
ax_cv = fig.add_subplot(1, 2, 1, projection=ccrs.PlateCarree())  # 修正：地圖軸需帶投影
ax_cs = fig.add_subplot(1, 2, 2)

# --- 左圖：Composite Reflectivity (CV) ---
GRID_SHAPE = (31, 241, 241)
GRID_LIMITS = ((0, 15000), (-150000, 150000), (-150000, 150000))
COMPOSITE_FIELD = 'reflectivity'

grid = pyart.map.grid_from_radars(
    radar,
    grid_shape=GRID_SHAPE,
    grid_limits=GRID_LIMITS,
    fields=[COMPOSITE_FIELD],
    weighting_function='nearest',  # 修正：Py-ART 參數小寫
)

x = grid.x['data'] / 1000  # km
y = grid.y['data'] / 1000
z = grid.z['data']         # m

radar_lon = float(radar.longitude['data'][0])
radar_lat = float(radar.latitude['data'][0])

# 計算「最小可達 beam 高度」遮罩
x2d, y2d = np.meshgrid(x * 1000, y * 1000)  # m
rng = np.sqrt(x2d**2 + y2d**2)              # m

sweep_elevs = radar.fixed_angle['data']
beam_heights = []
for elev in sweep_elevs:
    # 4/3 地球半徑近似（單位 m）
    Re = 8500000.0
    h_beam = np.sqrt(rng**2 + Re**2 + 2 * rng * Re * np.sin(np.radians(elev))) - Re
    beam_heights.append(h_beam)
min_beam_height = np.min(np.array(beam_heights), axis=0)

# 取 Composite
reflectivity_data = grid.fields[COMPOSITE_FIELD]['data']  # (nz, ny, nx)
for i in range(reflectivity_data.shape[0]):
    height_layer_m = z[i]  # 這層中心高度（m）
    # 高度低於當層可達最小 beam → 設 NaN
    reflectivity_data[i][height_layer_m < min_beam_height] = np.nan

comp_reflect = np.nanmax(reflectivity_data, axis=0)  # (ny, nx)

# 經緯度格點（小範圍近似）
lon_grid = radar_lon + (x / 111.0) / np.cos(np.radians(radar_lat))
lat_grid = radar_lat + (y / 111.0)



ax_cv.set_title(
    f"Composite Reflectivity CV - {station_realname}\n{time_str} Z",
    fontproperties=title_font,
    fontsize=14
)

mesh_cv = ax_cv.pcolormesh(
    lon_grid, lat_grid, comp_reflect,
    cmap='NWSRef', vmin=0, vmax=65,
    transform=ccrs.PlateCarree()
)

# 設範圍
lon_min, lon_max = float(np.min(lon_grid)), float(np.max(lon_grid))
lat_min, lat_max = float(np.min(lat_grid)), float(np.max(lat_grid))
margin_lon = (lon_max - lon_min) * 0.02
margin_lat = (lat_max - lat_min) * 0.02
ax_cv.set_extent(
    [lon_min - margin_lon, lon_max + margin_lon,
     lat_min - margin_lat, lat_max + margin_lat],
    crs=ccrs.PlateCarree()
)

from cartopy.io.shapereader import Reader
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
# 台灣邊界
ax_cv.add_geometries(
    Reader(shapefile_path).geometries(),
    crs=ccrs.PlateCarree(),
    facecolor='none',
    edgecolor='gray',
    linewidth=1,
)

cbar_cv = plt.colorbar(mesh_cv, ax=ax_cv, orientation='vertical', pad=0.05, shrink=0.8)
cbar_cv.set_label("dBZ", fontproperties=myfont)

# --- 畫出切面線（只畫距離 [cs_r_min_m, cs_r_max_m] 這一段） ---
geod = Geodesic()
points = [[radar_lon, radar_lat]]

# 起點：距離測站 cs_r_min_m
start_ll = geod.direct(
    points,
    [target_azimuth],
    [cs_r_min_m]   # 公尺
)
# 終點：距離測站 cs_r_max_m
end_ll = geod.direct(
    points,
    [target_azimuth],
    [cs_r_max_m]   # 公尺
)

start_lon = float(start_ll[0][0])
start_lat = float(start_ll[0][1])
cut_lon   = float(end_ll[0][0])
cut_lat   = float(end_ll[0][1])

ax_cv.plot(
    [start_lon, cut_lon], [start_lat, cut_lat],
    color='black', linewidth=2.5, linestyle='-',zorder=3,
    transform=ccrs.PlateCarree()
)
ax_cv.plot(
    [start_lon, cut_lon], [start_lat, cut_lat],
    color='w', linewidth=3.5, linestyle='-',zorder=2,
    transform=ccrs.PlateCarree()
)
ax_cv.plot(
    [radar_lon, start_lon], [radar_lat, start_lat],
    color='black', linewidth=1, linestyle='--',
    transform=ccrs.PlateCarree()
)

ax_cv.plot(radar_lon, radar_lat, 'ro',color = 'black', transform=ccrs.PlateCarree())

# =========================
# 右圖：Cross Section (CS)（散佈圖版本）
# =========================
# 將 (nsweeps, nbins) 攤平成 1D 才能 scatter
r_flat = r_arr.flatten()    # km
z_flat = z_arr.flatten()    # km
v_flat = v_arr.flatten()    # PID 值

# ✅ 只畫非 fill (-999) + 距離在 [cs_r_min_km, cs_r_max_km] 的點
valid_mask = (
    (v_flat != -999) &
    (r_flat >= cs_r_min_km) &
    (r_flat <= cs_r_max_km)
)
r_plot = r_flat[valid_mask]
z_plot = z_flat[valid_mask]
v_plot = v_flat[valid_mask].astype(int)

# 顏色依類別取，用 cmap+norm 保證一致
colors_plot = pid_plot_cmap(pid_plot_norm(v_plot))

ax_cs.scatter(
    r_plot, z_plot,
    c=colors_plot,
    s=2,
    marker='o',
    edgecolors='none'
)

ax_cs.set_xlabel("Distance from Radar (km)")
ax_cs.set_ylabel("Height (km)")
ax_cs.set_title(
    f"Cross Section | Azimuth: {target_azimuth}° | "
    f"{time_str}\nRange: {cs_r_min_km:.1f}-{cs_r_max_km:.1f} km"
)
ax_cs.grid(True, linestyle=':', alpha=0.6)
ax_cs.set_ylim(0, 10)  # km
ax_cs.set_xlim(cs_r_min_km, cs_r_max_km)

# Legend（按類別顏色顯示，包含 Unknown）
legend_classes = [-1, 0, 1, 2, 3, 4, 5]  # 不含 -999（fill）

# ✅ Legend 也只統計距離在 [cs_r_min_km, cs_r_max_km] 的點
radial_mask_2d = (r_arr >= cs_r_min_km) & (r_arr <= cs_r_max_km)
mask_legend = np.isin(v_arr, legend_classes) & radial_mask_2d

vals, cnts = np.unique(v_arr[mask_legend].astype(int), return_counts=True)
count_map = {int(v): int(c) for v, c in zip(vals, cnts)}

legend_handles = []
for cls in legend_classes:
    if cls not in label_map_dict:
        continue
    cls_label = label_map_dict[cls]
    face_color = pid_plot_cmap(pid_plot_norm(cls))
    legend_handles.append(
        Patch(facecolor=face_color, edgecolor='black', label=f"{cls_label}")
    )

ax_cs.legend(handles=legend_handles, title="PID (in CS)", loc='upper right', frameon=True)

plt.tight_layout()
file_name = f"{time_str}_{pid}_AZ_{int(target_azimuth)}_CS.png"
save_path = os.path.join(save_dir, file_name)
plt.savefig(save_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
print(f"✅ Saved: {save_path}")
plt.show()
