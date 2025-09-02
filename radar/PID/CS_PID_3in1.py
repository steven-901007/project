from CV_map_lon_lat_set import lon_lat_set
from CS_line_CVmap import cross_section_map
from CS_PID import hydrometeor_cross_section

import os



year = '2021'
month = '05'
day = '30'
pid = 'way' #park or way(魏) 使用哪個PID
hh = '05'
mm = '55'


ss = '00'
show = False
add_flash=True
import platform
## ==== 路徑設定 ==== ##
if platform.system() == 'Windows':
    data_top_path = "C:/Users/steve/python_data/radar"
    flash_data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
elif platform.system() == 'Linux':
    data_top_path = "/home/steven/python_data/radar"
    flash_data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"

save_dir = f"{data_top_path}/PID_CS/{year}{month}{day}"
os.makedirs(save_dir, exist_ok=True)

points = lon_lat_set(
    data_top_path,
    year, month, day,
    hh, mm, ss,
    add_flash,
    flash_data_top_path
)

# points 應該是一個 list: [(lon0, lat0), (lon1, lat1)]
if points and len(points) == 2:
    lon0, lat0 = points[0]
    lon1, lat1 = points[1]
    print(f"\n自動設定剖面線：\n起點: ({lon0:.5f}, {lat0:.5f})\n終點: ({lon1:.5f}, {lat1:.5f})")
else:
    print("❌ 未正確取得兩個點，請重新執行")



cross_section_map(data_top_path,year,month,day,hh,mm,ss,lon0,lat0,lon1,lat1,show,add_flash,flash_data_top_path)

hydrometeor_cross_section(data_top_path,year,month,day,hh,mm,ss,lon0, lat0, lon1, lat1,pid,show)
pid = 'park' #park or way(魏) 使用哪個PID
hydrometeor_cross_section(data_top_path,year,month,day,hh,mm,ss,lon0, lat0, lon1, lat1,pid,show)