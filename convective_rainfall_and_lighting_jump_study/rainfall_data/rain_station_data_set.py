import os
import re
import glob
from tqdm import tqdm
import pandas as pd
from geopy.distance import geodesic

import sys
##變數設定
year = sys.argv[2].zfill(2) if len(sys.argv) > 1 else "2021"
month = sys.argv[1].zfill(2) if len(sys.argv) > 1 else "05" 
dis = 36

import platform
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"


max_lon = 122.1
min_lon = 120
max_lat = 25.5
min_lat = 21.5

def fileset(path):    #建立資料夾
    import os
    
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 


def rain_station_location_data(path):
    lon_data_list = []  # 經度
    lat_data_list = []  # 緯度
    name_data_list = []  #測站名稱
    real_name_data_list = [] #測站實際名稱

    line = 0
    try:
        with open(path, 'r', encoding='big5') as file:
            for line_text in file:
                if line >= 3:
                    data = re.split(re.compile(r'\s+|\n|\*'), line_text.strip())
                    if len(data) >= 5:
                        try:
                            lon = float(data[4])
                            lat = float(data[3])
                            if min_lon < lon < max_lon and min_lat < lat < max_lat:
                                lon_data_list.append(lon)
                                lat_data_list.append(lat)
                                name_data_list.append(data[0])
                                real_name_data_list.append(data[1])
                        except ValueError:
                            continue
                line += 1
    except UnicodeDecodeError:
        print(f"❌ 檔案編碼錯誤: {path}")
    except Exception as e:
        print(f"❌ 其他錯誤發生: {path}, 錯誤訊息: {e}")
    
    return lon_data_list, lat_data_list ,name_data_list ,real_name_data_list

fileset(f"{data_top_path}/rain_data/station_count_in_range/{year}_{month}")
fileset(f"{data_top_path}/rain_data/station_data/")
lon_data_list, lat_data_list ,station_name_data_list ,real_name_data_list = [],[],[],[]

##確認所有資料的測站都有被記錄
## 讀取每月資料
month_path = f"{data_top_path}/rain_data/raw_data/{year}/{month}/{month}"
result  =glob.glob(month_path+"/*")
for day_path in tqdm(result,desc=f'{year}{month}測站資料'):
    # print(day_path)
    day = day_path.split('/')[-1].split('\\')[-1] #日期
    # print('日期:'+day)

    ## 讀取每日資料
    result  =glob.glob(day_path+'/*')
    for rain_data_path in result:
        # print(rain_data_path)
        lon_list, lat_list ,station_name_list,real_name_list = rain_station_location_data(rain_data_path)
        for i in range(len(station_name_list)):
            if station_name_list[i] == 'C1E890':##rawdata錯誤修改
                lon_list[i] = 120.6718
                lat_list[i] = 24.4652
            if station_name_data_list.count(station_name_list[i]) == 0:
                station_name_data_list.append(str(station_name_list[i]))
                lon_data_list.append(round(float(lon_list[i]),2))
                lat_data_list.append(round(float(lat_list[i]),2))
                real_name_data_list.append(str(real_name_list[i]))


data = {
    'station name':station_name_data_list,
    'station real name':real_name_data_list,
    'lon':lon_data_list,
    'lat':lat_data_list
}
data_df = pd.DataFrame(data)
##測站資料
data_df.to_csv(f"{data_top_path}/rain_data/station_data/{year}_{month}.csv",encoding='utf-8-sig',index=False)


for station_name_nb in tqdm(range(len(station_name_data_list)),desc=f'{year}{month}測站範圍內測站數'):
# station_name_nb = 0
    station_name = str(station_name_data_list[station_name_nb])
    real_name = str(real_name_data_list[station_name_nb])
    station_lon = round(lon_data_list[station_name_nb],2)
    station_lat = round(lat_data_list[station_name_nb],2)
    station_lat_lon = (station_lat,station_lon)
    data_df['distance_km'] = data_df.apply(lambda row: geodesic((row['lat'], row['lon']), station_lat_lon).km, axis=1)
    save_data = data_df[data_df['distance_km'] < dis]['station name'].astype(str)
    # print(station_name)
    # print(save_data)
    save_path = f"{data_top_path}/rain_data/station_count_in_range/{year}_{month}/{station_name}.csv"
    pd.DataFrame(save_data).to_csv(save_path,index= False)

