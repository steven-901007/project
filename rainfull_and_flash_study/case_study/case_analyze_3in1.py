from case_analysis_set import case_data_set
from case_draw import case_draw
from case_map_draw import case_map_draw
##變數設定

data_top_path = "C:/Users/steve/python_data"
year = '2021' #年分
month = '06' #月份
day = '05'
time_start = 15
time_end = 22
dis = 36
alpha = 2 #統計檢定
# station_name = 'C0F9N0'
station_name = 'C0V800' #六龜
# station_name = '466920' #台北
# for i in range(1,31): #記得調case_draw的存檔位置
#     day = str(i).zfill(2)
case_data_set(year,month,day,time_start,time_end,dis,station_name,data_top_path)
case_draw(year,month,day,time_start,time_end,dis,station_name,data_top_path,alpha)
case_map_draw(station_name,data_top_path,year,month,day,time_start,time_end,dis)