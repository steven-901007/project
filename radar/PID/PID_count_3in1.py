from CV_map_lon_lat_set import lon_lat_set
from PID_range_square_CVmap import square_map

from PID_hotmap import draw_PID_hotmap_percentColor_countText
import sys
import os



year = sys.argv[1] if len(sys.argv) > 1 else '2021'
month = sys.argv[2] if len(sys.argv) > 2 else '05'
day = sys.argv[3] if len(sys.argv) > 3 else '24'
hh = sys.argv[4] if len(sys.argv) > 4 else '04'
mm = sys.argv[5] if len(sys.argv) > 5 else '50'

station = sys.argv[6] if len(sys.argv) > 6 else 'RCWF'
point_num = sys.argv[7] if len(sys.argv) > 7 else '1'  # 預設點選兩個點
if point_num == '1':
    range_radius = sys.argv[8] if len(sys.argv) > 8 else '0.05'  # 預設範圍半徑0.1度
    range_radius = float(range_radius)
else:
    range_radius = None
pid = 'park' #park or way(魏) 使用哪個PID

ss = '00'
show = False
add_flash=True
import platform
## ==== 路徑設定 ==== ##

data_top_path = "/home/steven/python_data/radar"
flash_data_top_path = "/home/steven/python_data/convective_rainfall_and_lighting_jump"

save_dir = f"{data_top_path}/PID_CS/{year}{month}{day}"
os.makedirs(save_dir, exist_ok=True)

point_num = int(point_num) 


points = lon_lat_set(
    data_top_path,
    year, month, day,
    hh, mm, ss,
    station,
    point_num,
    range_radius,
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
    sys.exit(1)


square_map(data_top_path,year,month,day,hh,mm,ss,lon0,lat0,lon1,lat1,show,station,add_flash,flash_data_top_path,set_extent=[120.5,123,24.5,26])

draw_PID_hotmap_percentColor_countText(data_top_path,year,
    month,
    day,
    hh,
    mm,
    ss,
    lon0,
    lat0,
    lon1,
    lat1,
    pid,
    station,
    ['GC/AP', 'BS', 'DS', 'WS', 'CR', 'GR', 'BD', 'RA', 'HR', 'RH']
)
# draw_PID_count_hotmap(data_top_path,year,month,day,hh,mm,ss,lon0,lat0,lon1,lat1,pid,station,['Graupel'])
# draw_PID_percent_hotmap(data_top_path,year,month,day,hh,mm,ss,lon0,lat0,lon1,lat1,pid,station,['Snow', 'Graupel', 'Hail'])
# pid = 'park' #park or way(魏) 使用哪個PID
# draw_PID_count_hotmap(data_top_path,year,month,day,hh,mm,ss,lon0,lat0,lon1,lat1,pid)
# draw_PID_percent_hotmap(data_top_path,year,month,day,hh,mm,ss,lon0,lat0,lon1,lat1,pid)
