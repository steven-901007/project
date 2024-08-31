import matplotlib.pyplot as plt
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import pandas as pd
from cartopy import geodesic


def case_map_draw(station_name,data_top_path,year,month,day,time_start,time_end,dis):
    prefigurance_path = f"{data_top_path}/研究所/前估後符/前估.csv"
    post_agreement_path = f"{data_top_path}/研究所/前估後符/後符.csv"
    position_path = f"{data_top_path}/研究所/雨量資料/{year}測站資料.csv"
    range_station_name_path = f"{data_top_path}/研究所/雨量資料/{year}測站範圍內測站數/{station_name}.csv"
    range_station_inf_path = f"{data_top_path}/研究所/雨量資料/{year}測站資料.csv"

    prefigurance_datas = pd.read_csv(prefigurance_path)
    post_agreement_datas = pd.read_csv(post_agreement_path)
    position_datas = pd.read_csv(position_path)
    range_station_name_datas = pd.read_csv(range_station_name_path)
    range_station_inf_datas = pd.read_csv(range_station_inf_path)
    # print(range_station_name_datas)
    # print(range_station_inf_datas)
    range_station_need_inf_datas = pd.merge(range_station_inf_datas,range_station_name_datas, on='station name', how='inner')
    range_station_count = range_station_need_inf_datas['station name'].count()
    # print(range_station_need_inf_datas['station name'].count())
    # 設定標記點的經緯度
    point_lon = position_datas[position_datas['station name'] == station_name]['lon'].iloc[0]
    point_lat = position_datas[position_datas['station name'] == station_name]['lat'].iloc[0]
    point_real_name = position_datas[position_datas['station name'] == station_name]['station real name'].iloc[0]
    prefigurance_data = prefigurance_datas[prefigurance_datas['station name'] == station_name]
    post_agreement_data = post_agreement_datas[post_agreement_datas['station name'] == station_name]

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

    ax.scatter(point_lon,point_lat,color = 'r', s=15, zorder=5,label = f"{station_name}")#main stataion
    ax.scatter(range_station_need_inf_datas['lon'],range_station_need_inf_datas['lat'],color = 'g',s=1,zorder=4,label = 'around stataion location') #周圍dis內的測站
    g = geodesic.Geodesic()
    circle = g.circle(lon=point_lon, lat=point_lat, radius=dis*1000)  # radius in meters
    ax.plot(circle[:, 0], circle[:, 1], color='blue', transform=ccrs.PlateCarree(),label = f"半徑 = {dis}")


    # 加入標籤
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.legend()
    ax.set_title(f"{point_real_name} ({point_lon},{point_lat})\ninside {dis}km station number = {range_station_count}\nprefigurance hit persent = {round(prefigurance_data['hit persent'].iloc[0],2)}\npost agreement hit persent = {round(post_agreement_data['hit persent'].iloc[0],2)}")

    # 顯示地圖

    case_root_path =  f"{data_top_path}/研究所/個案分析/{station_name}_{dis}_{year}{month}{day}_{str(time_start).zfill(2)}00to{str(time_end)}00"
    pic_save_path = case_root_path + '/map.png'
    plt.savefig(pic_save_path, bbox_inches='tight', dpi=300)
    print('地圖已建立')
    # plt.show()

# ## 變數設定
# data_top_path = "C:/Users/steve/python_data"
# year = '2021' #年分
# month = '06' #月份
# day = '01'
# time_start = 12
# time_end = 17
# dis = 36
# alpha = 2 #統計檢定
# station_name = 'C0G880'



# case_map_draw(station_name,data_top_path,year,month,day,time_start,time_end,dis)