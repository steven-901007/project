import pyart
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Geod
from datetime import datetime
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap

# ==== 檔案與時間設定 ====
data_top_path = "C:/Users/steve/python_data/radar"
year, month, day = '2024', '05', '23'
hh, mm, ss = '00', '02', '00'
time_str = f"{year}{month}{day}{hh}{mm}{ss}"
file_path = f"{data_top_path}/PID/{time_str}.nc"

# ==== 切線座標設定 ====
lon0 = 122.08
lat0 = 26.39
lon1 = 121.53
lat1 = 25.93

# ==== 中文顯示 ====
plt.rcParams['font.sans-serif'] = ['MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# ==== 讀取雷達 Grid 資料 ====
radar = pyart.io.read(file_path)
grid = pyart.map.grid_from_radars(
    radar,
    grid_shape=(21, 400, 400),
    grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
    fields=['hydro_class'],
    gridding_algo='map_gates_to_grid',
    weighting_function='Barnes',
    roi_func='constant',
    constant_roi=1500
)

# ==== 地理→雷達座標轉換 ====
geod = Geod(ellps='WGS84')
az12, _, dist = geod.inv(lon0, lat0, lon1, lat1)
npoints = 300
distances = np.linspace(0, dist, npoints)
lons, lats, _ = geod.fwd(np.full(npoints, lon0), np.full(npoints, lat0), np.full(npoints, az12), distances)

radar_lon = radar.longitude['data'][0]
radar_lat = radar.latitude['data'][0]
azs, _, dists = geod.inv(np.full(npoints, radar_lon), np.full(npoints, radar_lat), lons, lats)
x = dists * np.sin(np.radians(azs)) / 1000  # km
y = dists * np.cos(np.radians(azs)) / 1000  # km

# ==== 擷取 Grid 資料 ====
gx = grid.x['data'] / 1000
gy = grid.y['data'] / 1000
gz = grid.z['data'] / 1000
hydro = grid.fields['hydro_class']['data']

cross_section = np.full((len(gz), len(x)), np.nan)
for i, (px, py) in enumerate(zip(x, y)):
    ix = np.argmin(np.abs(gx - px))
    iy = np.argmin(np.abs(gy - py))
    column = hydro[:, iy, ix]
    if np.ma.is_masked(column):
        column = column.astype(float).filled(np.nan)
    cross_section[:, i] = column

# ==== 畫圖 ====
fig, ax = plt.subplots(figsize=(12, 6))

# 自訂 colormap（紅色給 Graupel）
custom_colors = [
    "#1f77b4",  # Rain
    "#ff7f0e",  # Melting Layer
    "#2ca02c",  # Wet Snow
    "#27c2d6",  # Dry Snow
    "#f51010",  # Graupel（紅）
    "#9467bd",  # Hail
]
cmap = ListedColormap(custom_colors)

# 畫 pcolormesh
zz, xx = np.meshgrid(gz, np.linspace(0, dist / 1000, len(x)), indexing='ij')
masked_cross_section = np.ma.masked_invalid(cross_section)
pc = ax.pcolormesh(xx, zz, masked_cross_section, cmap=cmap, vmin=0, vmax=5, shading='auto')

# 標籤與標題
ax.set_xlabel("距離 (km)")
ax.set_ylabel("高度 (km)")
ax.set_title(f"Hydrometeor Cross-Section\n{datetime.strptime(time_str, '%Y%m%d%H%M%S').strftime('%Y/%m/%d %H:%M:%S')}")

# 圖例
label_names = ['Rain', 'Melting Layer', 'Wet Snow', 'Dry Snow', 'Graupel', 'Hail']
patches = [mpatches.Patch(color=cmap(i), label=label_names[i]) for i in range(6)]
ax.legend(handles=patches, loc='upper right', title='Hydrometeors')

plt.tight_layout()
plt.show()
