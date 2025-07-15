import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from datetime import datetime
import sys
import platform

## === 參數設定 ===
month = sys.argv[2] if len(sys.argv) > 1 else "05"
year = sys.argv[1] if len(sys.argv) > 1 else "2021"
dis = 36  # 半徑 (km)

## === 路徑設定 ===
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"

## === 儲存資料夾建立 ===
output_path = f"{data_top_path}/flash_data/TLDS/sort_by_station/TLDS_{year}{month}_{dis}km"
os.makedirs(output_path, exist_ok=True)
print(f"{output_path} 已建立")

## === 讀閃電資料 ===
flash_data_path = f"{data_top_path}/flash_data/raw_data/TLDS/{year}/{year}{month}.txt"
flash_data_df = pd.read_csv(flash_data_path)

## 時間轉換（floor 到分鐘）
flash_data_df['Time'] = pd.to_datetime(flash_data_df['日期時間'], errors='coerce')
flash_data_df = flash_data_df.dropna(subset=['Time'])
flash_data_df = flash_data_df[flash_data_df['Time'].dt.month == int(month)]

## 改欄位名稱統一
flash_data_df = flash_data_df.rename(columns={'經度': 'lon', '緯度': 'lat'})

## === 讀測站資料 ===
station_datas_path = f"{data_top_path}/rain_data/station_data/{year}_{month}.csv"
station_datas_df = pd.read_csv(station_datas_path)

## === Haversine公式 計算兩點距離 ===
def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    r = 6371  # 地球半徑
    return c * r

## === 每個測站處理 ===
for index, row in tqdm(station_datas_df.iterrows(), total=station_datas_df.shape[0]):

    station_name = row['station name']
    station_lon = row['lon']
    station_lat = row['lat']

    # 計算距離
    flash_data_df['distance'] = haversine(flash_data_df['lon'], flash_data_df['lat'], station_lon, station_lat)

    # 篩選 36km 內閃電點
    near_flash_df = flash_data_df[flash_data_df['distance'] <= dis].copy()

    # 時間只保留到分鐘
    near_flash_df['data time'] = near_flash_df['Time'].dt.floor('min')

    # 統計每分鐘閃電次數
    flash_count_df = near_flash_df.groupby('data time').size().reset_index(name='flash_count')

    # 儲存結果
    save_path = f"{output_path}/{station_name}.csv"
    flash_count_df.to_csv(save_path, index=False)

now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"{now_time} 完成 TLDS {year}/{month} flash_datasort_by_time")
