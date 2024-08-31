import os
import calendar
from tqdm import tqdm
import pandas as pd

year = '2021' #年分
month = '06' #月份
data_top_path = "C:/Users/steve/python_data"
# data_top_path = 'C:/Users/steven.LAPTOP-8A1BDJC6/OneDrive/桌面'


def fileset(path):    #建立資料夾
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 

fileset(data_top_path + "/研究所/閃電資料/依時間分類/"+year+ '/' + month)


## 讀取閃電資料
flash_data_path = data_top_path+'/研究所/閃電資料/raw_data/'+year+'/'+year+month+'.txt'
flash_rawdata = pd.read_csv(flash_data_path,header = 0)
flash_rawdata['simple_time'] = year + month + flash_rawdata['日期時間'].str[8:10] + flash_rawdata['日期時間'].str[11:13] + flash_rawdata['日期時間'].str[14:16]
# print(flash_rawdata['simple_time'],flash_rawdata['經度'],flash_rawdata['緯度'])





last_day = calendar.monthrange(int(year),int(month))[1]
# print(last_day)

for dd in tqdm(range(1,last_day+1),desc = '寫入資料'):
    dd = str(dd).zfill(2)

    for HH in range(24):
        HH = str(HH).zfill(2)

        for MM in range(60):
            MM = str(MM).zfill(2)
            day = year+month+dd+HH+MM

            csv_file_path = data_top_path + "/研究所/閃電資料/依時間分類/"+year+ '/' + month + '/' + day + '.csv'

            flash_data_lon_list = flash_rawdata[flash_rawdata['simple_time'] == day]['經度']
            flash_data_lat_list = flash_rawdata[flash_rawdata['simple_time'] == day]['緯度']
            if flash_data_lat_list.empty == False:
                flash_data_to_save = {
                    'lon' : flash_data_lon_list,
                    'lat' : flash_data_lat_list
                }
                
                pd.DataFrame(flash_data_to_save).to_csv(csv_file_path)