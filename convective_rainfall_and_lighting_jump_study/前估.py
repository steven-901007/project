##前估
from openpyxl import load_workbook
import glob
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib as mpl
import os



year = '2021' #年分
month = '06' #月份
dis = 36
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"

def check_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"資料夾 '{folder_path}' 不存在。")
        raise ValueError

def check_in_time_range(row, lj_times):
    return int(any((lj_times >= row['start time']) & (lj_times <= row['end time'])))

def fileset(path):    #建立資料夾
    import os
    
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 

#建立前估後符資料夾
fileset(f"{data_top_path}/前估後符")

##強降雨發生但沒有lighting jump
data_path = f"{data_top_path}/雨量資料/測站資料/{year}_{month}.csv"
check_folder(data_path)
data = pd.read_csv(data_path)

# print(data)
check_folder(f"{data_top_path}/雨量資料/對流性降雨{dis}km/{year}/{month}")
check_folder(f"{data_top_path}/閃電資料/lighting_jump/{year}_{month}_{dis}km")
prefigurance_station_name_list = []#前估測站名稱
prefigurance_hit_list = []#個測站命中的list
total_prefigurance_list = []#前估總量(lighting jump and rain + non_lighting jump and rain)
prefigurance_lon_data_list = []
prefigurance_lat_data_list = []

month_path =f"{data_top_path}/雨量資料/對流性降雨{dis}km/{year}/{month}/*.csv"

result  =glob.glob(month_path)

for rain_station_path in tqdm(result,desc='資料處理中....'):
# rain_station_path = f"{data_top_path}/雨量資料/對流性降雨{dis}km/{year}/{month}/C0V730.csv"
    rain_station_name = rain_station_path.split('/')[-1].split('\\')[-1].split('.')[0]
    # print(rain_station_name)

    #flash
    try:
        flash_station_path = f"{data_top_path}/閃電資料/lighting_jump/{year}_{month}_{dis}km/{rain_station_name}.csv"
        rain_data = pd.read_csv(rain_station_path)
        flash_data = pd.read_csv(flash_station_path)
        # print(rain_station_name)
    except:
        flash_station_path = None
        # print(rain_station_name)

    if flash_station_path != None:
        # print(rain_data)
        # print(flash_data)
        #end time< lighting jump <= time data
        rain_data['time data'] = pd.to_datetime(rain_data['time data'])
        rain_data['start time'] = rain_data["time data"] - pd.Timedelta(minutes= 50)
        rain_data['end time'] = rain_data['time data'] + pd.Timedelta(minutes=10)
        flash_data['LJ_time'] = pd.to_datetime(flash_data['LJ_time'])

        try:
            rain_data['LJ_in_time_range'] = rain_data.apply(lambda row: check_in_time_range(row, flash_data['LJ_time']), axis=1)
        except:
            print(rain_station_name)
            print(rain_data)
            ValueError
        # print(rain_data[rain_data['LJ_in_time_range'] == 1])
        pd.set_option('display.max_rows', None)

        # print(rain_data)
        # print(rain_data['LJ_in_time_range'].sum())

        if rain_data['LJ_in_time_range'].sum() != 0:
            prefigurance_station_name_list.append(rain_station_name)
            # print(data[data['station name'] == rain_station_name]['lon'].iloc[0])
            prefigurance_hit_list.append(rain_data['LJ_in_time_range'].sum())
            total_prefigurance_list.append(len(rain_data))
            prefigurance_lon_data_list.append(data[data['station name'] == rain_station_name]['lon'].iloc[0])
            prefigurance_lat_data_list.append(data[data['station name'] == rain_station_name]['lat'].iloc[0])
print(rain_station_name,rain_data['LJ_in_time_range'].sum(),len(rain_data))


prefigurance_hit_persent_list = [] # 前估命中率
for i in range(len(total_prefigurance_list)):
    prefigurance_hit_persent_list.append(prefigurance_hit_list[i]/total_prefigurance_list[i]*100)

# print(prefigurance_station_name_list)
# print(prefigurance_hit_list)
# print(total_prefigurance_list)
# print(prefigurance_lon_data_list)
# print(prefigurance_lat_data_list)
# print(prefigurance_hit_persent_list)
prefigurance_save_data = {
    'station name':prefigurance_station_name_list,
    'lon':prefigurance_lon_data_list,
    'lat':prefigurance_lat_data_list,
    'hit':prefigurance_hit_list,
    'total':total_prefigurance_list,
    'hit persent':prefigurance_hit_persent_list,
}
prefigurance_save_path = f"{data_top_path}/前估後符/前估.csv"
pd.DataFrame(prefigurance_save_data).to_csv(prefigurance_save_path,index=False)

##前估繪圖

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
taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"  # 你需要提供台灣邊界的shapefile文件
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='white')
ax.add_feature(shape_feature)


# 加入經緯度格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False

## 計算某個地方達到10mm/10min的次數 + colorbar
color_list = []

level = [0,10,25,50,75,120,150,170,210]
color_box = ['silver','purple','darkviolet','blue','g','y','orange','r']

for nb in prefigurance_hit_list:
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
ax.scatter(prefigurance_lon_data_list, prefigurance_lat_data_list, color=color_list, s=3, zorder=5)

# colorbar setting

nlevel = len(level)
cmap1 = mpl.colors.ListedColormap(color_box, N=nlevel)
cmap1.set_over('fuchsia')
cmap1.set_under('black')
norm1 = mcolors.Normalize(vmin=min(level), vmax=max(level))
norm1 = mcolors.BoundaryNorm(level, nlevel, extend='max')
im = cm.ScalarMappable(norm=norm1, cmap=cmap1)
cbar1 = plt.colorbar(im,ax=ax, extend='neither', ticks=level)


# 加入標籤
plt.xlabel('Longitude')
plt.ylabel('Latitude')

ax.set_title(f"{year}年{month}月\n前估 max = {round(max(prefigurance_hit_list),3)}")


## 這是用來確認colorbar的配置
fig,ax1 = plt.subplots()
X = [i for i in range(len(prefigurance_hit_list))]
Y = sorted(prefigurance_hit_list)
ax1.plot(X,Y,color =  'black',marker = "*",linestyle = '--') #折線圖
ax1.set_title('這是用來確認colorbar的配置')



##前估命中率繪圖

plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_xlim(lon_min, lon_max)
ax.set_ylim(lat_min, lat_max)

plt.rcParams['font.sans-serif'] = [u'MingLiu']  # 設定字體為'細明體'
plt.rcParams['axes.unicode_minus'] = False  # 用來正常顯示正負號

# 加載台灣的行政邊界
taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"  # 你需要提供台灣邊界的shapefile文件
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                               ccrs.PlateCarree(), edgecolor='black', facecolor='white')
ax.add_feature(shape_feature)


# 加入經緯度格線
gridlines = ax.gridlines(draw_labels=True, linestyle='--')
gridlines.top_labels = False
gridlines.right_labels = False

## 計算某個地方達到10mm/10min的次數 + colorbar
color_list = []

level = [0,10,20,30,40,50,60,70,80]
color_box = ['silver','purple','darkviolet','blue','g','y','orange','r']

for nb in prefigurance_hit_persent_list:
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
ax.scatter(prefigurance_lon_data_list, prefigurance_lat_data_list, color=color_list, s=3, zorder=5)

# colorbar setting

nlevel = len(level)
cmap1 = mpl.colors.ListedColormap(color_box, N=nlevel)
cmap1.set_over('fuchsia')
cmap1.set_under('black')
norm1 = mcolors.Normalize(vmin=min(level), vmax=max(level))
norm1 = mcolors.BoundaryNorm(level, nlevel, extend='max')
im = cm.ScalarMappable(norm=norm1, cmap=cmap1)
cbar1 = plt.colorbar(im,ax=ax, extend='neither', ticks=level)


# 加入標籤
plt.xlabel('Longitude')
plt.ylabel('Latitude')

ax.set_title(f"{year}年{month}月\n前估命中率 [%] max = {round(max(prefigurance_hit_persent_list),3)}")


## 這是用來確認colorbar的配置
fig,ax1 = plt.subplots()
X = [i for i in range(len(prefigurance_hit_persent_list))]
Y = sorted(prefigurance_hit_persent_list)
ax1.plot(X,Y,color =  'black',marker = "*",linestyle = '--') #折線圖
ax1.set_title('這是用來確認colorbar的配置')


# 顯示地圖
plt.show()