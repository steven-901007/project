import pyart
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from datetime import datetime

data_top_path = "C:/Users/steve/python_data/radar"
year = '2024'
month = '05'
day = '23'
hh = '08'
mm = '02'
ss = '00'

file_path = f"{data_top_path}/{year}{month}{day}_u.RCWF/{year}{month}{day}{hh}{mm}{ss}.VOL"
shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"

plt.rcParams['font.sans-serif'] = [u'MingLiu']
plt.rcParams['axes.unicode_minus'] = False
time = file_path.split('/')[-1].split('.')[0]
time_dt = datetime.strptime(time, "%Y%m%d%H%M%S").strftime("%Y/%m/%d %H:%M:%S")

radar = pyart.io.read(file_path)
sweep_num = 1

display = pyart.graph.RadarMapDisplay(radar)
fig = plt.figure(figsize=(10, 10))
ax = plt.subplot(1, 1, 1, projection=ccrs.PlateCarree())

display.plot_ppi_map('velocity',
                     sweep=sweep_num,
                     ax=ax,
                     colorbar_label='徑向風速 ($V_{r}$) \n (m/s)',
                     title=f'velocity\n{time_dt}',
                     vmin=-30,
                     vmax=30,
                     shapefile=shapefile_path,
                     shapefile_kwargs={"facecolor": 'none', 'edgecolor': 'green'},
                     embellish=False)

ax.set_extent([119, 123.5, 21, 26.5])
plt.show()
