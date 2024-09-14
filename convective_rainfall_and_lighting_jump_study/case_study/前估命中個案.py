##前估
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



year = '2021' #年分
month = '06' #月份
dis = 36
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"

def fileset(path):    #建立資料夾
    import os
    
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"{path}已建立") 
fileset(f"{data_top_path}/個案分析/前估命中個案/{year}_{month}")

def rain_station_location_data_to_list(data_top_path,year):## 讀取雨量站經緯度資料
    import pandas as pd
    data_path = f"{data_top_path}/雨量資料/測站資料/{year}_{month}.csv"
    data = pd.read_csv(data_path)
    station_data_name = data['station name'].to_list()
    station_real_data_name = data['station real name'].to_list()
    lon_data = data['lon'].to_list()
    lat_data = data['lat'].to_list()
    # print(data)
    return station_data_name,station_real_data_name,lon_data,lat_data
station_data_name,station_real_data_name,lon_data,lat_data = rain_station_location_data_to_list(data_top_path,year)

def check_in_time_range(row, lj_times):
    return int(any((lj_times >= row['start time']) & (lj_times <= row['end time'])))

##強降雨發生但沒有lighting jump


month_path = f"{data_top_path}/雨量資料/對流性降雨{dis}km/{year}/{month}/**.csv"
result  =glob.glob(month_path)

for rain_station_path in tqdm(result,desc='資料處理中....'):
# rain_station_path = "C:/Users/steve/python_data/研究所/雨量資料/對流性降雨36km統計/2021/06/C0R490.csv"
    rain_station_name = rain_station_path.split('/')[-1].split('\\')[-1].split('.')[0]


    #flash
    try:
        flash_station_path = f"{data_top_path}/閃電資料/lighting_jump/{year}_{month}_{dis}km/{rain_station_name}.csv"
        rain_data = pd.read_csv(rain_station_path)
        flash_data = pd.read_csv(flash_station_path)
        # if rain_station_name == 'C0G880':
        #     print(rain_data)
    except:
        flash_station_path = None

    if flash_station_path != None:
        #end time< lighting jump <= time data
        rain_data['time data'] = pd.to_datetime(rain_data['time data'])
        rain_data['start time'] = rain_data["time data"] - pd.Timedelta(minutes= 50)
        rain_data['end time'] = rain_data['time data'] + pd.Timedelta(minutes=10)
        flash_data['LJ_time'] = pd.to_datetime(flash_data['LJ_time'])
        # print(rain_data)

        rain_data['LJ_in_time_range'] = rain_data.apply(lambda row: check_in_time_range(row, flash_data['LJ_time']), axis=1)

        # print(rain_data[rain_data['LJ_in_time_range'] == 1])
        # pd.set_option('display.max_rows', None)

        # print(flash_data)
        # print(rain_data['LJ_in_time_range'].sum())
        if rain_data['LJ_in_time_range'].sum() != 0:
            time_data = pd.to_datetime(rain_data[rain_data['LJ_in_time_range'] == 1]['time data'])
            LJ_data_save_path = f"{data_top_path}/個案分析/前估命中個案/{year}_{month}/{rain_station_name}_{rain_data['LJ_in_time_range'].sum()}.csv"
            LJ_data_save = {
                'time data' : time_data
            }
            pd.DataFrame(LJ_data_save).to_csv(LJ_data_save_path,index=False)


