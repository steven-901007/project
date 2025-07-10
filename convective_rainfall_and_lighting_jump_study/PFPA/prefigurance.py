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
import sys
import numpy as np


month =  sys.argv[2] if len(sys.argv) > 1 else "05" 
year = sys.argv[1] if len(sys.argv) > 1 else '2021'

dis = 36
data_source = 'EN'#flash_data來源

import platform
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"


def check_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"資料夾 '{folder_path}' 不存在。")
        raise ValueError

def check_in_time_range(row, lj_times):
    return int(any((lj_times >= row['start time']) & (lj_times <= row['end time'])))

def fileset(path):    #建立資料夾
   
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 

#建立前估後符資料夾

fileset(f"{data_top_path}/PFPA/{data_source}_{year}{month}")

##強降雨發生但沒有lighting jump
data_path = f"{data_top_path}/rain_data/station_data/{year}_{month}.csv"
check_folder(data_path)
data = pd.read_csv(data_path)

# print(data)
check_folder(f"{data_top_path}/rain_data/CR_{dis}km/{year}/{month}")
check_folder(f"{data_top_path}/flash_data/{data_source}/lighting_jump/{data_source}_{year}{month}_{dis}km")
prefigurance_station_name_list = []#前估測站名稱
prefigurance_hit_list = []#個測站命中的list
total_prefigurance_list = []#前估總量(lighting jump and rain + non_lighting jump and rain)
prefigurance_lon_data_list = []
prefigurance_lat_data_list = []

month_path =f"{data_top_path}/rain_data/CR_{dis}km/{year}/{month}/*.csv"

result  =glob.glob(month_path)

for rain_station_path in tqdm(result,desc=f"{year}{month}資料處理中...."):
# rain_station_path = f"{data_top_path}/rain_data/對流性降雨{dis}km/{year}/{month}/C0V730.csv"
    rain_station_name = os.path.basename(rain_station_path).split('.')[0]
    # print(rain_station_name)

    #flash
    try:
        flash_station_path = f"{data_top_path}/flash_data/{data_source}/lighting_jump/{data_source}_{year}{month}_{dis}km/{rain_station_name}.csv"
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
        rain_data['start time'] = rain_data["time data"] - pd.Timedelta(minutes= 40)
        rain_data['end time'] = rain_data['time data'] + pd.Timedelta(minutes=10)
        flash_data['LJ_time'] = pd.to_datetime(flash_data['LJ_time'])

        try:
            rain_data['LJ_in_time_range'] = rain_data.apply(lambda row: check_in_time_range(row, flash_data['LJ_time']), axis=1)
        except:
            print(rain_station_name)
            print(rain_data)
            ValueError
        # print(rain_data[rain_data['LJ_in_time_range'] == 1])
        # pd.set_option('display.max_rows', None)

        # print(rain_data)
        # print(rain_data['LJ_in_time_range'].sum())

        if rain_data['LJ_in_time_range'].sum() != 0:
            prefigurance_station_name_list.append(rain_station_name)
            # print(data[data['station name'] == rain_station_name]['lon'].iloc[0])
            prefigurance_hit_list.append(rain_data['LJ_in_time_range'].sum())
            total_prefigurance_list.append(len(rain_data))
            prefigurance_lon_data_list.append(data[data['station name'] == rain_station_name]['lon'].iloc[0])
            prefigurance_lat_data_list.append(data[data['station name'] == rain_station_name]['lat'].iloc[0])
# print(rain_station_name,rain_data['LJ_in_time_range'].sum(),len(rain_data))


prefigurance_hit_persent_list = [] # 前估命中率
for i in range(len(total_prefigurance_list)):
    prefigurance_hit_persent_list.append(prefigurance_hit_list[i]/total_prefigurance_list[i]*100)


prefigurance_save_data = {
    'station name':prefigurance_station_name_list,
    'lon':prefigurance_lon_data_list,
    'lat':prefigurance_lat_data_list,
    'hit':prefigurance_hit_list,
    'total':total_prefigurance_list,
    'hit persent':prefigurance_hit_persent_list,
}
prefigurance_save_path = f"{data_top_path}/PFPA/{data_source}_{year}{month}/prefigurance.csv"
pd.DataFrame(prefigurance_save_data).to_csv(prefigurance_save_path,index=False)

##前估繪圖
# 加載台灣的行政邊界
taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"  # 你需要提供台灣邊界的shapefile文件


# 設定經緯度範圍
lon_min, lon_max = 120, 122.1
lat_min, lat_max = 21.5, 25.5

def CR_count():
    # CR事件數 colorbar（連續）
    plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)

    shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                                ccrs.PlateCarree(), edgecolor='black', facecolor='white')
    ax.add_feature(shape_feature)

    gridlines = ax.gridlines(draw_labels=True, linestyle='--')
    gridlines.top_labels = False
    gridlines.right_labels = False

    # 使用連續 colormap 設定
    cmap = plt.get_cmap('RdYlBu')
    interval = 25
    raw_max = max(prefigurance_hit_list)
    vmax = int(np.ceil(raw_max / interval)) * interval  # 向上取整
    vmin = 0
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    sc = ax.scatter(prefigurance_lon_data_list, prefigurance_lat_data_list,
                    c=total_prefigurance_list, cmap=cmap, norm=norm, s=10, zorder=5)
    cbar = plt.colorbar(sc, ax=ax)
    # cbar.set_label('CR事件數')

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    ax.set_title(f"{year}/{month}\nNumber of convective rainfall events\n flash data source:{data_source}")
    plt.savefig(f"{data_top_path}/PFPA/{data_source}_{year}{month}/PF_CR_count.png", bbox_inches='tight', dpi=300)

CR_count()

def hit_count():
    # 命中次數 colorbar（連續）
    plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)

    shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                                ccrs.PlateCarree(), edgecolor='black', facecolor='white')
    ax.add_feature(shape_feature)

    gridlines = ax.gridlines(draw_labels=True, linestyle='--')
    gridlines.top_labels = False
    gridlines.right_labels = False

    # 使用連續 colormap 設定
    cmap = plt.get_cmap('RdYlBu')
    # 自動推算 colorbar 上限（例如以 25 為階距）
    interval = 25
    raw_max = max(prefigurance_hit_list)
    vmax = int(np.ceil(raw_max / interval)) * interval  # 向上取整
    vmin = 0
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    sc = ax.scatter(prefigurance_lon_data_list, prefigurance_lat_data_list,
                    c=prefigurance_hit_list, cmap=cmap, norm=norm, s=10, zorder=5)
    cbar = plt.colorbar(sc, ax=ax)
    # cbar.set_label('Lighting Jump 命中次數')

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    ax.set_title(f"{year}/{month}\n Prefigurance max = {round(max(prefigurance_hit_list),3)}\n flash data source:{data_source}")
    plt.savefig(f"{data_top_path}/PFPA/{data_source}_{year}{month}/PF.png", bbox_inches='tight', dpi=300)

hit_count()

def hit_rate():
    # 命中率 colorbar（自動分段）
    plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)

    shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(),
                                ccrs.PlateCarree(), edgecolor='black', facecolor='white')
    ax.add_feature(shape_feature)

    gridlines = ax.gridlines(draw_labels=True, linestyle='--')
    gridlines.top_labels = False
    gridlines.right_labels = False

    # 設定 bin 與 cmap
    bin_width = 10
    levels = list(range(0, 110, bin_width))
    cmap = plt.get_cmap('rainbow', len(levels) - 1)
    norm = mcolors.BoundaryNorm(boundaries=levels, ncolors=cmap.N)

    sc = ax.scatter(prefigurance_lon_data_list, prefigurance_lat_data_list,
                    c=prefigurance_hit_persent_list, cmap=cmap, norm=norm, s=10, zorder=5)
    cbar = plt.colorbar(sc, ax=ax, ticks=levels)
    # cbar.set_label('命中率 [%]')

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    ax.set_title(f"{year}/{month}\nPrefigurance hit rate [%] max = {round(max(prefigurance_hit_persent_list),3)}\n flash data source:{data_source}")
    plt.savefig(f"{data_top_path}/PFPA/{data_source}_{year}{month}/PF_hit_rate.png", bbox_inches='tight', dpi=300)
hit_rate()

