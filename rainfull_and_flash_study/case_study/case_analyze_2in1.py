from rainfull_and_flash_study.case_study.case_analysis_set import case_data_set
from case_draw import case_draw

data_top_path = "C:/Users/steve/python_data"

##變數設定
year = '2021' #年分
month = '06' #月份
day = '09'
time_start = 15
time_end = 18
dis = 36
alpha = 2 #統計檢定
station_name = 'V2C250'


case_data_set(year,month,day,time_start,time_end,dis,station_name,data_top_path)
case_draw(year,month,day,time_start,time_end,dis,station_name,data_top_path,alpha)