def fileset(path):    #建立資料夾
    import os
    
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"{path}已建立") 



def rain_station_location_data_to_list(data_top_path,year):## 讀取雨量站經緯度資料
    import pandas as pd
    data_path = f"{data_top_path}/研究所/雨量資料/{year}測站資料.csv"
    data = pd.read_csv(data_path)
    station_data_name = data['station name'].to_list()
    station_real_data_name = data['station real name'].to_list()
    lon_data = data['lon'].to_list()
    lat_data = data['lat'].to_list()
    # print(data)
    return station_data_name,station_real_data_name,lon_data,lat_data


