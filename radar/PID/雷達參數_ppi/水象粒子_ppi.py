import pyart
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
from datetime import datetime
import numpy as np
## === 路徑與時間設定 ===
data_top_path = "C:/Users/steve/python_data/radar"
year, month, day = '2024', '05', '23'
hh, mm, ss = '00', '02', '00'
file_path = f"{data_top_path}/PID/{year}{month}{day}{hh}{mm}{ss}.nc"
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
sweep_num = 2


## === 字體設定（MingLiu 為例）===
plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False

## === 讀資料與時間處理 ===
radar = pyart.io.read(file_path)
time_str = file_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")
  

## === 畫 hydro_class 圖 ===
display = pyart.graph.RadarMapDisplay(radar)
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

cmap = plt.cm.get_cmap("tab10", 6)

pm = display.plot_ppi_map(
    'hydro_class',
    sweep=sweep_num,
    ax=ax,
    vmin=0,
    vmax=5,
    cmap=cmap,
    colorbar_flag=False,
    colorbar_label='Hydrometeor Type',
    shapefile=shapefile_path,
    shapefile_kwargs={"facecolor": 'none', 'edgecolor': 'green'},
    embellish=False
)

# === 自行設定 title 字體大小 ===
ax.set_title(f"水象粒子 PPI\n{time_dt}", fontsize=16)

ax.set_extent([119, 123.5, 21, 26.5])
gl = ax.gridlines(draw_labels=True)
gl.right_labels = False

## === 圖例設定 ===
label_names = ['Rain', 'Melting Layer', 'Wet Snow', 'Dry Snow', 'Graupel', 'Hail']
patches = [mpatches.Patch(color=cmap(i), label=label_names[i]) for i in range(6)]
plt.legend(handles=patches, loc='lower left', fontsize=10, title='Hydrometeors')

plt.tight_layout()
plt.show()
