from case_analysis_set import case_data_set
from case_draw import case_draw
from flash_and_rainfall_pattern import flash_and_rainfall_pattern
# from case_map_draw import case_map_draw
# from flash_pattern import flash_pattern
import calendar
import sys
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)

#記得要先執行前估命中個案

month =  sys.argv[2] if len(sys.argv) > 1 else "05" 
year = sys.argv[1] if len(sys.argv) > 1 else '2021'

day = '24'
time_start = 12 #(00~23)
time_end = 22 #(00~23)
dis = 36
alpha = 2 #統計檢定
flash_source = 'EN' # EN or TLDS
# station_name = 'O1P470' #前估max
# station_name = '466880' #板橋
# station_name = '01F680'
# station_name = '01C400'
station_name = 'C0AH30' #五分山
one_month_draw = False


import platform
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"



if one_month_draw == True:
    
    max_month_day = calendar.monthrange(int(year),int(month))[-1]
    for i in range(1,max_month_day+1):
        day = str(i).zfill(2)
        case_data_set(year,month,day,time_start,time_end,dis,station_name,data_top_path,flash_source)
        case_draw(year,month,day,time_start,time_end,dis,station_name,data_top_path,alpha,flash_source,one_month_draw)
        flash_and_rainfall_pattern(year, month, day, time_start, time_end, dis, station_name, data_top_path, flash_source)
        

elif one_month_draw == False:
    case_data_set(year,month,day,time_start,time_end,dis,station_name,data_top_path,flash_source)
    case_draw(year,month,day,time_start,time_end,dis,station_name,data_top_path,alpha,flash_source,one_month_draw)
    flash_and_rainfall_pattern(year, month, day, time_start, time_end, dis, station_name, data_top_path, flash_source)
 

from datetime import datetime
now_time = datetime.now()
formatted_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
print(f"{formatted_time} 完成 {year}{month}")