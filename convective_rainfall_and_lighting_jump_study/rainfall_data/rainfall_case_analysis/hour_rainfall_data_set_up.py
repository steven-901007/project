import pandas as pd
from glob import glob
from tqdm import tqdm
from datetime import datetime, timedelta
import os


year = '2021'  # 年分
month = '06'  # 月份
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"

def fileset(path):  # 建立資料夾
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立")

def read_data_after_preamble(file_path, keyword):
    data_lines = []
    with open(file_path, 'r', encoding='big5') as file:
        is_data_section = False
        for line in file:
            if keyword in line:
                is_data_section = True  # 找到關鍵字，從此行開始讀取數據
                title = line[1:].split()
                continue
            if is_data_section:
                data_lines.append(line.strip())  # 收集數據行

    # 將讀取的數據轉換為 DataFrame，並根據文件結構分列
    data_df = pd.DataFrame([x.split() for x in data_lines])
    data_df.columns = title
    return data_df

# 創建存放資料的資料夾
fileset(f"{data_top_path}/雨量資料/cwa小時雨量測試/hour_data")

# 讀取資料並處理時間
hour_rain_data_paths = f"{data_top_path}/雨量資料/小時雨量/{year}_hrrain/CWB/{year}{month}**.txt"
result = glob(hour_rain_data_paths)
keyword = '# stno'

for hour_rain_data_path in result:
    hour_rain_auto_datas = read_data_after_preamble(hour_rain_data_path, keyword)

    # 將PP01轉換為數字類型
    hour_rain_auto_datas['PP01'] = pd.to_numeric(hour_rain_auto_datas['PP01'], errors='coerce')

    # 處理雨量數據，將小於0的數據替換為0
    hour_rain_auto_datas['PP01'] = hour_rain_auto_datas['PP01'].apply(lambda x: 0 if pd.notnull(x) and x < 0 else x)

    # 處理時間數據，防止出現 24 小時格式
    hour_rain_auto_datas['yyyymmddhh'] = hour_rain_auto_datas['yyyymmddhh'].apply(
        lambda x: datetime.strptime(x, '%Y%m%d%H') if '24' not in x[-2:] else 
        (datetime.strptime(x[:-2], '%Y%m%d') + timedelta(days=1)).replace(hour=0))

    unique_stations = hour_rain_auto_datas['stno'].unique()

    # 儲存每個測站的處理結果
    for station in tqdm(unique_stations, desc='資料建立中...'):
        station_data = hour_rain_auto_datas[hour_rain_auto_datas['stno'] == station][['yyyymmddhh', 'PP01']]
        station_data.columns = ['data time', 'one hour rain']
        station_data.to_csv(f"{data_top_path}/雨量資料/cwa小時雨量測試/hour_data/{station}.csv", index=False)
