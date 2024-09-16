import pandas as pd
from glob import glob
import os

year = '2021'  # 年分
month = '07'   # 月份
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
dis = 36


convective_rainfall_path =f"{data_top_path}/雨量資料/對流性降雨36km/2021/{month}/00H710.csv"
station_name = os.path.basename(convective_rainfall_path).split('.')[0]
print(station_name)
convective_rainfall_times = pd.read_csv(convective_rainfall_path)
print(convective_rainfall_times)
for convective_rainfall_time in convective_rainfall_times:
