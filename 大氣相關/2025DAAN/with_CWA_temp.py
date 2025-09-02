import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re

## === 共同參數（溫度專用） ===
start_time_str = "2025-08-15 06:00:00"
end_time_str   = "2025-08-18 06:00:00"
temp_min,temp_max = 24, 45  # y 範圍（若不要固定可註解掉）
xlim_start = pd.Timestamp("2025-08-15 06:00:00")
xlim_end   = pd.Timestamp("2025-08-18 06:00:00")

data_top_path = r"C:/Users/steve/python_data/2025DAAN_park"
base_folder   = rf"{data_top_path}\20250815-0818觀測坪"           # #1~#12 各自資料夾
cwa_folder    = rf"{data_top_path}\20250815-0818CWA"             # CWA txt（含日期）
output_folder = rf"{data_top_path}\Temperature_with_CWA"         # 輸出圖檔資料夾
os.makedirs(output_folder, exist_ok=True)

## 固定標籤與特殊修正
tags_all = [f"#{i}" for i in range(1, 13)]
target_basename_str = "109_2025_08_05_03.csv"  # 你的特殊修正檔名
old_time_str = '20250805031108'
new_time_str = '20250805031102'

## === 小工具：讀取 CWA 當日（MN）並做 5 分鐘 centered 平滑 ===
def read_cwa_smooth_5min_for_day(day_str):  # 回傳 DateTime, CWA_Smooth5min
    cwa_file = os.path.join(cwa_folder, f"{day_str}.txt")
    if not os.path.exists(cwa_file):
        return None
    cwa_df = pd.read_csv(cwa_file, header=None, encoding="utf-8", on_bad_lines="skip")
    cwa_df = cwa_df[cwa_df[2] == "MN"][[3, 7]].copy()
    cwa_df.columns = ["Time", "CWA_Temp"]
    cwa_df["DateTime"] = pd.to_datetime(cwa_df["Time"], format="%Y%m%d%H%M", errors="coerce")
    cwa_df = cwa_df[["DateTime", "CWA_Temp"]].dropna()
    if cwa_df.empty:
        return None
    cwa_df = cwa_df.set_index("DateTime").sort_index()
    cwa_df["CWA_Smooth5min"] = cwa_df["CWA_Temp"].rolling("5min", center=True, min_periods=1).mean()  # 5min centered
    return cwa_df.reset_index()[["DateTime", "CWA_Smooth5min"]]

## === 小工具：讀取某 tag 的 raw（2 秒）→ 5 分鐘 centered 平滑 → 1 分鐘 ===
def read_tag_smooth_1min(tag):  # 回傳整段期間的 1 分鐘資料（DateTime, Temp）
    csv_folder_path = os.path.join(base_folder, tag)
    all_files_list = sorted(glob.glob(os.path.join(csv_folder_path, "*.csv")))
    if not all_files_list:
        print(f"{tag}: 找不到 CSV，略過")
        return None

    df_list = []
    for file_path in all_files_list:
        data_df = pd.read_csv(
            file_path,
            header=None,
            usecols=[1, 4],           # Temp(索引1), Time(索引4)
            dtype={4: str},
            engine='python',
            on_bad_lines='skip'
        )
        data_df.columns = ['Temp', 'Time']  # 你的命名習慣

        ## #1 檔案第一筆時間修正（轉 datetime 前）
        if tag == "#1" and os.path.basename(file_path) == target_basename_str:
            if str(data_df.at[0, 'Time']) == old_time_str:
                data_df.at[0, 'Time'] = new_time_str

        data_df['DateTime'] = pd.to_datetime(data_df['Time'], format='%Y%m%d%H%M%S', errors='coerce')
        data_df = data_df[['DateTime', 'Temp']]
        df_list.append(data_df)

    if not df_list:
        return None

    merged_data_df = pd.concat(df_list, ignore_index=True)
    ## 與完整時間表合併（確保 2 秒頻率，避免缺秒造成 rolling 視窗不均）
    full_time_df = pd.DataFrame({'DateTime': pd.date_range(start=start_time_str, end=end_time_str, freq='2s')})
    merged_data_df = pd.merge(full_time_df, merged_data_df, on='DateTime', how='left')
    merged_data_df['Temp'] = pd.to_numeric(merged_data_df['Temp'], errors='coerce').astype(float)

    merged_data_df = merged_data_df.sort_values('DateTime').set_index('DateTime')
    smooth_series = merged_data_df['Temp'].rolling('5min', center=True, min_periods=1).mean()  # 5min centered
    minute_df = smooth_series.resample('1min').mean().to_frame(name='Temp').reset_index()      # 1min
    return minute_df  # DateTime, Temp

## === 預先讀入所有 tag 的 1 分鐘資料 ===
tag_minute_df_dict = {}  # {'#1': df, ...}
for tag in tags_all:
    minute_df = read_tag_smooth_1min(tag)
    if minute_df is not None:
        tag_minute_df_dict[tag] = minute_df

if not tag_minute_df_dict:
    raise RuntimeError("沒有任何測站的分鐘資料，無法作圖。")

## === 分日期作圖（一天一張）：所有測站 + CWA（紅色加粗） ===
date_range_df = pd.DataFrame({'DateTime': pd.date_range(start=start_time_str, end=end_time_str, freq='D')})
date_list = date_range_df['DateTime'].dt.normalize().unique()

for d in date_list:
    day_start = pd.Timestamp(d)
    day_end   = day_start + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

    ## 套用 xlim 的交集
    day_start = max(day_start, pd.Timestamp(xlim_start))
    day_end   = min(day_end,   pd.Timestamp(xlim_end))
    if day_start > day_end:
        continue

    ## 讀 CWA 當日（5min smooth）
    day_str = day_start.strftime("%Y%m%d")
    cwa_smooth_df = read_cwa_smooth_5min_for_day(day_str)
    if cwa_smooth_df is None or cwa_smooth_df.empty:
        print(f"{day_str}: 找不到 CWA 或無資料，略過此日")
        continue

    plt.figure(figsize=(14, 7))
    ax = plt.gca()
    has_any = False

    ## 畫所有測站
    for tag, minute_df in tag_minute_df_dict.items():
        mask = (minute_df['DateTime'] >= day_start) & (minute_df['DateTime'] <= day_end)
        sub_df = minute_df.loc[mask]
        if not sub_df.empty:
            ax.plot(sub_df['DateTime'], sub_df['Temp'], label=f'{tag}')  # 各站
            has_any = True

    ## 畫 CWA（紅色加粗）
    cwa_mask = (cwa_smooth_df['DateTime'] >= day_start) & (cwa_smooth_df['DateTime'] <= day_end)
    cwa_sub = cwa_smooth_df.loc[cwa_mask]
    if not cwa_sub.empty:
        ax.plot(cwa_sub['DateTime'], cwa_sub['CWA_Smooth5min'], linewidth=2.5, color='red', label='CWA (5min smooth)')

    if not has_any and cwa_sub.empty:
        plt.close()
        continue

    ## X 軸：每天固定 00/06/12/18
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    ax.set_xlim(day_start, day_end)

    ## y 範圍（若不想固定可註解掉）
    # ax.set_ylim(temp_min, temp_max)

    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.title(f'{day_start.strftime("%Y-%m-%d")} Temperature (ALL stations + CWA)')
    plt.grid(True)
    plt.legend(ncol=2)
    plt.tight_layout()

    save_path = rf"{output_folder}/{day_start.strftime('%Y%m%d')}_ALL_with_CWA.png"
    plt.savefig(save_path)
    plt.close()
    print(f"已輸出: {save_path}")
