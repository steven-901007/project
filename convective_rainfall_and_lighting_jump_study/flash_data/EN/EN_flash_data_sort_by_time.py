import os
import pandas as pd
from datetime import datetime, timedelta
import calendar
from tqdm import tqdm
import sys


month =  sys.argv[2] if len(sys.argv) > 1 else "05" 
year = sys.argv[1] if len(sys.argv) > 1 else '2024'

data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
data_time_zone = 'LCT'  # LCT or UTC

def fileset(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 

fileset(f"{data_top_path}/flash_data/EN/sort_by_time/{year}/{month}")

# 讀取資料
flash_data_path = f"{data_top_path}/flash_data/raw_data/EN/lightning_{year}.txt"
flash_rawdata = pd.read_csv(flash_data_path)

# 時間處理，保留年月日時分
flash_rawdata['Time'] = pd.to_datetime(flash_rawdata['Time'], format='mixed')
flash_rawdata['simple_time'] = flash_rawdata['Time'].dt.strftime('%Y%m%d%H%M')

# 新增 LCT 調整後的時間欄位
flash_rawdata['save_time'] = pd.to_datetime(flash_rawdata['simple_time'], format='%Y%m%d%H%M') + timedelta(minutes=1)
if data_time_zone == 'UTC':
    flash_rawdata['save_time'] = flash_rawdata['save_time'] + timedelta(hours=8)

flash_rawdata['save_time_str'] = flash_rawdata['save_time'].dt.strftime('%Y%m%d%H%M')
flash_rawdata['save_month'] = flash_rawdata['save_time'].dt.strftime('%m')

# 篩選目標月份資料
flash_month_data = flash_rawdata[flash_rawdata['save_month'] == month]

# groupby 分類
grouped = flash_month_data.groupby('save_time_str')

# 計算該月份天數
last_day = calendar.monthrange(int(year), int(month))[1]

# 逐分鐘檢查
for dd in tqdm(range(1, last_day + 1), desc='檢查每分鐘'):
    dd = str(dd).zfill(2)
    for HH in range(24):
        HH = str(HH).zfill(2)
        for MM in range(60):
            MM = str(MM).zfill(2)
            this_time_str = f"{year}{month}{dd}{HH}{MM}"
            this_time_dt = pd.to_datetime(this_time_str, format='%Y%m%d%H%M')
            save_time_str = (this_time_dt + timedelta(minutes=1)).strftime('%Y%m%d%H%M')

            save_folder = f"{data_top_path}/flash_data/EN/sort_by_time/{year}/{month}/"
            fileset(save_folder)
            csv_file_path = save_folder + f"{save_time_str}.csv"

            if save_time_str in grouped.groups:
                group = grouped.get_group(save_time_str)
                group[['lon', 'lat', 'lightning_type']].to_csv(csv_file_path, index=False)
            else:
                pd.DataFrame(columns=['lon', 'lat', 'lightning_type']).to_csv(csv_file_path, index=False)

now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"{now_time} 完成 EN {year}/{month} flash_datasort_by_time, time zone = {data_time_zone}，空白檔案已補上")
