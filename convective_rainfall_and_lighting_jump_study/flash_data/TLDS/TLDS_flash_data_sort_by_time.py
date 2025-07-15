import os
import calendar
from tqdm import tqdm
import pandas as pd
import sys


month =  sys.argv[2] if len(sys.argv) > 1 else "05" 
year = sys.argv[1] if len(sys.argv) > 1 else '2021'


import platform
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"


month_path = f"{data_top_path}/flash_data/TLDS/sort_by_time/{year}/{month}"
os.makedirs(month_path, exist_ok=True)
print(f"{month_path} 已建立")

## 讀取flash_data
flash_data_path = f'{data_top_path}/flash_data/raw_data/TLDS/{year}/{year}{month}.txt'
flash_rawdata = pd.read_csv(flash_data_path, header=0)
flash_rawdata['simple_time'] = pd.to_datetime(flash_rawdata['日期時間'], format='%Y-%m-%d %H:%M:%S', errors='coerce').dt.strftime('%Y%m%d%H%M')
# print(flash_rawdata['simple_time'])


last_day = calendar.monthrange(int(year), int(month))[1]

for dd in tqdm(range(1, last_day + 1), desc='寫入資料'):
    dd = str(dd).zfill(2)

    for HH in range(24):
        HH = str(HH).zfill(2)

        for MM in range(60):
            MM = str(MM).zfill(2)
            day = year + month + dd + HH + MM
            
            # 篩選該分鐘資料
            minute_data = flash_rawdata[flash_rawdata['simple_time'] == day]
            flash_data_lon_list = minute_data['經度']
            flash_data_lat_list = minute_data['緯度']
            col_type = '類型' if int(year) in [2023, 2024] else '雷擊型態'
            flash_data_type_list = minute_data[col_type]  # ✅ 加入這一行
            
            # 建立字典
            flash_data_to_save = {
                'lon': flash_data_lon_list,
                'lat': flash_data_lat_list,
                'lightning_type': flash_data_type_list  # ✅ 加入這一行
            }

            # 儲存時間為 +1 分鐘
            day = pd.to_datetime(day, format='%Y%m%d%H%M')
            save_day = day + pd.Timedelta(minutes=1)
            save_day_str = save_day.strftime('%Y%m%d%H%M')

            csv_file_path = f"{data_top_path}/flash_data/TLDS/sort_by_time/{year}/{month}/{save_day_str}.csv"            
            pd.DataFrame(flash_data_to_save).to_csv(csv_file_path, index=False)