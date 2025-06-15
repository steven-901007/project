import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime
from cartopy.io.shapereader import Reader
from pyart.graph import GridMapDisplay
# import pyart.graph.cm

# ==== 時間與路徑設定 ====
data_top_path = "C:/Users/steve/python_data/radar"
year, month, day = '2024', '05', '23'
hh, mm, ss = '00', '02', '00'
time_str = f"{year}{month}{day}{hh}{mm}{ss}"
file_path = f"{data_top_path}/PID/{time_str}.nc"
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

# ==== 中文顯示設定 ====
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# ==== 讀取雷達資料 ====
radar = pyart.io.read(file_path)
time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

# ==== 製作 Grid ====
grid = pyart.map.grid_from_radars(
    radar,
    grid_shape=(41, 400, 400),
    grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
    fields=['reflectivity'],
    weighting_function='nearest',
    gridding_algo='map_gates_to_grid'
)

# ==== 找出距離 z_target 最近的層 ====
z_target = 2000
z_levels = grid.z['data']
z_index = np.abs(z_levels - z_target).argmin()
print(f"選擇切層 z_index={z_index}, 對應高度為 {z_levels[z_index]} m")

# ==== 畫 CAPPI ====
display = GridMapDisplay(grid)
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

display.plot_grid(
    field='reflectivity',
    level=z_index,
    ax=ax,
    # cmap=pyart.graph.cm.NWSRef,
    vmin=0,
    vmax=70,
    colorbar_label='Reflectivity (dBZ)',
    embellish=False
)

# === 自行設定 title 字體大小 ===
ax.set_title(f"reflectivity CAPPI@ {z_levels[z_index]/1000:.1f} km\n{time_dt}", fontsize=16)

# 加上台灣縣市邊界
shp = Reader(shapefile_path)
ax.add_geometries(
    shp.geometries(),
    crs=ccrs.PlateCarree(),
    facecolor='none',
    edgecolor='red'
)

# 設定顯示範圍
center_lon = radar.longitude['data'][0]
center_lat = radar.latitude['data'][0]
ax.set_extent([center_lon - 1.5, center_lon + 1.5, center_lat - 1.5, center_lat + 1.5])

plt.tight_layout()
plt.show()
