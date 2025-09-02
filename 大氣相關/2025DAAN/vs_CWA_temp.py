import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import glob
import re

## === 路徑設定 ===
cwa_folder_path = r"C:\Users\steve\python_data\2025DAAN_park\20250815-0818CWA"
base_folder_path = r"C:\Users\steve\python_data\2025DAAN_park\20250815-0818觀測坪"
data_top_path    = r"C:\Users\steve\python_data\2025DAAN_park"

## === 參數 ===
tags_all_list = [f"#{i}" for i in range(1, 13)]  # #1 ~ #12
target_basename_str = "109_2025_08_05_03.csv"     # 你的特殊修正檔名
old_time_str = '20250805031108'
new_time_str = '20250805031102'

## === 讀取當天 CWA 分鐘溫度（MN） ===
def read_cwa_temp_for_day(cwa_file_path_str):  # 回傳當天 CWA 每分鐘資料
    cwa_data_df = pd.read_csv(cwa_file_path_str, header=None, encoding="utf-8", on_bad_lines="skip")
    cwa_data_df = cwa_data_df[cwa_data_df[2] == "MN"][[3, 7]].copy()
    cwa_data_df.columns = ["Time", "CWA_Temp"]
    cwa_data_df["DateTime"] = pd.to_datetime(cwa_data_df["Time"], format="%Y%m%d%H%M", errors="coerce")
    cwa_data_df = cwa_data_df[["DateTime", "CWA_Temp"]].dropna()
    return cwa_data_df

## === 讀某天某儀器 raw（2 秒）→ 每分鐘平均（不做平滑） ===
def read_tag_minute_avg_for_day(tag_str, day_str):  # 回傳當天每分鐘平均溫度 df
    csv_folder_path_str = os.path.join(base_folder_path, tag_str)
    all_files_list = sorted(glob.glob(os.path.join(csv_folder_path_str, "*.csv")))
    if not all_files_list:
        print(f"{tag_str}: 找不到 CSV，略過")
        return None

    tag_daily_list = []  # raw 當天資料
    for file_path_str in all_files_list:
        data_raw_df = pd.read_csv(
            file_path_str,
            header=None,
            usecols=[1, 4],      # Temp(索引1), Time(索引4)
            dtype={4: str},
            engine="python",
            on_bad_lines="skip"
        )
        data_raw_df.columns = ["Temp", "Time"]  # 依你的習慣

        ## #1 特殊修正（只針對該檔、該 tag）
        if tag_str == "#1" and os.path.basename(file_path_str) == target_basename_str:
            if str(data_raw_df.at[0, 'Time']) == old_time_str:
                data_raw_df.at[0, 'Time'] = new_time_str

        data_raw_df["DateTime"] = pd.to_datetime(data_raw_df["Time"], format="%Y%m%d%H%M%S", errors="coerce")

        # 只取指定日期
        mask_bool = data_raw_df["DateTime"].dt.strftime("%Y%m%d") == day_str
        data_raw_df = data_raw_df.loc[mask_bool, ["DateTime", "Temp"]]

        if not data_raw_df.empty:
            tag_daily_list.append(data_raw_df)

    if not tag_daily_list:
        return None

    merged_tag_df = pd.concat(tag_daily_list, ignore_index=True)
    merged_tag_df = merged_tag_df.set_index("DateTime").sort_index()

    ## 不做 smooth：直接以 1 分鐘頻率取平均
    minute_avg_df = merged_tag_df["Temp"].resample("1min").mean().to_frame("Minute_Avg_Temp").reset_index()
    return minute_avg_df  # 每分鐘一筆（該 tag）

## === 主流程：每天對應 CWA 與 all(#1~#12) raw→1min 的差值，單圖顯示所有 tag ===
def compare_daily_all_tags():
    cwa_files_list = sorted(glob.glob(os.path.join(cwa_folder_path, "*.txt")))
    output_folder_path = rf"{data_top_path}\Temp_Diff_vs_CWA_raw2s_to_1min\all"
    os.makedirs(output_folder_path, exist_ok=True)

    for cwa_file_path_str in cwa_files_list:
        basename_str = os.path.basename(cwa_file_path_str)
        m = re.search(r"(\d{8})", basename_str)
        if not m:
            continue
        day_str = m.group(1)                             # e.g. '20250815'
        day_start_ts = pd.to_datetime(day_str)
        day_end_ts = day_start_ts + pd.Timedelta(days=1) - pd.Timedelta(minutes=1)

        ## 讀 CWA（當天）
        cwa_day_df = read_cwa_temp_for_day(cwa_file_path_str)
        if cwa_day_df.empty:
            print(f"{day_str}: CWA 無資料，略過")
            continue

        ## 蒐集各 tag 的差值曲線
        has_any_tag_bool = False
        plt.figure(figsize=(14, 7))
        ax = plt.gca()

        for tag_str in tags_all_list:
            tag_minute_df = read_tag_minute_avg_for_day(tag_str, day_str)
            if tag_minute_df is None or tag_minute_df.empty:
                continue

            merged_df = pd.merge(tag_minute_df, cwa_day_df, on="DateTime", how="inner")
            if merged_df.empty:
                continue

            merged_df["Diff"] = merged_df["Minute_Avg_Temp"] - merged_df["CWA_Temp"]
            ax.plot(merged_df["DateTime"], merged_df["Diff"], label=f"{tag_str} − CWA")
            has_any_tag_bool = True

        if not has_any_tag_bool:
            plt.close()
            print(f"{day_str}: 所有 tag 與 CWA 都無可用重疊資料，略過")
            continue

        ## 圖面設定
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
        ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
        ax.set_xlim(day_start_ts, day_end_ts)
        plt.xlabel("Time")
        plt.ylabel("ΔTemperature (°C)")
        plt.title(f"{day_start_ts.strftime('%Y-%m-%d')} ΔTemperature vs CWA ")
        plt.grid(True)
        plt.legend(ncol=2)  # 12 支儀器，兩欄比較不擠
        plt.tight_layout()

        save_path_str = rf"{output_folder_path}\{day_str}_ALL_vs_CWA_raw2s_to_1min.png"
        plt.savefig(save_path_str)
        plt.close()
        print(f"已輸出: {save_path_str}")

## === 執行 ===
compare_daily_all_tags()
