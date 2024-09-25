from case_analysis_set import case_data_set
from case_draw import case_draw
from case_map_draw import case_map_draw
import calendar
##變數設定
#記得要先執行前估命中個案
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
year = '2021' #年分
month = '07' #月份
day = '24'
time_start = 9
time_end = 15
dis = 36
alpha = 2 #統計檢定
# station_name = 'O1P470' #前估max
station_name = '466880' #板橋
# station_name = 'C0V800' #六龜
# station_name = '466920' #台北
# max_month_day = calendar.monthrange(int(year),int(month))[-1]
# for i in range(1,max_month_day+1): #記得調case_draw的存檔位置
#     day = str(i).zfill(2)
case_data_set(year,month,day,time_start,time_end,dis,station_name,data_top_path)
case_draw(year,month,day,time_start,time_end,dis,station_name,data_top_path,alpha)
case_map_draw(station_name,data_top_path,year,month,day,time_start,time_end,dis)