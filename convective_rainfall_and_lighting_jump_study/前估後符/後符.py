##新後符
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
month = '06' #月份(01~12)
dis = 36
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
data_source = 'TLDS'#閃電資料來源 (EN、TLDS)

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
fileset(f"{data_top_path}/前估後符")
fileset(f"{data_top_path}/前估後符/{data_source}_{year}{month}")

##有lighting jump但沒強降雨發生
data_path = f"{data_top_path}/雨量資料/測站資料/{year}_{month}.csv"
check_folder(data_path)
data = pd.read_csv(data_path)


# print(data)
check_folder(f"{data_top_path}/雨量資料/對流性降雨{dis}km/{year}/{month}")
check_folder(f"{data_top_path}/閃電資料/{data_source}/lighting_jump/{data_source}_{year}{month}_{dis}km")
post_agreement_station_name_list = []#後符測站名稱
post_agreement_hit_list = []#個測站後符命中的list
total_post_agreement_list = []#後符總量(lighting jump and rain + lighting jump and non_rain)
post_agreement_lon_data_list = []
post_agreement_lat_data_list = []

month_path = f"{data_top_path}/閃電資料/{data_source}/lighting_jump/{data_source}_{year}{month}_{dis}km/*.csv"
result  =glob.glob(month_path)

for flash_station_path in tqdm(result,desc=f"{year}{month}資料處理中...."):
    # print(flash_station_path)
# flash_station_path = "C:/Users/steve/python_data/研究所/閃電資料/lighting_jump/36km/2021/06/00H710.csv"
    flash_station_name = os.path.basename(flash_station_path).split('.')[0]
    # print(flash_station_name)

    #rain
    try:
        rain_station_path = f"{data_top_path}/雨量資料/對流性降雨{dis}km/{year}/{month}/{flash_station_name}.csv"
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
post_agreement_save_path = f"{data_top_path}/前估後符/{data_source}_{year}{month}/後符.csv"
pd.DataFrame(post_agreement_save_data).to_csv(post_agreement_save_path,index=False)


##後符繪圖

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

level = [0,100,200,300,400,500,600,700,850]
color_box = ['silver','purple','darkviolet','blue','g','y','orange','r']

for nb in post_agreement_hit_list:
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
ax.scatter(post_agreement_lon_data_list, post_agreement_lat_data_list, color=color_list, s=3, zorder=5)

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

ax.set_title(f"{year}年{month}月\n後符命中數 max = {round(max(post_agreement_hit_list),3)}\n flash data source：{data_source}")
pic_save_path = f"{data_top_path}/前估後符/{data_source}_{year}{month}/後符.png"
plt.savefig(pic_save_path, bbox_inches='tight', dpi=300)

## 這是用來確認colorbar的配置
fig,ax1 = plt.subplots()
X = [i for i in range(len(post_agreement_hit_list))]
Y = sorted(post_agreement_hit_list)
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

level = [0,20,40,50,60,70,80,90,100]
color_box = ['silver','purple','darkviolet','blue','g','y','orange','r']

for nb in post_agreement_hit_persent_list:
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
ax.scatter(post_agreement_lon_data_list, post_agreement_lat_data_list, color=color_list, s=3, zorder=5)

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

ax.set_title(f"{year}年{month}月\n後符命中率 [%] max = {round(max(post_agreement_hit_persent_list))}\n flash data source：{data_source}")
pic_save_path = f"{data_top_path}/前估後符/{data_source}_{year}{month}/後符命中率(%).png"
plt.savefig(pic_save_path, bbox_inches='tight', dpi=300)

## 這是用來確認colorbar的配置
fig,ax1 = plt.subplots()
X = [i for i in range(len(post_agreement_hit_persent_list))]
Y = sorted(post_agreement_hit_persent_list)
ax1.plot(X,Y,color =  'black',marker = "*",linestyle = '--') #折線圖
ax1.set_title('這是用來確認colorbar的配置')


# 顯示地圖
# plt.show()
print(f"Time：{year}{month}、dis：{dis}、source：{data_source}")