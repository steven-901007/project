import pyart
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime

data_top_path = "C:/Users/steve/python_data/radar"
year = '2024'
month = '05'
day = '23'
hh = '00'
mm = '02'
ss = '00'

file_path = f"{data_top_path}/{year}{month}{day}_u.RCWF/{year}{month}{day}{hh}{mm}{ss}.VOL"
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False
time = file_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

radar = pyart.io.read(file_path)
sweep_num = 2


display = pyart.graph.RadarMapDisplay(radar)
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

display.plot_ppi_map('cross_correlation_ratio',
                     sweep=sweep_num,
                     ax=ax,
                     colorbar_label='相關係數 ($\\rho_{HV}$)',
                     title=f'cross correlation ratio\n{time_dt}',
                     vmin=0.7,
                     vmax=1.0,
                     shapefile=shapefile_path,
                     shapefile_kwargs={"facecolor": 'none', 'edgecolor': 'green'},
                     embellish=False)

ax.set_extent([119, 123.5, 21, 26.5])
gl = ax.gridlines(draw_labels=True)
gl.right_labels = False
plt.show()
