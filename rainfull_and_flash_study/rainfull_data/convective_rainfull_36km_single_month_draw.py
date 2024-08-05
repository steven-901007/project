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


year = '2021' #年分
month = '06' #月份
dis = 36
data_top_path = "C:/Users/steve/python_data"

station_data_path = data_top_path + "/研究所/雨量資料/"+year+"測站資料.csv"
station_data = pd.read_csv(station_data_path)
station_name_list = station_data['station name'].to_list()
station_lon_df = station_data['lon']
station_lat_df = station_data['lat']
station_real_name = station_data['station real name'] #個案分析用

rain_36km_name_list = [] #個案分析用
rain_36km_count_list = [] #降雨次數
rain_36km_lon_list = []
rain_36km_lat_list = []
rain_36km_real_name_list = []#個案分析用

##降雨資料讀取

rain_data_paths = data_top_path + "/研究所/雨量資料/對流性降雨"+str(dis)+"km統計/"+year+"/"+month+"/**.csv"
result  =glob.glob(rain_data_paths)
for rain_data_path in tqdm(result,desc='資料讀取+紀錄'):
    # print(rain_data_path)
    rain_data_station_name = rain_data_path.split('/')[-1].split('\\')[-1].split('.')[0]
    # print(rain_data_station_name)
    rain_data_count = pd.read_csv(rain_data_path)['time data'].count()
    # print(rain_data_count)

    if rain_data_count != 0:
        rain_36km_name_list.append(rain_data_station_name)
        rain_36km_lon_list.append(station_lon_df[station_name_list.index(rain_data_station_name)])
        rain_36km_lat_list.append(station_lat_df[station_name_list.index(rain_data_station_name)])
        rain_36km_count_list.append(rain_data_count)
        rain_36km_real_name_list.append(station_real_name[station_name_list.index(rain_data_station_name)])

##個案分析區        

case_data ={
    'station name':rain_36km_name_list,
    'real name':rain_36km_real_name_list,
    'count':rain_36km_count_list

}
save_data_path = data_top_path + "/研究所/雨量資料/對流性降雨次數.csv"
pd.DataFrame(case_data).to_csv(save_data_path,index= False,encoding='utf-8-sig')

##個案分析區##




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

level = [0,50,100,150,200,300,350,400,500]
color_box = ['silver','purple','darkviolet','blue','g','y','orange','r']

for nb in rain_36km_count_list:
    more_then_maxma_or_not = 0
    for j in range(len(level)-1):
        if level[j]<nb<=level[j+1]:
            color_list.append(color_box[j])
            more_then_maxma_or_not = 1
            break
    if more_then_maxma_or_not == 0:
        color_list.append('lime')
        print(nb)
# print(len(color_list))


# 標記經緯度點
ax.scatter(rain_36km_lon_list, rain_36km_lat_list, color=color_list, s=3, zorder=5)

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

ax.set_title(year+"年"+month+"月"+'\n雨量>10mm/10min 事件數\nmax = '+ str(max(rain_36km_count_list)))


## 這是用來確認colorbar的配置
fig,ax1 = plt.subplots()
X = [i for i in range(len(rain_36km_count_list))]
Y = sorted(rain_36km_count_list)
ax1.plot(X,Y,color =  'black',marker = "*",linestyle = '--') #折線圖
ax1.set_title('這是用來確認colorbar的配置')


# 顯示地圖
plt.show()


