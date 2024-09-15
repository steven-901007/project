import os
from glob import glob
import pandas as pd
from tqdm import tqdm

year = '2021'  # 年分
month = '07'   # 月份
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
dis = 36

def fileset(path):    #建立資料夾
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 

fileset(f"{data_top_path}/雨量資料/cwa小時雨量測試/min_data_to_hour")

# 設置路徑
station_name_paths = os.path.join(data_top_path, "雨量資料/cwa小時雨量測試/hour_data/**")
result = glob(station_name_paths)
for station_name_path in result:
    # print(station_name_path)
# 取得測站名稱
    if result:
        # station_name_path = result[0]
        station_name = os.path.basename(station_name_path).split('.')[0]  # 更正為使用 os.path.basename 來取得檔案名稱
        # print(f"測站名稱: {station_name}")

        # 初始化變數
        ten_min_rain_time_data_save = []
        ten_min_rain_data_save = []

        # 讀取每個十分鐘雨量的檔案
        ten_min_rain_paths = os.path.join(data_top_path, f"雨量資料/降雨data/{year}/{month}/**.csv")
        ten_min_rain_result = glob(ten_min_rain_paths)

        for ten_min_rain_path in tqdm(ten_min_rain_result, desc=f"{station_name}資料建立中"):
            ten_min_rain_time = os.path.basename(ten_min_rain_path).split('.')[0]
            
            ten_min_datas = pd.read_csv(ten_min_rain_path, on_bad_lines='skip')
            # 使用 eq().any() 來進行比較，避免 FutureWarning
            if ten_min_datas['station name'].eq(station_name).any():
                ten_min_rain_time_data_save.append(ten_min_rain_time)
                ten_min_rain_data_save.append(ten_min_datas.loc[ten_min_datas['station name'] == station_name, 'rain data'].values[0])

    # 創建 DataFrame
    min_data = pd.DataFrame({
        'data time': ten_min_rain_time_data_save,
        'one hour rain': ten_min_rain_data_save
    })

    # 將 'data time' 轉換為日期時間格式
    min_data['data time'] = pd.to_datetime(min_data['data time'], format='%Y%m%d%H%M')

    # 按小時進行分組並計算每小時的總降雨量
    min_data['hour'] = min_data['data time'].dt.floor('h')  # 按小時進行截取
    hourly_rainfall = min_data.groupby('hour')['one hour rain'].sum().reset_index()

    # 將 'hour' 格式化為 yyyymmddhh
    hourly_rainfall['hour'] = hourly_rainfall['hour'].dt.strftime('%Y%m%d%H') 
    hourly_rainfall.columns = ['data time','one hour rain']
    # 打印結果
    # print(hourly_rainfall)

    # 保存到CSV
    save_path = f"{data_top_path}/雨量資料/cwa小時雨量測試/min_data_to_hour/{station_name}.csv"
    hourly_rainfall.to_csv(save_path, index=False)
