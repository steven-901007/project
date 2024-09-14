from glob import glob
import pandas as pd
from tqdm import tqdm


year = '2021' #年分
month = '06' #月份
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
dis = 36

def fileset(path):    #建立資料夾
    import os
    
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

    # 將讀取的數據轉換為DataFrame，並根據文件結構分列
    data_df = pd.DataFrame([x.split() for x in data_lines])
    data_df.columns = title
    return data_df


fileset(f"{data_top_path}/雨量資料/cwa小時雨量")

# 關鍵字，數據部分開始的標題
keyword = '# stno'


hour_rain_data_paths = f"{data_top_path}/雨量資料/小時雨量/{year}_hrrain/CWB/{year}{month}**.txt"
result = glob(hour_rain_data_paths)
##auto資料處理
for hour_rain_data_path in result:
    print(hour_rain_data_path)
    hour_rain_auto_datas = read_data_after_preamble(hour_rain_data_path, keyword)

    # 將PP01轉換為數字類型並處理缺失值（小於0的數據替換為0）
    hour_rain_auto_datas['PP01'] = pd.to_numeric(hour_rain_auto_datas['PP01'], errors='coerce')  # 確保 PP01 是數字
    hour_rain_auto_datas['PP01'] = hour_rain_auto_datas['PP01'].apply(lambda x: 0 if x < 0 else x)  # 用0替換小於0的數據

    # 提取時間的yyyy-mm-dd-hh

    # 計算每個測站的每小時累積雨量


    # print(hour_rain_auto_datas[['stno','yyyymmddhh','PP01']])
    unique_stations = hour_rain_auto_datas['stno'].unique()
    # print(unique_stations)
    for station in tqdm(unique_stations,desc='資料建立中...'):
    # station = 'C0A520'    
        # print(station)
        station_data = hour_rain_auto_datas[hour_rain_auto_datas['stno'] == station][['yyyymmddhh','PP01']]
        station_data = pd.DataFrame(station_data)
        station_data.columns = ['data time','one hour rain']
        station_data.to_csv(f"{data_top_path}/雨量資料/cwa小時雨量/{station}.csv",index= False)
        # print(station_data)
