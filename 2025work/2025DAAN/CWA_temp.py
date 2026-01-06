import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import glob
import re

## === 路徑設定 ===
cwa_folder_path = r"C:\Users\steve\python_data\2025DAAN_park\20250815-0818CWA"
data_top_path   = r"/home/steven/python_data/2025DAAN_park"

## === 讀取當天 CWA 分鐘溫度（MN） ===
def read_cwa_temp_for_day(cwa_file_path_str):
    cwa_data_df = pd.read_csv(cwa_file_path_str, header=None, encoding="utf-8", on_bad_lines="skip")
    cwa_data_df = cwa_data_df[cwa_data_df[2] == "MN"][[3, 7]].copy()
    cwa_data_df.columns = ["Time", "CWA_Temp"]
    cwa_data_df["DateTime"] = pd.to_datetime(cwa_data_df["Time"], format="%Y%m%d%H%M", errors="coerce")
    cwa_data_df = cwa_data_df[["DateTime", "CWA_Temp"]].dropna()
    return cwa_data_df

## === 畫 CWA 溫度日圖（原始 + 5 分鐘 smooth） ===
def plot_cwa_daily_with_smooth():
    cwa_files_list = sorted(glob.glob(os.path.join(cwa_folder_path, "*.txt")))
    output_folder_path = rf"{data_top_path}\CWA_Temp_smooth5min"
    os.makedirs(output_folder_path, exist_ok=True)

    for cwa_file_path_str in cwa_files_list:
        basename_str = os.path.basename(cwa_file_path_str)
        m = re.search(r"(\d{8})", basename_str)
        if not m:
            continue
        day_str = m.group(1)                             # e.g. '20250815'
        day_start_ts = pd.to_datetime(day_str)
        day_end_ts = day_start_ts + pd.Timedelta(days=1) - pd.Timedelta(minutes=1)

        ## 讀 CWA
        cwa_day_df = read_cwa_temp_for_day(cwa_file_path_str)
        if cwa_day_df.empty:
            print(f"{day_str}: CWA 無資料，略過")
            continue

        ## 5 分鐘 centered 平滑
        cwa_day_df = cwa_day_df.set_index("DateTime").sort_index()
        cwa_day_df["Smooth5min"] = cwa_day_df["CWA_Temp"].rolling("5min", center=True, min_periods=1).mean()
        cwa_day_df = cwa_day_df.reset_index()

        ## 繪圖
        plt.figure(figsize=(14, 7))
        ax = plt.gca()
        ax.plot(cwa_day_df["DateTime"], cwa_day_df["CWA_Temp"], color="gray", alpha=0.5, label="CWA Temp (1min raw)")
        ax.plot(cwa_day_df["DateTime"], cwa_day_df["Smooth5min"], color="red", linewidth=2, label="CWA Temp (5min smooth)")

        ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
        ax.set_xlim(day_start_ts, day_end_ts)

        plt.xlabel("Time")
        plt.ylabel("Temperature (°C)")
        plt.title(f"{day_start_ts.strftime('%Y-%m-%d')} CWA Temperature (MN, 5min smooth)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        save_path_str = rf"{output_folder_path}\result\{day_str}_CWA_Temp_smooth5min.png"
        plt.savefig(save_path_str)
        plt.close()
        print(f"已輸出: {save_path_str}")

## === 執行 ===
plot_cwa_daily_with_smooth()
