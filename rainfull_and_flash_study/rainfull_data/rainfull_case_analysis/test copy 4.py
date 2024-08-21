#使用時間測站散步圖選擇時間點

import pandas as pd
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# 設定年分和月份
year = '2021'
month = '06'

# 設定資料路徑
data_top_path = "C:/Users/steve/python_data"
dis = 36

# 設定目標測站編號
station = '466920'

# 設定時間段（調整這些變數來選擇你要的時間段）
start_time = '010000'  # 開始時間
end_time = '020000'    # 結束時間

# 讀取測站資料
tg_station_data_path = f"{data_top_path}/研究所/雨量資料/{year}測站資料.csv"
tg_station_datas = pd.read_csv(tg_station_data_path)

# 獲取目標測站的實際名稱、經度和緯度
tg_station_real_name = tg_station_datas[tg_station_datas['station name'] == station]['station real name'].iloc[0]
tg_station_lon = tg_station_datas[tg_station_datas['station name'] == station]['lon'].iloc[0]
tg_station_lat = tg_station_datas[tg_station_datas['station name'] == station]['lat'].iloc[0]
tg_station_lat_lon = (tg_station_lat, tg_station_lon)

# 讀取雨量資料
data_path = f"{data_top_path}/研究所/雨量資料/{str(dis)}km個案分析/{month}/{station}/{station}_rain_data.xlsx"
datas = pd.read_excel(data_path)

# 計算每個測站到目標測站的距離，並篩選出距離小於5公里的資料
datas['distance'] = datas.apply(lambda row: geodesic((row['station lat'], row['station lon']), tg_station_lat_lon).km, axis=1)
tg_datas = datas[datas['distance'] < 5].dropna(axis=1, how='all')
print(tg_datas)
# 選取時間列進行篩選
time_columns = [col for col in tg_datas.columns if start_time <= col <= end_time]

# 取得測站的經緯度資料並排序
station_positions = tg_datas[['station name', 'station lon', 'station lat','distance']].drop_duplicates()
station_positions = station_positions.set_index('station name')

# 根據與tg測站的距離為標準
station_positions = station_positions.sort_values('distance', ascending=True)
station_order = station_positions.index.tolist()

# 將資料轉換為長格式以方便繪圖
data_long = tg_datas.melt(id_vars=['station name'], value_vars=time_columns, var_name='time', value_name='value')
data_long = data_long.dropna(subset=['value'])  # 移除NaN的資料
data_long['station name'] = pd.Categorical(data_long['station name'], categories=station_order, ordered=True)

# 設定顏色對應的級別和顏色
level = [0, 0.1, 0.5, 1, 2, 5, 7, 10, 20]
color_box = ['silver', 'purple', 'darkviolet', 'blue', 'g', 'y', 'orange', 'r']

# 設定顏色規範
cmap = mcolors.ListedColormap(color_box)
norm = mcolors.BoundaryNorm(level, cmap.N)

# 繪製散佈圖
plt.figure(figsize=(15, 8))
scatter = plt.scatter(
    x=data_long['time'],  # 將時間作為橫軸
    y=data_long['station name'].cat.codes,  # 使用排序後的測站索引作為Y值
    c=data_long['value'],  # 使用根據數值設定的顏色
    cmap=cmap,  # 使用自定義顏色表
    norm=norm,  # 使用自定義顏色範圍
    s=20  # 點的大小
)

# 加上顏色條
cbar = plt.colorbar(scatter, ticks=level, boundaries=level)
cbar.set_label('Rainfall (mm)')

# 設定軸標籤和標題
plt.xlabel('Time')
plt.ylabel('Station (Sorted by Latitude)')
plt.xticks(rotation=45)  # 如果時間標籤太長，可以旋轉標籤角度
plt.title('Scatter Plot of Station Data over Time')

# 顯示圖表
plt.show()
