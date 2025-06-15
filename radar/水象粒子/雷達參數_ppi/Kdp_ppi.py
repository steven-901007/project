import pyart
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime
import numpy as np
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import FixedLocator

# === 路徑與時間設定 ===
data_top_path = "C:/Users/steve/python_data/radar"
year, month, day = '2024', '05', '23'
hh, mm, ss = '00', '02', '00'
file_path = f"{data_top_path}/PID/{year}{month}{day}{hh}{mm}{ss}.nc"
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# === 讀取雷達資料與時間字串 ===
radar = pyart.io.read(file_path)
time_str = file_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")
sweep_num = 2

# === 設定 colorbar 階層 ===
boundaries = [0, 0.1, 0.5, 1, 10]  # 最後一格包含 >1 的值
norm = BoundaryNorm(boundaries, ncolors=len(boundaries) - 1)
ticks = boundaries[:-1] + [">1"]

# === 繪圖 ===
display = pyart.graph.RadarMapDisplay(radar)
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

# 使用指定色階（例如 jet，你可再指定）
cmap = plt.get_cmap("turbo", len(boundaries) - 1)

# 繪圖
display.plot_ppi_map(
    'kdp_maesaka',
    sweep=sweep_num,
    ax=ax,
    cmap=cmap,
    norm=norm,
    colorbar_label='KDP (deg/km)',  # 讓它自己產生 colorbar
    shapefile=shapefile_path,
    shapefile_kwargs={"facecolor": 'none', 'edgecolor': 'green'},
    embellish=False
)

# === 自行設定 title 字體大小 ===
ax.set_title(f'KDP PPI\n{time_dt}', fontsize=16)

# # 加 colorbar
# cbar = plt.colorbar(pm, ax=ax, orientation='vertical', pad=0.02, shrink=0.9)
# cbar.set_label('KDP (deg/km)', fontsize=12)

# 自訂 colorbar 刻度標籤
tick_values = boundaries
tick_labels = ['0', '0.1', '0.5', '1', '>1']
# cbar.set_ticks(boundaries)
# cbar.set_ticklabels(tick_labels)

# 地圖格線
ax.set_extent([119, 123.5, 21, 26.5])
gl = ax.gridlines(draw_labels=True)
gl.right_labels = False

plt.tight_layout()
plt.show()
