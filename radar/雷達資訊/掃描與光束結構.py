import pyart


data_top_path = "C:/Users/steve/python_data/radar"
year = '2021'
month = '11'
day = '26'
hh = '07'
mm = '36'
ss = '00'




## === 讀取雷達檔案 ===
file_path = f"{data_top_path}/{year}{month}{day}_u.RCWF/{year}{month}{day}{hh}{mm}{ss}.VOL" 
radar = pyart.io.read(file_path)

## === 印出掃描與光束結構資訊 ===
print("## 掃描與光束結構資訊 ##")



print(f"掃描圈數 (nsweeps): {radar.nsweeps}")  # 仰角數量
print(f"總射線數 (nrays)  : {radar.nrays}")    # 所有 ray 數
print(f"每條射線的 gate 數 (ngates): {radar.ngates}")  # 每條 ray 上的 bin 數

## 取出固定仰角並存成 list
fixed_angle_list = radar.fixed_angle['data'].tolist()
## 印出結果
print("fixed_angle_list =", fixed_angle_list)

print("\n--- 各掃描圈 Sweep 詳細資訊 ---")
for i in range(radar.nsweeps):
    start_idx = radar.sweep_start_ray_index['data'][i]
    end_idx = radar.sweep_end_ray_index['data'][i]
    fixed_angle = radar.fixed_angle['data'][i]
    sweep_mode = radar.sweep_mode['data'][i].decode('utf-8')

    print(f"Sweep {i:2d}:")
    print(f"  ▸ 仰角 (fixed_angle): {fixed_angle:.2f}°")
    print(f"  ▸ 掃描模式 (mode)   : {sweep_mode}")
    print(f"  ▸ 射線範圍 index    : {start_idx} ~ {end_idx}")
    print(f"  ▸ 射線數 (rays)     : {end_idx - start_idx + 1}")
