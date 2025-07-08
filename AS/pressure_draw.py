import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.dates as mdates
import pandas as pd


## === 參數設定 ===
data_top_path = "C:/Users/steve/python_data/AS"
data_folder = rf"{data_top_path}\20250704T045315Z-1-001\2024-05-09_avg10min"  # 資料夾路徑請自行更換
target_file = "2024-05-01_lv2.nc"  # 測試讀第一筆

day = target_file[:10]
print(day)

file_path = os.path.join(data_folder, target_file)

## === 讀取netCDF資料 ===
ds = xr.open_dataset(file_path)
# print(ds)


## === 讀資料 ===
ds = xr.open_dataset(file_path)

time = ds['times'].values
ps = ds['Ps'].values  # 地面氣壓 hPa
rain_flag = ds['FLG_RAIN'].values  # 降雨旗標
# print(time)
## === 畫圖 ===
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(time, ps, 'r-', label='MWR-P')

## 找出降雨區間
rain_flag = np.array(rain_flag)
rain_diff = np.diff(rain_flag, prepend=0)

## 降雨開始、結束的 index
start_idx = np.where(rain_diff == 1)[0]
end_idx = np.where(rain_diff == -1)[0]

## 處理邊界：若最後持續降雨
if len(end_idx) < len(start_idx):
    end_idx = np.append(end_idx, len(rain_flag)-1)

## 畫完整降雨區間
for s, e in zip(start_idx, end_idx):
    ax.axvspan(time[s] - np.timedelta64(5, 'm'), time[e] + np.timedelta64(5, 'm'),
               color='gray', alpha=0.3, edgecolor='none')

## 格式設定
ax.set_ylabel('Pressure [hPa]')
# ax.set_xlabel('Time [UTC]')
ax.grid()
ax.legend()
ax.set_title(day)

## 時間軸美化
ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%HZ'))
fig.autofmt_xdate()
## 這行移除頭尾空白
ax.set_xlim(time.min(), time.max())

plt.show()