import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime
from cartopy.io.shapereader import Reader
from pyart.graph import GridMapDisplay

# ==== 基本設定 ====
data_top_path = "C:/Users/steve/python_data/radar"
year, month, day = '2024', '05', '23'
hh, mm, ss = '00', '02', '00'
time_str = f"{year}{month}{day}{hh}{mm}{ss}"
file_path = f"{data_top_path}/PID/{time_str}.nc"
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# ==== 讀雷達 ====
radar = pyart.io.read(file_path)
time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

# # ==== Grid ====
# grid = pyart.map.grid_from_radars(
#     radar,
#     grid_shape=(21, 400, 400),
#     grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
#     fields=['cross_correlation_ratio'],
#     weighting_function='nearest',
#     gridding_algo='map_gates_to_grid'
# )
grid = pyart.map.grid_from_radars(
    radar,
    grid_shape=(21, 400, 400),
    grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
    fields=['cross_correlation_ratio'],

    gridding_algo='map_gates_to_grid',
    weighting_function='Barnes',  # 或 'Cressman'

    roi_func='constant',          # 固定半徑函數
    # constant_roi=500             # 搜尋半徑
)
z_index = np.abs(grid.z['data'] - 2000).argmin()

# ==== 畫圖 ====
display = GridMapDisplay(grid)
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

display.plot_grid(
    field='cross_correlation_ratio',
    level=z_index,
    ax=ax,
    vmin=0.7,
    vmax=1.0,
    colorbar_label='RHOHV',
    embellish=False
)
ax.set_title(f"RHOHV CAPPI@ 2.0 km\n{time_dt}", fontsize=16)
shp = Reader(shapefile_path)
ax.add_geometries(shp.geometries(), crs=ccrs.PlateCarree(), facecolor='none', edgecolor='red')
center_lon = radar.longitude['data'][0]
center_lat = radar.latitude['data'][0]
ax.set_extent([center_lon - 1.5, center_lon + 1.5, center_lat - 1.5, center_lat + 1.5])
plt.tight_layout()
plt.show()