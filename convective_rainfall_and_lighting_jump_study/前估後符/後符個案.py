import pandas as pd
from glob import glob
import os
from tqdm import tqdm

year = '2021'  # 年分
month = '07'   # 月份
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
dis = 36
# pd.set_option('display.max_rows', None)  # 讓數據完整顯示

def fileset(path):    #建立資料夾
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 

def check_in_time_range(row, rain_times):  # 檢查範圍內最早的對流降雨時間
    in_range_times = rain_times[(rain_times >= row['LJ_time']) & (rain_times <= row['end time'])]
    if not in_range_times.empty:
        return in_range_times.min()  # 返回範圍內最早的時間
    else:
        return pd.NaT  # 如果沒有時間符合範圍，返回空值

def leading_time(row):  # 計算LJ_time與最早對流降雨時間的差距
    if pd.notnull(row['convective rainfall or not']):
        return row['LJ_time'] - row['convective rainfall or not']
    else:
        return pd.NaT
    

# 將負的 timedelta 格式轉換為一般的時分秒格式
def format_leading_time(leading_time):
    if pd.isnull(leading_time):
        return None
    
    # 獲取總秒數，忽略天數部分
    total_seconds = abs(leading_time.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # 返回格式化後的時間字符串
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"


fileset(f"{data_top_path}/前估後符/{year}_{month}_後符命中個案")

#取得LJ station name
result = glob(f"{data_top_path}/flash_data/lighting_jump/{year}_{month}_{dis}km/*.csv")
for LJ_path in result:
# LJ_path = f"{data_top_path}/flash_data/lighting_jump/{year}_{month}_{dis}km/01E030.csv"
    station_name = os.path.basename(LJ_path).split('.')[0]
    # print(station_name)

    #取得周圍測站名稱
    around_station_names_df = pd.read_csv(f"{data_top_path}/雨量資料/測站範圍內測站數/{year}_{month}/{station_name}.csv")
    # print(around_station_names_df)

    #取得LJ資料時間
    LJ_datas = pd.read_csv(LJ_path)
    LJ_times_df = pd.to_datetime(LJ_datas['LJ_time'])
    # 取得對流性降雨資料
    convective_rainfall_path = f"{data_top_path}/雨量資料/對流性降雨{dis}km/{year}/{month}/{station_name}.csv"
    convective_rainfall_datas = pd.read_csv(convective_rainfall_path)

    # print(LJ_times_df)

    LJ_datas['LJ_time'] = pd.to_datetime(LJ_datas['LJ_time'])
    LJ_datas['end time'] = LJ_datas['LJ_time'] + pd.Timedelta(minutes=50)
    convective_rainfall_datas['time data'] = pd.to_datetime(convective_rainfall_datas['time data'])

    LJ_datas['convective rainfall or not'] = LJ_datas.apply(lambda row: check_in_time_range(row, convective_rainfall_datas['time data']), axis=1)

    # print(convective_rainfall_datas)
    # print(LJ_datas[LJ_datas['convective rainfall or not'] == 1])
    LJ_datas['convective rainfall or not'] = pd.to_datetime(LJ_datas['convective rainfall or not'])

    LJ_datas['leading time'] = LJ_datas.apply(lambda row: leading_time(row), axis=1)
    LJ_datas['leading time'] = LJ_datas['leading time'].apply(format_leading_time)


    rain_time_df = LJ_datas['convective rainfall or not']
    # 初始化結果列表
    max_rainfall_list = []
    more_then_10mm_count_list = []
    total_rainfall_list = []

    for rain_time in tqdm(rain_time_df, desc=f"{station_name}資料建立中"):
        # print(rain_time)
        if pd.notnull(rain_time):
            rain_time_str = rain_time.strftime('%Y%m%d%H%M')
            rainfall_path = f"{data_top_path}/雨量資料/降雨data/{year}/{month}/{rain_time_str}.csv"
            # print(rain_time_str)
            # 檢查檔案是否存在，避免出現錯誤
            if os.path.exists(rainfall_path):
                rainfall_datas_df = pd.read_csv(rainfall_path)
                # print(rainfall_datas_df)
                # 合併資料以取得周圍測站的降雨資料
                rainfall_merge_datas = pd.merge(around_station_names_df, rainfall_datas_df, on='station name', how='inner')
                # print(rainfall_merge_datas)

                # 找到周圍測站中最大的降雨量
                max_rainfall = rainfall_merge_datas['rain data'].max()
                max_rainfall_list.append(max_rainfall)

                # 計算降雨量大於10mm的測站數
                more_then_10mm_count = rainfall_merge_datas[rainfall_merge_datas['rain data'] >= 10]['rain data'].count()
                more_then_10mm_count_list.append(more_then_10mm_count)

                # 計算區域範圍總降雨量
                total_rainfall = rainfall_merge_datas[rainfall_merge_datas['rain data'] >= 10]['rain data'].sum()
                total_rainfall_list.append(total_rainfall)
            else:
                # 如果檔案不存在，則設定為預設值 (例如 0)
                max_rainfall_list.append(0)
                more_then_10mm_count_list.append(0)
                total_rainfall_list.append(0)
        else:
            max_rainfall_list.append(None)
            more_then_10mm_count_list.append(None)
            total_rainfall_list.append(None)     

    # print(max_rainfall_list)
    LJ_datas = LJ_datas.rename(columns={'time data': 'convective rainfall time'})
    LJ_datas['max rainfall'] = max_rainfall_list
    LJ_datas['more then 10mm count'] = more_then_10mm_count_list
    LJ_datas['total rainfall'] = total_rainfall_list
    LJ_datas = LJ_datas.drop(['end time'], axis=1)
    # print(LJ_datas.head(100))
    save_path = f"{data_top_path}/前估後符/{year}_{month}_後符命中個案/{station_name}.csv"
    LJ_datas.to_csv(save_path, index=False)
