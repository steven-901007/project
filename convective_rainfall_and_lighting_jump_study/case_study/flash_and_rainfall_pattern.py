import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.feature import ShapelyFeature
from cartopy import geodesic
import pandas as pd
import numpy as np
import matplotlib.colors as mcolors



def flash_and_rainfall_pattern(year, month, day, time_start, time_end, dis, station_name, data_top_path, flash_source,one_month_draw):

    ## === 檔案路徑設定 ===
    prefigurance_path = f"{data_top_path}/PFPA/{flash_source}_{year}{month}/prefigurance.csv"
    post_agreement_path = f"{data_top_path}/PFPA/{flash_source}_{year}{month}/post_agreement.csv"
    position_path = f"{data_top_path}/rain_data/station_data/{year}_{month}.csv"
    range_station_name_path = f"{data_top_path}/rain_data/station_count_in_range/{year}_{month}/{station_name}.csv"
    rain_data_path = f"{data_top_path}/case_study/{station_name}/{dis}_{flash_source}_{year}{month}{day}_{str(time_start).zfill(2)}00to{str(time_end).zfill(2)}00/rain_raw_data.csv"
    flash_paths = f"{data_top_path}/flash_data/{flash_source}/sort_by_time/{year}/{month}/"

    ## === 資料讀取 ===
    prefigurance_datas = pd.read_csv(prefigurance_path)
    post_agreement_datas = pd.read_csv(post_agreement_path)
    position_datas = pd.read_csv(position_path)
    range_station_name_datas = pd.read_csv(range_station_name_path)
    rain_datas = pd.read_csv(rain_data_path)

    ## 強降雨次數統計（>=10mm）
    rain_data = rain_datas[rain_datas['rain data'] >= 10]
    rain_data_station_counts = rain_data.groupby('station name').size().reset_index(name='count')

    ## 合併測站資訊與統計次數
    range_station_inf_datas = pd.read_csv(position_path)
    range_station_need_inf_datas = pd.merge(range_station_inf_datas, range_station_name_datas, on='station name', how='inner')
    merged_df = pd.merge(range_station_need_inf_datas, rain_data_station_counts, on='station name', how='left')
    merged_df['count'] = merged_df['count'].fillna(0)  # 沒有資料的設為 0

    ## 中心測站資訊
    point_lon = position_datas[position_datas['station name'] == station_name]['lon'].iloc[0]
    point_lat = position_datas[position_datas['station name'] == station_name]['lat'].iloc[0]
    point_real_name = position_datas[position_datas['station name'] == station_name]['station real name'].iloc[0]
    pre_data = prefigurance_datas[prefigurance_datas['station name'] == station_name]
    post_data = post_agreement_datas[post_agreement_datas['station name'] == station_name]
    pre_hit = round(pre_data['hit persent'].iloc[0], 2) if not pre_data.empty else 'N/A'
    post_hit = round(post_data['hit persent'].iloc[0], 2) if not post_data.empty else 'N/A'

    ## 閃電資料讀取為座標點
    lon_list, lat_list = [], []
    for file in sorted(os.listdir(flash_paths)):
        if file.endswith('.csv'):
            time_str = file.split('.')[0]
            time = pd.to_datetime(time_str)
            t0 = pd.to_datetime(f"{year}{month}{day} {time_start}:00:00")
            t1 = pd.to_datetime(f"{year}{month}{day} {time_end}:00:00")
            if t0 <= time <= t1:
                df = pd.read_csv(os.path.join(flash_paths, file))
                if not df.empty:
                    lon_list += df['lon'].tolist()
                    lat_list += df['lat'].tolist()

    ## 畫圖範圍與字型
    lon_min, lon_max = 120.0, 122.5
    lat_min, lat_max = 21.5, 25.5
    from matplotlib.font_manager import FontProperties
    myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
    title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20) 
    plt.rcParams['axes.unicode_minus'] = False

    ## 畫圖開始
    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)

    ## 台灣底圖
    shp_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
    shape_feature = ShapelyFeature(Reader(shp_path).geometries(), ccrs.PlateCarree(), edgecolor="#BAF671FF", facecolor="w")
    ax.add_feature(shape_feature)
    gridlines = ax.gridlines(draw_labels=True, linestyle='--')
    gridlines.top_labels = False
    gridlines.right_labels = False

    ## 畫閃電點
    if lon_list:
        ax.scatter(lon_list, lat_list, color='black', s=1, zorder=3, label='Flash')

    # ## 畫中心測站
    # ax.scatter(point_lon, point_lat, color='b',marker ='x', s=30, zorder=5)

    ## 畫測站（用次數數值 + plasma colormap 顯示）
    cmap = plt.get_cmap('plasma_r')
    interval = 5
    raw_max = round(max(merged_df['count']))
    vmax = int(np.ceil(raw_max / interval)) * interval  # 向上取整
    vmin = 0
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    sc = ax.scatter(
    merged_df['lon'], merged_df['lat'],
    c=merged_df['count'],
    cmap=cmap, norm=norm,
    s=40,                     # 可以稍微放大一點看得更清楚
    edgecolors='black',       # 黑色邊框
    linewidths=0.7,           # 邊框粗細
    zorder=4,
    label='測站'
    )

    # 畫 36km 藍圈
    ## 基本參數
    center_lon = point_lon
    center_lat = point_lat
    radius_m = dis * 1000

    ## 產生兩段圓：第一段從 0°~180°，第二段從 90°~360°
    circle1 = geodesic.Geodesic().circle(lon=center_lon, lat=center_lat, radius=radius_m, n_samples=180, endpoint=False)
    circle2 = geodesic.Geodesic().circle(lon=center_lon, lat=center_lat, radius=radius_m, n_samples=180, endpoint=False)
    # 把第二段的角度往後平移 90°
    circle2 = np.roll(circle2, shift=90, axis=0)

    # 畫兩段
    ax.plot(circle1[:, 0], circle1[:, 1], color='lime',linestyle='--', transform=ccrs.PlateCarree())
    ax.plot(circle2[:, 0], circle2[:, 1], color='lime',linestyle='--', transform=ccrs.PlateCarree(), label=f'{dis}km')


    ## colorbar
    cbar = plt.colorbar(sc, ax=ax, ticks=np.linspace(vmin, vmax, int((vmax - vmin) / interval) + 1),
                        orientation='vertical', shrink=0.5, pad=0.05)
    cbar.set_label("雨量站強降雨次數", fontproperties=myfont)

    ## 標題與圖例
    ax.set_title(f"{point_real_name} 測站數 = {len(merged_df)}\nmax = {raw_max} 前估 = {pre_hit}  後符 = {post_hit}", fontproperties=myfont)
    # ax.legend(prop=myfont)

    ## 儲存
    case_root_path = f"{data_top_path}/case_study/{station_name}/{dis}_{flash_source}_{year}{month}{day}_{str(time_start).zfill(2)}00to{str(time_end).zfill(2)}00"
    os.makedirs(case_root_path, exist_ok=True)
    pic_save_path = os.path.join(case_root_path, 'flash_and_rainfall_map.png')
    plt.savefig(pic_save_path, bbox_inches='tight', dpi=300)
    if one_month_draw is False:
        plt.show()
    plt.close('all')




# month =  "05" 
# year = '2021'
# day = '30'
# time_start = 12 #(00~23)
# time_end = 21 #(00~23)
# dis = 36
# alpha = 2 #統計檢定
# flash_source = 'EN' # EN or TLDS
# station_name = 'C0AH30' #五分山
# one_month_draw = False
# data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
# flash_and_rainfall_pattern(year, month, day, time_start, time_end, dis, station_name, data_top_path, flash_source,one_month_draw)
