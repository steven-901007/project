import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd


def case_map_draw(station_name,data_top_path,year,month,day,time_start,time_end,dis):
    prefigurance_path = f"{data_top_path}/研究所/前估後符/前估.csv"
    post_agreement_path = f"{data_top_path}/研究所/前估後符/後符.csv"
    data_path = f"{data_top_path}/研究所/雨量資料/{year}測站資料.csv"

    prefigurance_datas = pd.read_csv(prefigurance_path)
    post_agreement_datas = pd.read_csv(post_agreement_path)
    position_data = pd.read_csv(data_path)
    
    # 設定標記點的經緯度
    point_lon = position_data[position_data['station name'] == station_name]['lon'].iloc[0]
    point_lat = position_data[position_data['station name'] == station_name]['lat'].iloc[0]
    point_real_name = position_data[position_data['station name'] == station_name]['station real name'].iloc[0]
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

    ax.scatter(point_lon,point_lat,color = 'r', s=5, zorder=5)
    # 加入標籤
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    ax.set_title(f"{point_real_name} ({point_lon},{point_lat})\nprefigurance hit persent = {round(prefigurance_data['hit persent'].iloc[0],2)}\npost agreement hit persent = {round(post_agreement_data['hit persent'].iloc[0],2)}")

    # 顯示地圖
    # plt.show()
    case_root_path =  f"{data_top_path}/研究所/個案分析/{station_name}_{dis}_{year}{month}{day}_{str(time_start).zfill(2)}00to{str(time_end)}00"
    pic_save_path = case_root_path + '/map.png'
    plt.savefig(pic_save_path, bbox_inches='tight', dpi=300)
    print('地圖已建立')