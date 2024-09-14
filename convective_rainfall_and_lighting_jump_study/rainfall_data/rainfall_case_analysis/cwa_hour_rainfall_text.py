import os
from glob import glob
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from tqdm import tqdm


year = '2021'  # 年分
month = '06'  # 月份
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"


pd.set_option('future.no_silent_downcasting', True) 
station_name_data_list = []
rmse_data_list = []
# 讀取資料
hour_data_paths = f"{data_top_path}/雨量資料/cwa小時雨量測試/hour_data/**.csv"
result = glob(hour_data_paths)
# hour_data_path = result[0]
for hour_data_path in tqdm(result,desc='資料存取中...'):
    station_name = os.path.basename(hour_data_path).split('.')[0]
    # print(station_name)
    station_name_data_list.append(station_name)
    hour_datas = pd.read_csv(f"{data_top_path}/雨量資料/cwa小時雨量測試/hour_data/{station_name}.csv")
    min_data_to_hour_data = pd.read_csv(f"{data_top_path}/雨量資料/cwa小時雨量測試/min_data_to_hour/{station_name}.csv")

    # 檢查 'data time' 欄位是否為 datetime 格式，如果不是則進行轉換
    if hour_datas['data time'].dtype != 'datetime64[ns]':
        hour_datas['data time'] = pd.to_datetime(hour_datas['data time'])  # 不指定格式，讓 pandas 自動推斷
    if min_data_to_hour_data['data time'].dtype != 'datetime64[ns]':
        min_data_to_hour_data['data time'] = pd.to_datetime(min_data_to_hour_data['data time'])  # 同樣不指定格式

    # 合併資料（取聯集）
    datas_merged = pd.merge(hour_datas, min_data_to_hour_data, on=['data time'], how='outer').fillna(0).infer_objects(copy=False)

    # 計算 RMSE
    rmse = np.sqrt(mean_squared_error(datas_merged['one hour rain_x'], datas_merged['one hour rain_y']))
    # print(f"RMSE: {rmse}")
    rmse_data_list.append(round(rmse,2))
save_data = {
    'station name': station_name_data_list,
    'RMSE':rmse_data_list
}
save_path = f"{data_top_path}/雨量資料/cwa小時雨量測試/RMSE.csv"
pd.DataFrame(save_data).to_csv(save_path,index=False)
