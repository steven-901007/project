"""
要先執行prefigurance_case.py、prefigurance.py、post_agreement.py
"""

from case_analysis_set import case_data_set
from case_draw import case_draw
from flash_and_rainfall_pattern import flash_and_rainfall_pattern
import calendar
import sys
import pandas as pd
pd.set_option('future.no_silent_downcasting', True)



year = sys.argv[1] if len(sys.argv) > 1 else '2024'
month =  sys.argv[2] if len(sys.argv) > 2 else "05"
day = sys.argv[3] if len(sys.argv) > 3 else '24'

time_start = 00 #(00~23)
time_end = 23 #(00~23)
dis = 36
alpha = 2 #統計檢定
flash_source = 'EN' # EN or TLDS
# station_name = '01C400' #石門
# station_name = 'A0A010' #台大
station_name = 'C0AH30' #五分山
station_name = '467480'#嘉義

one_month_draw = True #True or False 這裡決定是畫整個月還是單一天


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
        flash_and_rainfall_pattern(year, month, day, time_start, time_end, dis, station_name, data_top_path, flash_source,one_month_draw)
        

elif one_month_draw == False:
    case_data_set(year,month,day,time_start,time_end,dis,station_name,data_top_path,flash_source)
    case_draw(year,month,day,time_start,time_end,dis,station_name,data_top_path,alpha,flash_source,one_month_draw)
    flash_and_rainfall_pattern(year, month, day, time_start, time_end, dis, station_name, data_top_path, flash_source,one_month_draw)
 

from datetime import datetime
now_time = datetime.now()
formatted_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
print(f"{formatted_time} 完成 {year}{month}")