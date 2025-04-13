import matplotlib.pyplot as plt
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import pandas as pd
from cartopy import geodesic
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import matplotlib as mpl




def case_map_draw(year,month,day,time_start,time_end,dis,station_name,data_top_path,flash_source):
    prefigurance_path = f"{data_top_path}/前估後符/{flash_source}_{year}{month}/前估.csv"
    post_agreement_path = f"{data_top_path}/前估後符/{flash_source}_{year}{month}/後符.csv"
    position_path = f"{data_top_path}/雨量資料/測站資料/{year}_{month}.csv"
    range_station_name_path = f"{data_top_path}/雨量資料/測站範圍內測站數/{year}_{month}/{station_name}.csv"
    rain_data_path = f"{data_top_path}/個案分析/{station_name}/{dis}_{flash_source}_{year}{month}{day}_{str(time_start).zfill(2)}00to{str(time_end).zfill(2)}00/rain_raw_data.csv"


    prefigurance_datas = pd.read_csv(prefigurance_path)
    post_agreement_datas = pd.read_csv(post_agreement_path)
    position_datas = pd.read_csv(position_path)
    range_station_name_datas = pd.read_csv(range_station_name_path)
    range_station_inf_datas = pd.read_csv(position_path)
    rain_datas = pd.read_csv(rain_data_path)
    # print(range_station_name_datas)
    # print(range_station_inf_datas)

    rain_data=rain_datas[rain_datas['rain data'] >= 10]
    rain_data_station_counts = rain_data.groupby('station name').size().reset_index(name='count')
    # print(rain_data_station_counts)
    print(f"半徑強降雨次數最高為 {rain_data_station_counts['count'].max()}")

    level = [0,5,10,15,20,25,30,35]
    color_box = ['silver','orange','y','g','blue','darkviolet','purple']
    conditions = [
        (rain_data_station_counts['count'] >= level[0]) & (rain_data_station_counts['count'] < level[1]),
        (rain_data_station_counts['count'] >= level[1]) & (rain_data_station_counts['count'] < level[2]),
        (rain_data_station_counts['count'] >= level[2]) & (rain_data_station_counts['count'] < level[3]),
        (rain_data_station_counts['count'] >= level[3]) & (rain_data_station_counts['count'] < level[4]),
        (rain_data_station_counts['count'] >= level[4]) & (rain_data_station_counts['count'] < level[5]),
        (rain_data_station_counts['count'] >= level[5]) & (rain_data_station_counts['count'] < level[6]),
        (rain_data_station_counts['count'] >= level[6]) & (rain_data_station_counts['count'] < level[7]),
    ]
    # level = [0,1,3,5,10]
    # color_box = ['silver','b','g','orange']
    # conditions = [
    #     (rain_data_station_counts['count'] >= level[0]) & (rain_data_station_counts['count'] < level[1]),
    #     (rain_data_station_counts['count'] >= level[1]) & (rain_data_station_counts['count'] < level[2]),
    #     (rain_data_station_counts['count'] >= level[2]) & (rain_data_station_counts['count'] < level[3]),
    #     (rain_data_station_counts['count'] >= level[3]) & (rain_data_station_counts['count'] < level[4]),
    # ]
    # 對應的顏色

    # 使用 np.select 根據條件設置顏色
    rain_data_station_counts['color'] = np.select(conditions, color_box)
    # print(rain_data_station_counts)
    range_station_need_inf_datas = pd.merge(range_station_inf_datas,range_station_name_datas, on='station name', how='inner')
    range_station_count = range_station_need_inf_datas['station name'].count()
    merged_df = pd.merge(range_station_need_inf_datas, rain_data_station_counts[['station name','color']], on='station name', how='left')
    merged_df['color'] = merged_df['color'].fillna('silver')
    # print(merged_df)
    # 設定標記點的經緯度
    point_lon = position_datas[position_datas['station name'] == station_name]['lon'].iloc[0]
    point_lat = position_datas[position_datas['station name'] == station_name]['lat'].iloc[0]
    point_real_name = position_datas[position_datas['station name'] == station_name]['station real name'].iloc[0]
    prefigurance_data = prefigurance_datas[prefigurance_datas['station name'] == station_name]
    post_agreement_data = post_agreement_datas[post_agreement_datas['station name'] == station_name]

    if not prefigurance_data.empty and not post_agreement_data.empty:
        pre_hit_persent = round(prefigurance_data['hit persent'].iloc[0], 2)
        post_hit_persent = round(post_agreement_data['hit persent'].iloc[0], 2)
    else:
        pre_hit_persent = 'N/A'
        post_hit_persent = 'N/A'

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

    ax.scatter(point_lon,point_lat,color = 'r', s=15, zorder=5,label = f"{station_name}")#main stataion
    ax.scatter(range_station_need_inf_datas['lon'],range_station_need_inf_datas['lat'],color = merged_df['color'],s=5,zorder=4,label = 'around stataion location') #周圍dis內的測站
    g = geodesic.Geodesic()
    circle = g.circle(lon=point_lon, lat=point_lat, radius=dis*1000)  # radius in meters
    ax.plot(circle[:, 0], circle[:, 1], color='blue', transform=ccrs.PlateCarree(),label = f"半徑 = {dis}")

    # colorbar setting

    nlevel = len(level)
    cmap1 = mpl.colors.ListedColormap(color_box, N=nlevel)
    cmap1.set_over('fuchsia')
    cmap1.set_under('black')
    norm1 = mcolors.Normalize(vmin=min(level), vmax=max(level))
    norm1 = mcolors.BoundaryNorm(level, nlevel, extend='max')
    im = cm.ScalarMappable(norm=norm1, cmap=cmap1)
    cbar1 = plt.colorbar(im,ax=ax, extend='neither', ticks=level, aspect=30, shrink=0.5)
    cbar1.set_label('Rain Station Count', rotation=270, labelpad=20)
    # 加入標籤
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()
    ax.set_title(f"{point_real_name} ({point_lon},{point_lat})\ninside {dis}km station number = {range_station_count}\nprefigurance hit persent = {pre_hit_persent}\npost agreement hit persent = {post_hit_persent}")

    # 顯示地圖

    case_root_path =  f"{data_top_path}/個案分析/{station_name}/{dis}_{flash_source}_{year}{month}{day}_{str(time_start).zfill(2)}00to{str(time_end).zfill(2)}00"
    pic_save_path = case_root_path + '/map.png'
    plt.savefig(pic_save_path, bbox_inches='tight', dpi=300)
    print('地圖已建立')
    # plt.show()

# ## 變數設定
# data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
# year = '2021' #年分
# month = '06' #月份
# day = '01'
# time_start = 00
# time_end = 12
# dis = 36
# alpha = 2 #統計檢定
# flash_source = 'EN' # EN or TLDS
# station_name = '01P190'


# case_map_draw(year,month,day,time_start,time_end,dis,station_name,data_top_path,flash_source)