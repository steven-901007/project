import glob
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib as mpl
from tqdm import tqdm
import pandas as pd
import os

year = '2021' #年分
month = '06' #月份
dis = 36
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"



## 讀取雨量站經緯度資料
def rain_station_location_data_to_list(data_top_path,year):## 讀取雨量站經緯度資料
    import pandas as pd
    data_path = f"{data_top_path}/雨量資料/{year}測站資料.csv"
    data = pd.read_csv(data_path)
    station_data_name = data['station name'].to_list()
    # station_real_data_name = data['station real name'].to_list()
    lon_data = data['lon'].to_list()
    lat_data = data['lat'].to_list()
    # print(data)
    return station_data_name,lon_data,lat_data

name_data_list,lon_data_list, lat_data_list = rain_station_location_data_to_list(data_top_path,year)

lj_count_lon_lat_list = [[],[],[]]

##lighting jump count
lighting_jump_paths = f"{data_top_path}/閃電資料/lighting_jump/{dis}km/{year}/{month}/**.csv"
result = glob.glob(lighting_jump_paths)
for lighting_jump_path in tqdm(result):
    # print(lighting_jump_path)
    station_name = os.path.basename(lighting_jump_path).split('.')[0]
    # print(station_name)
    data = pd.read_csv(lighting_jump_path)
    # print(data['LJ_time'].count())
    lj_count_lon_lat_list[0].append(data['LJ_time'].count())
    lj_count_lon_lat_list[1].append(lon_data_list[name_data_list.index(station_name)])
    lj_count_lon_lat_list[2].append(lat_data_list[name_data_list.index(station_name)])
    

## 繪圖

# 設定經緯度範圍
lon_min, lon_max = 120, 122.1
lat_min, lat_max = 21.5, 25.5

plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)

plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號

# 加載台灣的行政邊界
taiwan_shapefile = data_top_path+"/研究所/Taiwan_map_data/COUNTY_MOI_1090820.shp"  # 你需要提供台灣邊界的shapefile文件
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='white')
ax.add_feature(shape_feature)


# 加入經緯度格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False

## 計算某個地方達到10mm/10min的次數 + colorbar
color_list = []

level = [0,10,20,50,100,150,200,250,310]
color_box = ['silver','purple','darkviolet','blue','g','y','orange','r']

for nb in lj_count_lon_lat_list[0]:
    more_then_maxma_or_not = 0
    for j in range(len(level)-1):
        if level[j]<nb<=level[j+1]:
            color_list.append(color_box[j])
            more_then_maxma_or_not = 1
            break
    if more_then_maxma_or_not == 0:
        color_list.append('lime')
        # print(nb)
# print(len(color_list))


# 標記經緯度點
ax.scatter(lj_count_lon_lat_list[1], lj_count_lon_lat_list[2], color=color_list, s=3, zorder=5)

# colorbar setting

nlevel = len(level)
cmap1 = mpl.colors.ListedColormap(color_box, N=nlevel)
cmap1.set_over('fuchsia')
cmap1.set_under('black')
norm1 = mcolors.Normalize(vmin=min(level), vmax=max(level))
norm1 = mcolors.BoundaryNorm(level, nlevel, extend='max')
im = cm.ScalarMappable(norm=norm1, cmap=cmap1)
cbar1 = plt.colorbar(im, extend='neither', ticks=level)


# 加入標籤
plt.xlabel('Longitude')
plt.ylabel('Latitude')

ax.set_title(year+"年"+month+"月"+'\nlighting jump count\nmax = '+ str(max(lj_count_lon_lat_list[0])))


## 這是用來確認colorbar的配置
fig,ax1 = plt.subplots()
X = [i for i in range(len(lj_count_lon_lat_list[0]))]
Y = sorted(lj_count_lon_lat_list[0])
ax1.plot(X,Y,color =  'black',marker = "*",linestyle = '--') #折線圖
ax1.set_title('這是用來確認colorbar的配置')


# 顯示地圖
plt.show()


