import pyart
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime
import numpy.ma as ma

# === 路徑與時間設定 ===
data_top_path = "C:/Users/steve/python_data/radar"
year = '2021'
month = '11'
day = '26'
hh = '07'
mm = '36'
ss = '00'

file_path = f"{data_top_path}/PID/{year}{month}{day}/{year}{month}{day}{hh}{mm}{ss}.nc"
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

# === 中文顯示設定 ===
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False

# === 時間字串轉換 ===
time = file_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

# === 讀取雷達資料 ===
radar = pyart.io.read(file_path)
sweep_num = 4  # 可依需求修改

# === 讀取反射率與 rhohv 資料並設遮罩 ===
ref_data = radar.fields['reflectivity']['data']
rhohv_data = radar.fields['cross_correlation_ratio']['data']

# 設定遮罩條件：反射率 < 0 或 rhohv < 0.8 的部分遮掉
mask = (ref_data < 0) | (rhohv_data < 0.8)
ref_data = ma.masked_where(mask, ref_data)

# 更新回雷達物件
radar.fields['reflectivity']['data'] = ref_data

# === 畫 PPI 圖 ===
display = pyart.graph.RadarMapDisplay(radar)
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

display.plot_ppi_map(
    'reflectivity',
    sweep=sweep_num,
    ax=ax,
    colorbar_label='雷達迴波 ($Z_{e}$) \n (dBZ)',
    vmin=-10,
    vmax=60,
    shapefile=shapefile_path,
    shapefile_kwargs={"facecolor": 'none', 'edgecolor': 'green'},
    embellish=False
)

# === 自行設定 title 字體大小 ===
ax.set_title(f'reflectivity PPI\n{time_dt}', fontsize=16)

# 顯示範圍與格線
ax.set_extent([119, 123.5, 21, 26.5])
gl = ax.gridlines(draw_labels=True)
gl.right_labels = False

plt.show()
