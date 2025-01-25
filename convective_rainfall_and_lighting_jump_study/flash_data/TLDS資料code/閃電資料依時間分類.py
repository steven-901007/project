import os
import calendar
from tqdm import tqdm
import pandas as pd

year = '2021'  # 年分
month = '07'   # 月份
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"

def fileset(path):  # 建立資料夾
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 

fileset(data_top_path + "/研究所/閃電資料/依時間分類/" + year + '/' + month)

## 讀取閃電資料
flash_data_path = data_top_path + '/研究所/閃電資料/raw_data/TLDS/' + year + '/' + year + month + '.txt'
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
            
            # print(day)
            flash_data_lon_list = flash_rawdata[flash_rawdata['simple_time'] == day]['經度']
            flash_data_lat_list = flash_rawdata[flash_rawdata['simple_time'] == day]['緯度']
            flash_data_to_save = {
                'lon' : flash_data_lon_list,
                'lat' : flash_data_lat_list
            }
            day = pd.to_datetime(day, format='%Y%m%d%H%M')
            save_day = day + pd.Timedelta(minutes=1)
            save_day_str = save_day.strftime('%Y%m%d%H%M')
            # print(save_day_str)
            csv_file_path = f"{data_top_path}/閃電資料/依時間分類/{year}/{month}/{save_day_str}.csv"            
            pd.DataFrame(flash_data_to_save).to_csv(csv_file_path,index=False)