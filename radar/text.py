import pyart
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
from datetime import datetime

# === 雷達資料設定 ===
data_top_path = "C:/Users/steve/python_data/radar"
year, month, day = '2024', '05', '23'
hh, mm, ss = '08', '02', '00'
file_path = f"{data_top_path}/{year}{month}{day}_u.RCWF/{year}{month}{day}{hh}{mm}{ss}.VOL"
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

# === 讀資料 & 基本資訊 ===
radar = pyart.io.read(file_path)
sweep_num = 0
time = file_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

# === 抽取欄位 & 建立冰雹 mask ===
Z = radar.fields['reflectivity']['data']
ZDR = radar.fields['differential_reflectivity']['data']
RHOHV = radar.fields['cross_correlation_ratio']['data']
hail_mask = (Z > 50) & (ZDR < 0.5) & (RHOHV < 0.9)

hail_mask = hail_mask[sweep_num]

# === 對應經緯度位置 ===
x, y, _ = radar.get_gate_x_y_z(sweep=sweep_num)
x = x[sweep_num] / 1000
y = y[sweep_num] / 1000
lon = x / 111 + radar.longitude['data'][0]
lat = y / 111 + radar.latitude['data'][0]


plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# === 畫圖 ===
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())
display = pyart.graph.RadarMapDisplay(radar)

display.plot_ppi_map(
    'reflectivity',
    sweep=sweep_num,
    ax=ax,
    colorbar_label='Reflectivity (dBZ)',
    title=f'可能冰雹區域\n{time_dt}',
    vmin=0,
    vmax=70,
    shapefile=shapefile_path,
    shapefile_kwargs={"facecolor": 'none', 'edgecolor': 'green'},
    embellish=False
)

# 疊加紅點：標出冰雹區
ax.scatter(lon[hail_mask], lat[hail_mask], color='red', s=5, label='可能冰雹區')
ax.legend(loc='lower left')
ax.set_extent([119, 123.5, 21, 26.5])
plt.show()
