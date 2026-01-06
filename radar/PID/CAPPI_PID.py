import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy import geodesic  # 畫地理圓
from datetime import datetime, timedelta
from cartopy.io.shapereader import Reader
from pyart.graph import GridMapDisplay
import platform, os, sys
from glob import glob
from matplotlib.font_manager import FontProperties
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
from matplotlib.ticker import FormatStrFormatter
import matplotlib.ticker as mticker
plt.rcParams['axes.grid'] = False

# =========================
# 基本參數（請確認路徑與欄位）
# =========================
year  = sys.argv[1] if len(sys.argv) > 1 else '2021'
month = sys.argv[2] if len(sys.argv) > 2 else '05'
day   = sys.argv[3] if len(sys.argv) > 3 else '24'
station = sys.argv[4] if len(sys.argv) > 4 else 'RCWF'
draw_mode = sys.argv[5] if len(sys.argv) > 5 else 'all'   # "one" 或 "all"
pid = sys.argv[6] if len(sys.argv) > 6 else 'park'        # "park" 或 "way"
hh, mm, ss = "08", "24", "00"
z_target = float(sys.argv[7]) if len(sys.argv) > 7 else 3000  # m

# 可選：圈線寬、標數字的步長（1=每格都標；大一點更快更不擁擠）
circle_linewidth = 0.5
label_stride = 1

if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/radar"
else:
    data_top_path = "/home/steven/python_data/radar"

shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
shp_reader = Reader(shapefile_path)
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=12)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=18)

save_dir = f"{data_top_path}/PID_CAPPI/{year}{month}{day}/{station}/{round(z_target/1000)}km"
os.makedirs(save_dir, exist_ok=True)

# ===== 固定仰角列表（照你的截圖） =====
fixed_elevations_deg_list = [
    0.48, 0.48, 0.88, 0.88, 1.32, 1.32, 1.80, 2.42,
    3.12, 4.00, 5.10, 6.42, 8.00, 10.02, 12.00, 14.02,
    16.70, 19.51
]

# =========================
# color/label 定義
# =========================
def make_discrete_colorbar(pid_str: str):
    # 只定義離散顏色，不使用 pyart.graph.cm
    if pid_str == "park":
        colors = ["#1FE4F3FF", "#ebff0e", "#2ca02c", "#27d638", "#f51010", "#3c00ff"]
        labels = ["Rain", "Melting Layer", "Wet Snow", "Dry Snow", "Graupel", "Hail"]
        vmin, vmax = 0, len(colors) - 1
    else:
        colors = ["#1FE4F3FF", "#1FE4F3FF", "#2ca02c", "#2ca02c", "#2ca02c",
                  "#f51010", "#f51010", "#3c00ff", "#3c00ff", "#ebff0e", "#f49d07"]
        labels = ["Drizzle", "Rain", "Weak Snow", "Strong Snow", "Wet Snow",
                  "Dry Graupel", "Wet Graupel", "Small Hail", "Large Hail",
                  "Rain-Hail Mix", "Supercooled water"]
        vmin, vmax = 0, len(colors) - 1
    cmap = ListedColormap(colors)
    return cmap, labels, vmin, vmax

# =========================
# 讀檔→gridding→回傳 grid 與 z 索引、雷達經緯
# =========================
def process_pid_to_grid(station,file_path: str, z_target_m: float):
    radar = pyart.io.read(file_path)
    base = os.path.basename(file_path).replace(".nc", "")
    t_utc_dt = datetime.strptime(base, "%Y%m%d%H%M%S")
    t_lct_str = (t_utc_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M")


    if station == 'RCWF':
        grid = pyart.map.grid_from_radars(
            radar,
            grid_shape=(21, 400, 400),
            grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
            fields=["hydro_class"],
            gridding_algo="map_gates_to_grid",
            weighting_function="Nearest",
            roi_func="dist",        # ← 改用距離相依 ROI
            z_factor=0.04,          # 每↑1 m（高度），ROI 增 0.04 m
            xy_factor=0.005,         # 每↑1 m（水平距），ROI 增 0.005 m
            min_radius=500.0,       # ROI 不小於 500 m
            copy_field_data=True
        )
    elif station == 'RCCG':
        grid = pyart.map.grid_from_radars(
            radar,
            grid_shape=(21, 400, 400),
            grid_limits=((0, 10000), (-125000, 125000), (-125000, 125000)),
            fields=["hydro_class"],
            gridding_algo="map_gates_to_grid",
            weighting_function="Nearest",
            roi_func="dist",        # ← 改用距離相依 ROI
            z_factor=0.04,          # 每↑1 m（高度），ROI 增 0.04 m
            xy_factor=0.009,         # 每↑1 m（水平距），ROI 增 0.009 m
            min_radius=600.0,       # ROI 不小於 600 m
            copy_field_data=True
        )

    # 印原始代碼確認
    pid_grid = grid.fields["hydro_class"]["data"]
    raw_vals = np.unique(pid_grid.compressed().astype(int)) if np.ma.is_masked(pid_grid) else np.unique(pid_grid.astype(int))
    print("Grid 上的 hydro_class 原始代碼：", raw_vals)

    z_index = int(np.abs(grid.z["data"] - z_target_m).argmin())

    radar_lat = float(radar.latitude['data'][0])
    radar_lon = float(radar.longitude['data'][0])

    return grid, z_index, t_lct_str, t_utc_dt, radar_lat, radar_lon

# =========================
def plot_cappi(grid, z_index: int, t_lct: str, t_utc, z_target_m: float,
               pid_str: str, radar_lat: float, radar_lon: float):
    import matplotlib as mpl  # 放在函式內，避免全域缺少

    # --- 類別與色表 ---
    cmap, labels, vmin, vmax = make_discrete_colorbar(pid_str)
    ncat = len(labels)

    # --- 取該層資料，先「變成整數類別」(0..ncat-1)，保留 mask ---
    layer_ma = grid.fields["hydro_class"]["data"][z_index]   # (ny, nx) MaskedArray
    layer_codes = np.rint(layer_ma)                          # 四捨五入
    layer_codes = np.ma.clip(layer_codes, 0, ncat - 1)       # 夾在合法類別
    codes_int = layer_codes.astype(np.int16)                 # 轉整數代碼 (仍保留 mask)

    # --- 取得該層每個格點中心的經緯度 ---
    lats_2d = grid.point_latitude['data'][z_index]   # (ny, nx)
    lons_2d = grid.point_longitude['data'][z_index]  # (ny, nx)

    # --- 直接把代碼映射成 RGBA 顏色陣列（逐格指定顏色，不做任何 norm） ---
    ny, nx = codes_int.shape
    rgba_grid = np.zeros((ny, nx, 4), dtype=float)          # 預設透明
    valid_mask = ~np.ma.getmaskarray(codes_int)             # 有效格
    # 建 LUT：把離散色表轉成 RGBA
    lut = np.array([mpl.colors.to_rgba(c) for c in cmap.colors])  # (ncat, 4)
    # 依代碼索引 LUT 填色
    if np.any(valid_mask):
        rgba_grid[valid_mask] = lut[codes_int[valid_mask]]

    # --- 畫底圖/座標系 ---
    fig = plt.figure(figsize=(10, 10))
    ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

    # 直接用顏色網格畫（不經 colormap/norm），確保顏色==數字
    # 用 shading='nearest' 讓每個中心值填滿自己的格
    quad = ax.pcolormesh(
        lons_2d, lats_2d, rgba_grid,
        shading='nearest', transform=ccrs.PlateCarree()
    )

    ax.set_xlabel(""); ax.set_ylabel("")

    # --- ticks / extent 與地圖邊界 ---
    if station == 'RCWF':
        xtick_list = [120,120.5,121,121.5,122,122.5,123,123.5]
        ytick_list = [23.5,24,24.5,25,25.5,26,26.5]
    elif station == 'RCCG':
        xtick_list = [118.5,119,119.5,120,120.5,121,121.5,122]
        ytick_list = [21.5,22,22.5,23,23.5,24,24.5]
    else:
        xtick_list = [120,120.5,121,121.5,122,122.5]
        ytick_list = [23.5,24,24.5,25,25.5]

    ax.set_xticks(xtick_list, crs=ccrs.PlateCarree())
    ax.set_yticks(ytick_list, crs=ccrs.PlateCarree())
    ax.set_extent([min(xtick_list), max(xtick_list), min(ytick_list), max(ytick_list)],
                  crs=ccrs.PlateCarree())

    ax.xaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False,
                      linestyle='-', linewidth=1, color='gray', alpha=0.6)
    gl.xlocator = mticker.FixedLocator(xtick_list)
    gl.ylocator = mticker.FixedLocator(ytick_list)

    ax.add_geometries(shp_reader.geometries(), ccrs.PlateCarree(),
                      facecolor="none", edgecolor="black")

    # # --- 疊上每格數字（與顏色完全同源：codes_int） ---
    # # label_stride=1 會很密，必要時可調大
    # for j in range(0, ny, label_stride):
    #     row = codes_int[j]
    #     for i in range(0, nx, label_stride):
    #         if np.ma.is_masked(row[i]):
    #             continue
    #         iv = int(row[i])
    #         ax.text(lons_2d[j, i], lats_2d[j, i], str(iv),
    #                 transform=ccrs.PlateCarree(),
    #                 fontsize=1, ha='center', va='center', alpha=1)

    # # --- 畫仰角圈（每個 sweep 不同顏色） ---
    # G = geodesic.Geodesic()
    # sweep_cmap = plt.get_cmap('tab20', len(fixed_elevations_deg_list))
    # circle_handles_list, circle_labels_list = [], []
    # for si, elev_deg in enumerate(fixed_elevations_deg_list):
    #     if elev_deg <= 0:
    #         continue
    #     dis_km = (z_target_m / 1000.0) / np.tan(np.deg2rad(elev_deg))
    #     radius_m = dis_km * 1000.0
    #     color_i = sweep_cmap(si)
    #     circle = G.circle(lon=radar_lon, lat=radar_lat,
    #                       radius=radius_m, n_samples=180, endpoint=False)
    #     h, = ax.plot(circle[:, 0], circle[:, 1], color=color_i, linestyle='--',
    #                  linewidth=circle_linewidth, transform=ccrs.PlateCarree())
    #     circle_handles_list.append(h)
    #     circle_labels_list.append(f"S{si}  {elev_deg:.2f}°")

    # --- 標題與圖例 ---
    z_val_m = float(grid.z["data"][z_index])
    ax.set_title(f"{z_val_m/1000:.1f} km PID = {pid_str}\n{t_lct} LST",
                 fontproperties=title_font)

    # PID legend（用離散色表的第 i 色）
    pid_legend_handles = [
        Patch(facecolor=cmap.colors[i], edgecolor='k', label=labels[i])
        for i in range(ncat)
    ]
    leg_pid = ax.legend(handles=pid_legend_handles, loc='lower right',
                        fontsize=10, frameon=True, prop=myfont, title="PID")

    # leg_ang = ax.legend(circle_handles_list, circle_labels_list, loc='upper left',
    #                     fontsize=9, frameon=True,
    #                     title=f"仰角圈 (z={z_target_m/1000:.1f} km)")
    ax.add_artist(leg_pid)

    # --- 存檔 ---
    out_path = f"{save_dir}/{station}_{t_utc.strftime('%Y%m%d%H%M%S')}_{int(z_target_m/1000)}km_{pid_str}.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight", pad_inches=0.1)
    plt.close()
    print("✅", out_path)

# =========================
# 主程式
# =========================
date_tag = f"{year}{month}{day}"
pid_dir = f"{data_top_path}/PID/{date_tag}_{station}_{pid}"

if draw_mode == "one":
    time_str = f"{year}{month}{day}{hh}{mm}{ss}"
    file_list = [f"{pid_dir}/{time_str}.nc"]
else:
    file_list = sorted(glob(f"{pid_dir}/*.nc"))

if not file_list:
    print("⚠️ 找不到檔案：", pid_dir)
else:
    for f in file_list:
        try:
            grid, z_idx, t_lct, t_utc, radar_lat, radar_lon = process_pid_to_grid(station,f, z_target)
            if "hydro_class" not in grid.fields:
                raise KeyError("Grid 內找不到欄位 'hydro_class'")
            plot_cappi(grid, z_idx, t_lct, t_utc, z_target, pid, radar_lat, radar_lon)
        except Exception as e:
            print("❌", f, e)
