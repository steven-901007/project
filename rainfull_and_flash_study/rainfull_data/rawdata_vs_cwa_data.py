import pandas as pd
from glob import glob
from tqdm import tqdm
import re
import numpy as np

year = '2021' #年分
month = '06' #月份
data_top_path = "C:/Users/steve/python_data"


station_name_path = f"{data_top_path}/研究所/雨量資料/{year}測站資料.csv"
station_name_datas = pd.read_csv(station_name_path)
station_name_data_list = station_name_datas['station name'].to_list()
station_real_name_data_df = station_name_datas['station real name']
station_rain_sum_list = [0 for i in station_name_data_list]


##資料建立

month_path = f"{data_top_path}/研究所/雨量資料/{year}_{month}/{month}"
result  =glob(month_path+"/*")

for day_path in tqdm(result,desc='資料建立'):
    day = day_path.split('\\')[-1][-2:] #日期   
    # print('日期:'+day)  
    daily_files = glob(day_path+'/*')

    # 讀取每日資料
    for rain_data_path in daily_files:
        # print(rain_data_path)

        line = 0
        with open(rain_data_path, 'r') as files:
            for file in files:
                elements = re.split(re.compile(r'\s+|\n|\*'),file.strip()) 

                if line >= 3 :  #移除檔頭
                    station_name = elements[0] #測站名稱
                    rain_data_of_10min = float(elements[7]) #MIN_10
                    rain_data_of_3_hour = float(elements[8]) #HOUR_3
                    rain_data_of_6_hour = float(elements[9]) #HOUR_6
                    rain_data_of_12_hour = float(elements[10]) #HOUR_12
                    rain_data_of_24_hour = float(elements[11]) #HOUR_24

                    if 0<rain_data_of_10min <= rain_data_of_3_hour <=rain_data_of_6_hour<= rain_data_of_12_hour <= rain_data_of_24_hour: #QC and data !=0 or -999
                        try: #資料可能在研究經緯度外
                            station_rain_sum_list[station_name_data_list.index(station_name)] += rain_data_of_10min
                        except:pass
                line += 1

raw_rain_data = { #raw測站所計算的結果
    'station name':station_name_data_list,
    'station real name':station_real_name_data_df,
    'total rain':station_rain_sum_list
}
raw_rain_data_df = pd.DataFrame(raw_rain_data)
# print(raw_rain_data_df)

## cwa資料
cwa_rain_data_path = f"{data_top_path}/研究所/雨量資料/cwa{year}{month}各測站每日降雨資料.csv"
cwa_rain_datas = pd.read_csv(cwa_rain_data_path)
cwa_rain_datas = cwa_rain_datas.rename(columns={
    '測站':'station real name',
    '(毫米)':'total rain'
})
cwa_rain_datas_df = pd.DataFrame(cwa_rain_datas)
cwa_rain_datas_df['total rain'] = cwa_rain_datas_df['total rain'].astype(float).round()
# print(cwa_rain_datas_df)
    
union = pd.merge(raw_rain_data_df,cwa_rain_datas_df,on='station real name',how = 'inner') #資料交集
union = union.rename(columns={
    'total rain_x':'raw data',
    'total rain_y':'cwa data'
})

print(union)
correlation = np.corrcoef(union['raw data'], union['cwa data'])[0, 1]
print(f"raw data 和 cwa data 之間的相關係數為: {correlation}")
print(f"{year}年{month}月raw data 和cwa data交集的測站數為{union['station name'].count()}")


##raw測站所計算的結果存檔
save_data_path = f"{data_top_path}/研究所/雨量資料/{year}{month}_total_rain_sum.csv"
cwa_rain_datas.to_csv(save_data_path,index=False,encoding='utf-8-sig')