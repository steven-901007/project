##新後符
import glob
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib as mpl
import os
import sys
import pandas as pd
import numpy as np


month =  sys.argv[2] if len(sys.argv) > 1 else "05" 
year = sys.argv[1] if len(sys.argv) > 1 else '2024'

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
    
def check_in_time_range(row, rain_times):
    return int(any((rain_times >= row['start time']) & (rain_times <= row['end time'])))

def fileset(path):    #建立資料夾
    import os
    
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 

#建立前估後符資料夾
fileset(f"{data_top_path}/PFPA/{data_source}_{year}{month}")

##有lighting jump但沒強降雨發生
data_path = f"{data_top_path}/rain_data/station_data/{year}_{month}.csv"
check_folder(data_path)
data = pd.read_csv(data_path)


# print(data)
check_folder(f"{data_top_path}/rain_data/CR_{dis}km/{year}/{month}")
check_folder(f"{data_top_path}/flash_data/{data_source}/lighting_jump/{data_source}_{year}{month}_{dis}km")
post_agreement_station_name_list = []#後符測站名稱
post_agreement_hit_list = []#個測站後符命中的list
total_post_agreement_list = []#後符總量(lighting jump and rain + lighting jump and non_rain)
post_agreement_lon_data_list = []
post_agreement_lat_data_list = []

month_path = f"{data_top_path}/flash_data/{data_source}/lighting_jump/{data_source}_{year}{month}_{dis}km/*.csv"
result  =glob.glob(month_path)

for flash_station_path in tqdm(result,desc=f"{year}{month}資料處理中...."):
    # print(flash_station_path)
# flash_station_path = "C:/Users/steve/python_data/研究所/flash_data/lighting_jump/36km/2021/06/00H710.csv"
    flash_station_name = os.path.basename(flash_station_path).split('.')[0]
    # print(flash_station_name)

    #rain
    try:
        rain_station_path = f"{data_top_path}/rain_data/CR_{dis}km/{year}/{month}/{flash_station_name}.csv"
        rain_data = pd.read_csv(rain_station_path)
        flash_data = pd.read_csv(flash_station_path)
        # print(rain_station_path)
    except:
        rain_station_path = None
        # print(rain_station_path)

    if rain_station_path != None:
        # print(rain_data)
        # print(flash_data)
        #end time< lighting jump <= time data
        flash_data['LJ_time'] = pd.to_datetime(flash_data['LJ_time'])
        flash_data['start time'] = flash_data["LJ_time"]
        #  - pd.Timedelta(minutes= 40)
        flash_data['end time'] = flash_data['LJ_time'] + pd.Timedelta(minutes=50)
        rain_data['time data'] = pd.to_datetime(rain_data['time data'])
        # print(rain_data)
        # print(flash_data)


        try:
            flash_data['convective_rainfall_in_time_range'] = flash_data.apply(lambda row: check_in_time_range(row, rain_data['time data']), axis=1)
        except:
            print(flash_station_name)
            print(flash_data)
            ValueError
        # print(flash_data[flash_data['convective_rainfall_in_time_range'] == 1])
        # pd.set_option('display.max_rows', None)

        # print(rain_data)
        # print(flash_data['convective_rainfall_in_time_range'].sum())
        # print(flash_data)
        if flash_data['convective_rainfall_in_time_range'].sum() != 0:
            post_agreement_station_name_list.append(flash_station_name)
            # print(data[data['station name'] == rain_station_name]['lon'].iloc[0])
            post_agreement_hit_list.append(flash_data['convective_rainfall_in_time_range'].sum())
            total_post_agreement_list.append(len(flash_data))
            post_agreement_lon_data_list.append(data[data['station name'] == flash_station_name]['lon'].iloc[0])
            post_agreement_lat_data_list.append(data[data['station name'] == flash_station_name]['lat'].iloc[0])
    # print(flash_station_name,flash_data['convective_rainfall_in_time_range'].sum(),len(flash_data))
# print(post_agreement_station_name_list)
# print(post_agreement_hit_list)
# print(total_post_agreement_list)

post_agreement_hit_persent_list = [] # 後符命中率
for i in range(len(total_post_agreement_list)):
    post_agreement_hit_persent_list.append(post_agreement_hit_list[i]/(total_post_agreement_list[i])*100)

post_agreement_save_data = {
    'station name':post_agreement_station_name_list,
    'lon':post_agreement_lon_data_list,
    'lat':post_agreement_lat_data_list,
    'hit':post_agreement_hit_list,
    'total':total_post_agreement_list,
    'hit persent':post_agreement_hit_persent_list,
}
post_agreement_save_path = f"{data_top_path}/PFPA/{data_source}_{year}{month}/post_agreement.csv"
pd.DataFrame(post_agreement_save_data).to_csv(post_agreement_save_path,index=False)


##後符繪圖

# 設定經緯度範圍
lon_min, lon_max = 120, 122.1
lat_min, lat_max = 21.5, 25.5
taiwan_shapefile = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
shape_feature = ShapelyFeature(Reader(taiwan_shapefile).geometries(), ccrs.PlateCarree(),
                                   edgecolor='black',facecolor="#0362025C")

#設定中文字體
from matplotlib.font_manager import FontProperties
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)  
plt.rcParams['axes.unicode_minus'] = False

def LJ_count():
    plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)

    # 加載台灣邊界
    ax.add_feature(shape_feature)

    # 經緯度格線
    gridlines = ax.gridlines(draw_labels=True, linestyle='--')
    gridlines.top_labels = False
    gridlines.right_labels = False

    # 使用連續 colormap 設定
    cmap = plt.get_cmap('RdYlBu')
    interval = 25
    raw_max = max(total_post_agreement_list)
    vmax = int(np.ceil(raw_max / interval)) * interval  # 向上取整
    vmin = 0
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    sc = ax.scatter(post_agreement_lon_data_list, post_agreement_lat_data_list,
                    c=total_post_agreement_list, cmap=cmap, norm=norm, s=10, zorder=5)

    plt.colorbar(sc, ax=ax, ticks=np.linspace(vmin, vmax, int((vmax - vmin) / interval) + 1))
    # cbar.set_label("LJ事件數")

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # 標題與儲存
    ax.set_title(f"{year}/{month}\nLJ個案數 max = {round(max(total_post_agreement_list), 3)}\nflash data source: {data_source}", fontproperties=myfont)
    plt.savefig(f"{data_top_path}/PFPA/{data_source}_{year}{month}/PA_LJ_count.png", bbox_inches='tight', dpi=300)


LJ_count()

def hit_count():
    plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    ax.add_feature(shape_feature)

    gridlines = ax.gridlines(draw_labels=True, linestyle='--')
    gridlines.top_labels = False
    gridlines.right_labels = False

    cmap = plt.get_cmap('RdYlBu')
    interval = 25
    raw_max = max(post_agreement_hit_list)
    vmax = int(np.ceil(raw_max / interval)) * interval
    vmin = 0
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    sc = ax.scatter(post_agreement_lon_data_list, post_agreement_lat_data_list,
                    c=post_agreement_hit_list, cmap=cmap, norm=norm, s=10, zorder=5)
    plt.colorbar(sc, ax=ax, ticks=np.linspace(vmin, vmax, int((vmax - vmin) / interval) + 1))
    # cbar.set_label("命中次數")

    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    ax.set_title(f"{year}/{month}\n 後符命中數 max = {round(raw_max,3)}\nflash data source: {data_source}", fontproperties=myfont)
    plt.savefig(f"{data_top_path}/PFPA/{data_source}_{year}{month}/PA.png", bbox_inches='tight', dpi=300)

hit_count()

def hit_rate():
    plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    ax.add_feature(shape_feature)

    gridlines = ax.gridlines(draw_labels=True, linestyle='--')
    gridlines.top_labels = False
    gridlines.right_labels = False

    # 設定 bin 與 cmap
    bin_width = 10
    levels = list(range(0, 110, bin_width))
    cmap = plt.get_cmap('rainbow', len(levels) - 1)
    norm = mcolors.BoundaryNorm(boundaries=levels, ncolors=cmap.N)

    sc = ax.scatter(post_agreement_lon_data_list, post_agreement_lat_data_list,
                    c=post_agreement_hit_persent_list, cmap=cmap, norm=norm, s=10, zorder=5)
    plt.colorbar(sc, ax=ax, ticks=levels)


    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    ax.set_title(f"{year}/{month}\n後符 [%] max = {round(max(post_agreement_hit_persent_list), 1)}\nflash data source: {data_source}", fontproperties=myfont)
    plt.savefig(f"{data_top_path}/PFPA/{data_source}_{year}{month}/PA_hit_rate.png", bbox_inches='tight', dpi=300)


hit_rate()