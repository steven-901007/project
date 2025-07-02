import pyart
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Geod
from datetime import datetime
import matplotlib.patches as mpatches

# ==== 檔案與時間設定 ====
data_top_path = "C:/Users/steve/python_data/radar"
year, month, day = '2021', '06', '12'
hh, mm, ss = '00', '16', '00'
time_str = f"{year}{month}{day}{hh}{mm}{ss}"
file_path = f"{data_top_path}/PID/{year}{month}{day}/{time_str}.nc"



# ==== 切線座標設定 ====
lon0 = 121.77
lat0 = 25.07
lon1 = 121.77
lat1 = 26.07
# 任意兩點


# ==== 中文顯示 ====
plt.rcParams['font.sans-serif'] = ['MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# ==== 讀取雷達 Grid 資料 ====
radar = pyart.io.read(file_path)
grid = pyart.map.grid_from_radars(
    radar,
    grid_shape=(21, 400, 400),
    grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
    fields=['reflectivity'],
    gridding_algo='map_gates_to_grid',
    weighting_function='Barnes',
    roi_func='dist_beam'
    # roi_func='constant',
    # constant_roi=1500
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
Z = grid.fields['reflectivity']['data']

cross_section = np.full((len(gz), len(x)), np.nan)
for i, (px, py) in enumerate(zip(x, y)):
    ix = np.argmin(np.abs(gx - px))
    iy = np.argmin(np.abs(gy - py))
    column = Z[:, iy, ix]
    if np.ma.is_masked(column):
        column = column.astype(float).filled(np.nan)
    cross_section[:, i] = column

# 畫圖
fig, ax = plt.subplots(figsize=(12, 6))
from matplotlib.colors import ListedColormap, BoundaryNorm

# 自訂 dBZ 色階（從藍到紅）
cmap_colors = [
    '#0000FF',  # 0 dBZ - 藍
    '#0099FF',  # 5
    '#00CC99',  # 10
    '#00FF00',  # 15
    '#99FF00',  # 20
    '#CCFF00',  # 25
    '#FFFF00',  # 30
    '#FFCC00',  # 35
    '#FF9900',  # 40
    '#FF6600',  # 45
    '#FF3300',  # 50
    '#FF0000',  # 55
    '#CC0000',  # 60
    '#990000',  # 65
    '#660000'   # 70
]

from matplotlib.colors import Normalize

# ==== 改用平滑 colormap 和連續 norm ====
cmap = plt.cm.turbo  # 你也可以換成 nipy_spectral、jet、viridis...
norm = Normalize(vmin=0, vmax=70)

# ==== 繪圖 ====
zz, xx = np.meshgrid(gz, np.linspace(0, dist / 1000, len(x)), indexing='ij')
masked_cross_section = np.ma.masked_invalid(cross_section)

# 加入 shading='auto' 讓顯示更細膩
pc = ax.pcolormesh(xx, zz, masked_cross_section, cmap=cmap, norm=norm, shading='auto')

# ==== 加上標題與 colorbar ====
ax.set_xlabel("距離 (km)")
ax.set_ylabel("高度 (km)")
ax.set_title(f"Reflectivity Cross-Section\n{datetime.strptime(time_str, '%Y%m%d%H%M%S').strftime('%Y/%m/%d %H:%M:%S')}")
plt.colorbar(pc, ax=ax, label='Reflectivity (dBZ)')
plt.tight_layout()
plt.show()
