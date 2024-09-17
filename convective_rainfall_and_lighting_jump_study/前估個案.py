
import pandas as pd
from glob import glob
import os
from tqdm import tqdm

year = '2021'  # 年分
month = '06'   # 月份
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
dis = 36

def fileset(path):    #建立資料夾
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 

def check_in_time_range(row, lj_times):
    return int(any((lj_times >= row['start time']) & (lj_times <= row['end time'])))


fileset(f"{data_top_path}/前估後符/{year}_{month}_前估命中個案")


#取得對流性降雨station name
result = glob(f"{data_top_path}/雨量資料/對流性降雨36km/{year}/{month}/**.csv")
for convective_rainfall_path in result:
# convective_rainfall_path =f"{data_top_path}/雨量資料/對流性降雨36km/{year}/{month}/00H710.csv"
    station_name = os.path.basename(convective_rainfall_path).split('.')[0]
    # print(station_name)

    #取得周圍測站名稱
    around_station_names_df = pd.read_csv(f"{data_top_path}/雨量資料/測站範圍內測站數/{year}_{month}/{station_name}.csv")
    # print(around_station_names_df)

    #取得對流性降雨資料時間
    convective_rainfall_datas = pd.read_csv(convective_rainfall_path)
    convective_rainfall_times_df =  pd.to_datetime(convective_rainfall_datas['time data'])
    #取得LJ資料
    flash_path = f"{data_top_path}/閃電資料/lighting_jump/{year}_{month}_{dis}km/{station_name}.csv"
    flash_datas = pd.read_csv(flash_path)

    # print(convective_rainfall_datas)


    convective_rainfall_datas['start time'] = pd.to_datetime(convective_rainfall_datas["time data"]) - pd.Timedelta(minutes=40)
    convective_rainfall_datas['end time'] = pd.to_datetime(convective_rainfall_datas['time data']) + pd.Timedelta(minutes=10)
    flash_datas['LJ_time'] = pd.to_datetime(flash_datas['LJ_time'])

    convective_rainfall_datas['LJ or not'] = convective_rainfall_datas.apply(lambda row: check_in_time_range(row, flash_datas['LJ_time']), axis=1)

    # 初始化結果列表
    max_rainfall_list = []
    more_then_10mm_count_list = []
    total_rainfall_list = []

    for convective_rainfall_time in tqdm(convective_rainfall_times_df,desc=f"{station_name}資料建立中"):
        convective_rainfall_time_str = convective_rainfall_time.strftime('%Y%m%d%H%M')
        rainfall_path = f"{data_top_path}/雨量資料/降雨data/{year}/{month}/{convective_rainfall_time_str}.csv"
        
        # 檢查檔案是否存在，避免出現錯誤
        if os.path.exists(rainfall_path):
            rainfall_datas_df = pd.read_csv(rainfall_path)

            # 合併資料以取得周圍測站的降雨資料
            rainfall_merge_datas = pd.merge(around_station_names_df, rainfall_datas_df, on='station name', how='inner')
            # print(rainfall_merge_datas)
            # 找到周圍測站中最大的降雨量
            max_rainfall = rainfall_merge_datas['rain data'].max()
            max_rainfall_list.append(max_rainfall)

            # 計算降雨量大於10mm的測站數
            more_then_10mm_count = rainfall_merge_datas[rainfall_merge_datas['rain data'] >= 10]['rain data'].count()
            more_then_10mm_count_list.append(more_then_10mm_count)

            #計算區域範圍總降雨量
            total_rainfall = rainfall_merge_datas[rainfall_merge_datas['rain data'] >= 10]['rain data'].sum()
            total_rainfall_list.append(total_rainfall)
            # print(tatle_rainfall)

        else:
            # 如果檔案不存在，則設定為預設值 (例如 0)
            max_rainfall_list.append(0)
            more_then_10mm_count_list.append(0)
    convective_rainfall_datas = convective_rainfall_datas.rename(columns={'time data':'convective rainfall time'})
    convective_rainfall_datas['max rainfall'] = max_rainfall_list
    convective_rainfall_datas['more then 10mm count'] = more_then_10mm_count_list
    convective_rainfall_datas['total rainfall'] = total_rainfall_list
    convective_rainfall_datas = convective_rainfall_datas.drop(['start time','end time'],axis=1)
    # print(convective_rainfall_datas)
    save_path = f"{data_top_path}/前估後符/{year}_{month}_前估命中個案/{station_name}.csv"
    convective_rainfall_datas.to_csv(save_path,index= False)