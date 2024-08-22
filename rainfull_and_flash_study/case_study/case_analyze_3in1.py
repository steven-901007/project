from case_analysis_set import case_data_set
from case_draw import case_draw
from case_map_draw import case_map_draw
##變數設定
data_top_path = "C:/Users/steve/python_data"
year = '2021' #年分
month = '06' #月份
day = '01'
time_start = 12
time_end = 17
dis = 36
alpha = 2 #統計檢定
station_name = 'C0G880'


case_data_set(year,month,day,time_start,time_end,dis,station_name,data_top_path)
case_draw(year,month,day,time_start,time_end,dis,station_name,data_top_path,alpha)
case_map_draw(station_name,data_top_path,year,month,day,time_start,time_end,dis)