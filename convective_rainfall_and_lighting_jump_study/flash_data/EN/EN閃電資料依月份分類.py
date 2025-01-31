import pandas as pd

year = '2021'
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"




EN_flash_datas = pd.read_csv(f"{data_top_path}/閃電資料/raw_data/EN/{year}_EN/{year}_EN.txt")

# 補全時間部分
EN_flash_datas['observation_time'] = EN_flash_datas['observation_time'].apply(
    lambda x: f"{x} 00:00:00" if len(x) == 10 else x
)

# 轉換 observation_time 為 datetime 並提取月份
EN_flash_datas['observation_time'] = pd.to_datetime(EN_flash_datas['observation_time'], errors='coerce')
EN_flash_datas_plas_month = EN_flash_datas.copy()
EN_flash_datas_plas_month['month'] = EN_flash_datas_plas_month['observation_time'].dt.month


for month in range(1,13):
    month_data = EN_flash_datas[EN_flash_datas_plas_month['month'] == month]
    print(str(month).zfill(2))
    save_path = f"{data_top_path}/閃電資料/raw_data/EN/{year}_EN/{year}{str(month).zfill(2)}.csv"
    month_data.to_csv(save_path,index=False)


