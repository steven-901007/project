import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime, timedelta
from cartopy.io.shapereader import Reader
from pyart.graph import GridMapDisplay
import matplotlib.patches as mpatches
import sys

year = sys.argv[1] if len(sys.argv) > 1 else '2021'
month = sys.argv[2] if len(sys.argv) > 2 else '05'
day = sys.argv[3] if len(sys.argv) > 3 else '31'
hh = '05'
mm = '17'
ss = '00'

z_target = 4000

import platform
## ==== 路徑設定 ==== ##
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/radar"
    flash_data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/radar"
    flash_data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"

# ==== 路徑與時間設定 ====


time_str = f"{year}{month}{day}{hh}{mm}{ss}"
file_path = f"{data_top_path}/PID/{year}{month}{day}/{time_str}.nc"
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"


# ==== 中文顯示設定 ====
from matplotlib.font_manager import FontProperties
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
plt.rcParams['axes.unicode_minus'] = False

# ==== 讀取雷達資料 ====
radar = pyart.io.read(file_path)
time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")  # datetime 型別
time_str_LCT = (time_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M")  # 字串格式
# ==== 製作 Grid ====
grid = pyart.map.grid_from_radars(
    radar,
    grid_shape=(21, 400, 400),
    grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
    fields=['hydro_class'],
    gridding_algo='map_gates_to_grid',
    weighting_function='Barnes',
    roi_func='dist_beam',
)
# ==== 找出距離 z_target 最近的層 ====

z_levels = grid.z['data']
z_index = np.abs(z_levels - z_target).argmin()
print(f"選擇切層 z_index={z_index}, 對應高度為 {z_levels[z_index]} m")


# ==== 畫 CAPPI ====
display = GridMapDisplay(grid)
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())


# ==== 設定 colormap（自訂顏色）====
from matplotlib.colors import ListedColormap
custom_colors = [
    "#1FE4F3FF",  # Rain
    "#ebff0e",  # Melting Layer
    "#2ca02c",  # Wet Snow
    "#27d638",  # Dry Snow
    "#f51010",  # Graupel（紅）
    "#3c00ff",  # Hail
]
cmap = ListedColormap(custom_colors)
field_data = grid.fields['hydro_class']['data'][z_index]

# ==== 畫主圖 ====
pm = display.plot_grid(
    field='hydro_class',
    level=z_index,
    ax=ax,
    cmap=cmap,
    vmin=0,
    vmax=5,
    colorbar_flag=False,
    colorbar_label='Hydrometeor Type',
    embellish=False,
    add_grid_lines= False
)

# ==== Title ====
ax.set_title(f"PID CAPPI @ {z_levels[z_index]/1000:.1f} km\n{time_str_LCT}", fontsize=16,fontproperties=title_font)

# ==== 加邊界 ====
shp = Reader(shapefile_path)
ax.add_geometries(shp.geometries(), crs=ccrs.PlateCarree(), facecolor='none', edgecolor='green')
x = grid.x['data'] / 1000  # km
y = grid.y['data'] / 1000
radar_lon = radar.longitude['data'][0]
radar_lat = radar.latitude['data'][0]
lon_grid = radar_lon + (x / 111) / np.cos(np.radians(radar_lat))
lat_grid = radar_lat + (y / 111)
# ==== 顯示範圍 ====
lon_min = np.min(lon_grid)
lon_max = np.max(lon_grid)
lat_min = np.min(lat_grid)
lat_max = np.max(lat_grid)
margin_lon = (lon_max - lon_min) * 0.02
margin_lat = (lat_max - lat_min) * 0.02
ax.set_extent([lon_min - margin_lon, lon_max + margin_lon,
                lat_min - margin_lat, lat_max + margin_lat])

# ==== Gridlines ====
gl = ax.gridlines(draw_labels=True)
gl.right_labels = False

# ==== 圖例設定 ====
label_names = ['Rain', 'Melting Layer', 'Wet Snow', 'Dry Snow', 'Graupel', 'Hail']
patches = [mpatches.Patch(color=cmap(i), label=label_names[i]) for i in range(6)]
plt.legend(handles=patches, fontsize=10, title_fontproperties=myfont)

import os
save_dir = f"{data_top_path}/PID_CAPPI/{year}{month}{day}"
os.makedirs(save_dir, exist_ok=True)

save_path = f"{save_dir}/{time_str}_{int(z_target/1000)}km.png"
plt.savefig(save_path, dpi=300)

plt.tight_layout()
# plt.show()
plt.close()