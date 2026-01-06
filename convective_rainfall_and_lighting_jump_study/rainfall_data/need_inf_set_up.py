import pandas as pd
import glob
import re
from tqdm import tqdm
from datetime import datetime, timedelta
import os


import sys
##變數設定

month =  sys.argv[2] if len(sys.argv) > 1 else "11"
 
year = sys.argv[1] if len(sys.argv) > 1 else '2024'

import platform
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"


def fileset(path):    #建立資料夾

    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 



##建立資料夾
file_path = f"{data_top_path}/rain_data/rainfall_data/{year}/{month}/"
fileset(file_path)
## 讀取每月資料


if year == '2021':
    month_path = f"{data_top_path}/rain_data/raw_data/{year}/{month}/{month}"
elif year == '2024':
    month_path = f"{data_top_path}/rain_data/raw_data/{year}/{month}"
result  =glob.glob(month_path+"/*")

for day_path in tqdm(result,desc='資料建立'):
    day = day_path.split('\\')[-1][-2:] #日期   
    # print('日期:'+day)
    
    # ## 讀取每日資料

    result  =glob.glob(day_path+'/*')
    for rain_data_path in result:
        time = os.path.splitext(os.path.basename(rain_data_path))[0].split('.')[0]
        time_obj = datetime.strptime(time, '%Y%m%d%H%M')+ timedelta(hours=8) #將UTC轉成LT
        # time_obj = datetime.strptime(time, '%Y%m%d%H%M')
        time = time_obj.strftime('%Y%m%d%H%M')
    
        # print('時間:'+time)
        rain_data_list = []
        rainfall_list = []
        # 每10分鐘資料處理 rain data >10mm (10min)
# 定義要嘗試的編碼順序：優先 UTF-8，再試 Big5
        ENCODINGS_TO_TRY = ['utf-8', 'big5'] 
        files_content = None # 用於儲存成功讀取的內容

        for encoding in ENCODINGS_TO_TRY:
            try:
                # 嘗試以當前編碼開啟檔案
                with open(rain_data_path, 'r', encoding=encoding) as files:
                    files_content = files.readlines()
                    # print(f"✅ 成功使用 {encoding} 編碼讀取 {os.path.basename(rain_data_path)}")
                break # 成功讀取後跳出編碼嘗試迴圈

            except UnicodeDecodeError:
                # 如果解碼失敗，印出錯誤並嘗試下一個編碼
                # print(f"❌ {encoding} 編碼失敗，嘗試下一個編碼。")
                continue # 繼續嘗試清單中的下一個編碼

            except Exception as e:
                # 處理其他可能發生的錯誤 (如 FileNotFoundError 等)
                print(f"讀取檔案 {os.path.basename(rain_data_path)} 時發生非編碼錯誤: {e}")
                break # 如果是其他錯誤，直接跳出，避免無限迴圈

        # ----------------------------------------------------
        # 原有的資料處理邏輯 (現在將對 files_content 進行迭代)

        line = 0
        
        if files_content: # 確保 files_content 有內容才進行處理
            for file in files_content: # 這裡的 file 變數代表檔案中的每一行
                elements = re.split(re.compile(r'\s+|\n|\*'),file.strip()) 

                if line >= 3 : #移除檔頭
    
                    if 120 <float(elements[4])< 122.1 and 21.5 <float(elements[3])< 25.5: #確認經緯度範圍
                        station_name = elements[0] #測站名稱

                        # rain_data_of_10min = float(elements[6]) #RAIN 
                        rain_data_of_10min = float(elements[7]) #RAIN_10MIN
                        rain_data_of_3_hour = float(elements[8]) #HOUR_3
                        rain_data_of_6_hour = float(elements[9]) #HOUR_6
                        rain_data_of_12_hour = float(elements[10]) #HOUR_12
                        rain_data_of_24_hour = float(elements[11]) #HOUR_24

                        if 0<rain_data_of_10min <= rain_data_of_3_hour <=rain_data_of_6_hour<= rain_data_of_12_hour <= rain_data_of_24_hour: #QC
                            rain_data_list.append(station_name)
                            rainfall_list.append(rain_data_of_10min)
                
                line += 1
        # ----------------------------------------------------

        if rain_data_list != []:
            rain_data_save = {
                'station name':rain_data_list,
                'rain data':rainfall_list
            }
            pd.DataFrame(rain_data_save, dtype=str).to_csv(f"{data_top_path}/rain_data/rainfall_data/{year}/{month}/{time}.csv",index=False)

from datetime import datetime
now_time = datetime.now()
formatted_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
print(f"{formatted_time} 完成 {year}/{month} need inf set up")