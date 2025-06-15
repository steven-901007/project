import pyart


data_top_path = "C:/Users/steve/python_data/radar"
year = '2024'
month = '05'
day = '23'
hh = '08'
mm = '02'
ss = '00'



## === 讀取雷達檔案 ===
file_path = f"{data_top_path}/{year}{month}{day}_u.RCWF/{year}{month}{day}{hh}{mm}{ss}.VOL" 
radar = pyart.io.read(file_path)

## === 印出空間與時間定位資訊 ===
print("## 空間與時間定位資訊 ##")
print(f"data path:{data_top_path}/{year}{month}{day}_u.RCWF/{year}{month}{day}{hh}{mm}{ss}.VOL")
## 雷達站位置
print(f"Latitude : {round(float(radar.latitude['data'][0]),2)} °N")
print(f"Longitude: {round(float(radar.longitude['data'][0]),2)} °E")
print(f"Altitude : {radar.altitude['data'][0]} m")

## 掃描範圍資訊
print(f"Range (gate 數): {radar.ngates} bins")
print(f"Gate spacing   : {radar.range['meters_between_gates']} m")
print(f"First gate dist: {radar.range['meters_to_center_of_first_gate']} m")

## Azimuth / Elevation
print(f"Azimuth shape  : {radar.azimuth['data'].shape}")
print(f"Elevation shape: {radar.elevation['data'].shape}")
print(f"Azimuth (0-5): {radar.azimuth['data'][:5]}")
print(f"Elevation (0-5): {radar.elevation['data'][:5]}")

## 時間資訊
print(f"Time shape     : {radar.time['data'].shape}")
print(f"Time units     : {radar.time['units']}")
print(f"Time (0-5)     : {radar.time['data'][:5]} 秒")

