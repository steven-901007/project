import pyart
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime
import numpy as np
# === 路徑與時間設定 ===
data_top_path = "C:/Users/steve/python_data/radar"
year, month, day = '2024', '05', '23'
hh, mm, ss = '00', '02', '00'
file_path = f"{data_top_path}/PID/{year}{month}{day}{hh}{mm}{ss}.nc"
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# === 讀資料與時間字串 ===
radar = pyart.io.read(file_path)
time_str = file_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")
radar.fields['cross_correlation_ratio']['data'] = np.ma.masked_equal(
    radar.fields['cross_correlation_ratio']['data'], -999
)
sweep_num = 2

# === 畫 RHOHV PPI ===
display = pyart.graph.RadarMapDisplay(radar)
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())


display.plot_ppi_map('cross_correlation_ratio',
                     sweep=sweep_num,
                     ax=ax,
                     colorbar_label='相關係數 ($\\rho_{HV}$)',
                     vmin=0.7,
                     vmax=1.0,
                     shapefile=shapefile_path,
                     shapefile_kwargs={"facecolor": 'none', 'edgecolor': 'green'},
                     embellish=False)

# === 自行設定 title 字體大小 ===
ax.set_title(f'cross correlation ratio PPI\n{time_dt}', fontsize=16)

ax.set_extent([119, 123.5, 21, 26.5])
gl = ax.gridlines(draw_labels=True)
gl.right_labels = False
plt.show()
