import pandas as pd
import glob
import re
from tqdm import tqdm
import importset
from datetime import datetime, timedelta
year = '2021' #年分
month = '07' #月份
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"


##建立資料夾
file_path = f"{data_top_path}/雨量資料/降雨data/{year}/{month}/"
importset.fileset(file_path)
## 讀取每月資料


month_path = f"{data_top_path}/雨量資料/{year}_{month}/{month}"
result  =glob.glob(month_path+"/*")

for day_path in tqdm(result,desc='資料建立'):
    day = day_path.split('\\')[-1][-2:] #日期   
    # print('日期:'+day)
    
    # ## 讀取每日資料

    result  =glob.glob(day_path+'/*')
    for rain_data_path in result:
        time = rain_data_path.split('\\')[-1].split('.')[0]
        time_obj = datetime.strptime(time, '%Y%m%d%H%M')+ timedelta(hours=8) #將UTC轉成LT
        # time_obj = datetime.strptime(time, '%Y%m%d%H%M')
        time = time_obj.strftime('%Y%m%d%H%M')
    
        # print('時間:'+time)
        rain_data_list = []
        rainfall_list = []
        # 每10分鐘資料處理 rain data >10mm (10min)
        line = 0
        with open(rain_data_path, 'r') as files:
            for file in files:
                elements = re.split(re.compile(r'\s+|\n|\*'),file.strip()) 

                if line >= 3 :  #移除檔頭
                    
                    if 120 <float(elements[4])< 122.1 and 21.5 <float(elements[3])< 25.5: #確認經緯度範圍
                        station_name = elements[0] #測站名稱
                        rain_data_of_10min = float(elements[6]) #MIN_10
                        # rain_data_of_10min = float(elements[6]) #RAIN
                        rain_data_of_3_hour = float(elements[8]) #HOUR_3
                        rain_data_of_6_hour = float(elements[9]) #HOUR_6
                        rain_data_of_12_hour = float(elements[10]) #HOUR_12
                        rain_data_of_24_hour = float(elements[11]) #HOUR_24

                        if 0<rain_data_of_10min <= rain_data_of_3_hour <=rain_data_of_6_hour<= rain_data_of_12_hour <= rain_data_of_24_hour: #QC
                            rain_data_list.append(station_name)
                            rainfall_list.append(rain_data_of_10min)
        
                line += 1

        if rain_data_list != []:
            rain_data_save = {
                'station name':rain_data_list,
                'rain data':rainfall_list
            }
            pd.DataFrame(rain_data_save, dtype=str).to_csv(f"{data_top_path}/雨量資料/降雨data/{year}/{month}/{time}.csv",index=False)


