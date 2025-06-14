import pyart
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime
from cartopy.io.shapereader import Reader
from pyart.graph import RadarMapDisplay
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

# ==== 時間與路徑設定 ====
data_top_path = "C:/Users/steve/python_data/radar"
year, month, day = '2024', '05', '23'
hh, mm, ss = '00', '02', '00'
sweep_num = 2  # 第幾層掃描角
time_str = f"{year}{month}{day}{hh}{mm}{ss}"
file_path = f"{data_top_path}/PID/{time_str}.nc"
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

# ==== 中文顯示設定 ====
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# ==== 讀取雷達資料 ====
radar = pyart.io.read(file_path)
time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

# ==== 畫 PPI：KDP ====
display = RadarMapDisplay(radar)
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

display.plot_ppi_map(
    'kdp_maesaka',
    sweep=sweep_num,
    ax=ax,
    vmin=-2,
    vmax=6,
    cmap='plasma',
    title=f"KDP PPI\n{time_dt}",
    colorbar_label='KDP (°/km)',
    embellish=False,

)

# 加上台灣縣市界線
shp = Reader(shapefile_path)
ax.add_geometries(
    shp.geometries(),
    crs=ccrs.PlateCarree(),
    facecolor='none',
    edgecolor='red'
)

# 設定範圍（以雷達為中心 ±1.5 度）
center_lon = radar.longitude['data'][0]
center_lat = radar.latitude['data'][0]
ax.set_extent([center_lon - 1.5, center_lon + 1.5, center_lat - 1.5, center_lat + 1.5])

# 加經緯線
gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
gl.top_labels = False
gl.right_labels = False
gl.xformatter = LongitudeFormatter()
gl.yformatter = LatitudeFormatter()

plt.tight_layout()
plt.show()
