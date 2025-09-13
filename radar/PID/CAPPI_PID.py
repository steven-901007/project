import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime, timedelta
from cartopy.io.shapereader import Reader
from pyart.graph import GridMapDisplay
import matplotlib.patches as mpatches
import sys
import os
from glob import glob
import platform
from matplotlib.font_manager import FontProperties
from matplotlib.colors import ListedColormap

## ==== 參數區（維持你的預設與格式）==== ##
year  = sys.argv[1] if len(sys.argv) > 1 else '2024'
month = sys.argv[2] if len(sys.argv) > 2 else '06'
day   = sys.argv[3] if len(sys.argv) > 3 else '02'
station = sys.argv[4] if len(sys.argv) > 4 else 'RCWF'
draw_one_or_all = sys.argv[5] if len(sys.argv) > 5 else 'all'   # 'one' or 'all'
pid = sys.argv[6] if len(sys.argv) > 6 else 'park'               # 'park' 或 'way'
hh = '05'
mm = '17'
ss = '00'
z_target = 4000  # m

## ==== 路徑設定 ==== ##
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/radar"
    flash_data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
else:
    data_top_path = "/home/steven/python_data/radar"
    flash_data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"

## 測站中文名（沿用你的對照）
if station == 'RCWF':
    station_realname = '五分山'
elif station == 'RCCG':
    station_realname = '七股'
elif station == 'RCKT':
    station_realname = '墾丁'
elif station == 'RCHL':
    station_realname = '花蓮'


## ==== 共用資源（font/shp 等只建一次）==== ##
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
shp_reader = Reader(shapefile_path)

myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=12)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=18)
plt.rcParams['axes.unicode_minus'] = False

## 儲存資料夾
save_dir = f"{data_top_path}/PID_CAPPI/{year}{month}{day}"
os.makedirs(save_dir, exist_ok=True)

## ==== 依 pid 準備離散色盤與標籤 ==== ##
def get_pid_cmap_and_labels(pid_name: str):
    if pid_name == 'park':
        # 索引 0..5
        custom_colors = [
            "#1FE4F3FF",  # 0 Rain
            "#ebff0e",    # 1 Melting Layer
            "#2ca02c",    # 2 Wet Snow
            "#27d638",    # 3 Dry Snow
            "#f51010",    # 4 Graupel
            "#3c00ff",    # 5 Hail
        ]
        label_names = ['Rain', 'Melting Layer', 'Wet Snow', 'Dry Snow', 'Graupel', 'Hail']
    elif pid == 'way':
        # 索引 0..10
        custom_colors = [
            "#1FE4F3FF",  # 0 Drizzle
            "#1FE4F3FF",  # 1 Rain（與 0 同色：依你提供）
            "#2ca02c",    # 2 Weak Snow
            "#2ca02c",    # 3 Strong Snow
            "#2ca02c",    # 4 Wet Snow
            "#f51010",    # 5 Dry Graupel
            "#f51010",    # 6 Wet Graupel
            "#3c00ff",    # 7 Small Hail
            "#3c00ff",    # 8 Large Hail
            "#ebff0e",    # 9 Rain-Hail Mixture
            "#f49d07",    # 10 Supercooled water
        ]
        label_names = [
            'Drizzle', 'Rain', 'Weak Snow', 'Strong Snow', 'Wet Snow',
            'Dry Graupel', 'Wet Graupel', 'Small Hail', 'Large Hail',
            'Rain-Hail Mixture', 'Supercooled water'
        ]
    cmap = ListedColormap(custom_colors)
    vmin, vmax = 0, len(custom_colors) - 1
    return cmap, label_names, vmin, vmax

## ==== 資料處理：讀 radar → 建 grid → 找 z_index ==== ##
def process_pid_to_grid(file_path_str, z_target_int):
    """
    讀單一 PID 檔（.nc），建 3D grid，回傳 grid、z_index、時間字串（LCT）、時間物件（UTC）。
    """
    radar = pyart.io.read(file_path_str)

    # 由檔名推時間（YYYYMMDDHHMMSS.nc）
    base_name_str = os.path.basename(file_path_str).replace('.nc', '')
    time_dt_obj = datetime.strptime(base_name_str, "%Y%m%d%H%M%S")
    time_str_LCT_str = (time_dt_obj + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M")

    # 建 grid（沿你的設定）
    grid_obj = pyart.map.grid_from_radars(
        radar,
        grid_shape=(21, 400, 400),
        grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
        fields=['hydro_class'],
        gridding_algo='map_gates_to_grid',
        weighting_function='Barnes',
        roi_func='dist_beam',
    )

    # 找最接近 z_target 的層
    z_levels_arr = grid_obj.z['data']
    z_index_int = np.abs(z_levels_arr - z_target_int).argmin()

    return grid_obj, z_index_int, time_str_LCT_str, time_dt_obj

## ==== 繪圖：給 grid、z_index → 畫 CAPPI 並儲存（依 pid 上色+colorbar） ==== ##
def plot_cappi_and_save(grid_obj, z_index_int, title_time_LCT_str, time_dt_obj,
                        z_target_int, save_dir_str, station_realname_str, pid_name: str):
    """
    將指定層（z_index）之 'hydro_class' 畫成 CAPPI，使用 pid 對應的離散 colormap 與 colorbar。
    """
    # 依 pid 取色盤與標籤
    cmap, label_names, vmin, vmax = get_pid_cmap_and_labels(pid_name)

    display = GridMapDisplay(grid_obj)
    fig = plt.figure(figsize=(10, 10))
    ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

    pm = display.plot_grid(
        field='hydro_class',
        level=z_index_int,
        ax=ax,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        colorbar_flag=False,   # 我們自己畫離散 colorbar
        embellish=False,
        add_grid_lines=False
    )

    # Title
    z_val_m = grid_obj.z['data'][z_index_int]
    ax.set_title(
        f"PID CAPPI（{station_realname_str}）@ {z_val_m/1000:.1f} km\n{title_time_LCT_str}",
        fontproperties=title_font
    )

    # 台灣邊界
    ax.add_geometries(shp_reader.geometries(), crs=ccrs.PlateCarree(),
                      facecolor='none', edgecolor='green')

    # 經緯換算（沿你做法）
    radar_lon = grid_obj.radar_longitude['data'][0]
    radar_lat = grid_obj.radar_latitude['data'][0]
    x_km = grid_obj.x['data'] / 1000
    y_km = grid_obj.y['data'] / 1000
    lon_grid = radar_lon + (x_km / 111) / np.cos(np.radians(radar_lat))
    lat_grid = radar_lat + (y_km / 111)

    # 顯示範圍
    lon_min = np.min(lon_grid); lon_max = np.max(lon_grid)
    lat_min = np.min(lat_grid); lat_max = np.max(lat_grid)
    margin_lon = (lon_max - lon_min) * 0.02
    margin_lat = (lat_max - lat_min) * 0.02
    ax.set_extent([lon_min - margin_lon, lon_max + margin_lon,
                   lat_min - margin_lat, lat_max + margin_lat])

    # Gridlines
    gl = ax.gridlines(draw_labels=True)
    gl.right_labels = False

    # ====== 離散 colorbar（依索引 0..N-1 打刻度+標籤）======
    cbar = plt.colorbar(pm, ax=ax, fraction=0.046, pad=0.02)
    ticks = np.arange(vmin, vmax + 1, 1)
    cbar.set_ticks(ticks)
    # 避免標籤過長擠在一起，可視需要縮小字或旋轉；先用較小字體
    cbar.ax.set_yticklabels(label_names, fontproperties=myfont)

    # 輸出檔名：沿用 time_str 與高度(km)
    time_str_for_name = time_dt_obj.strftime("%Y%m%d%H%M%S")
    save_path = f"{save_dir_str}/{time_str_for_name}_{int(z_target_int/1000)}km_{pid_name}.png"
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"✅ 儲存圖檔：{save_path}")

## ==== 依 one / all 模式組合檔案清單並執行 ==== ##
def main_run():
    date_tag_str = f"{year}{month}{day}"
    pid_dir_str = f"{data_top_path}/PID/{date_tag_str}_{station}_{pid}"

    if draw_one_or_all == 'one':
        time_str = f"{year}{month}{day}{hh}{mm}{ss}"
        file_path = f"{pid_dir_str}/{time_str}.nc"
        file_list = [file_path]
    else:
        file_list = sorted(glob(f"{pid_dir_str}/*.nc"))

    if not file_list:
        print(f"⚠️ 找不到檔案：{pid_dir_str}")
        return

    for file_path in file_list:
        try:
            grid_obj, z_index_int, time_str_LCT_str, time_dt_obj = process_pid_to_grid(
                file_path, z_target
            )
            print(f"選擇切層 z_index={z_index_int}, 對應高度為 {grid_obj.z['data'][z_index_int]} m")

            plot_cappi_and_save(
                grid_obj, z_index_int, time_str_LCT_str, time_dt_obj,
                z_target, save_dir, station_realname, pid
            )
        except Exception as e:
            print(f"❌ 讀取/繪圖失敗：{file_path}\n原因：{e}")

if __name__ == "__main__":
    main_run()
