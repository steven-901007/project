import os, re, glob
import pandas as pd
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

## ============================== 參數設定 ============================== ##
year = "2021"
month = "05"
day = "24"

pid = 'park' #park or way(魏) 使用哪個PID
station = 'RCWF'

start_time_str = "04:00:00"   # 起始時間    
end_time_str   = "08:00:00"   # 結束時間

data_top_path = "/home/steven/python_data/radar"
data_folder_path = rf"{data_top_path}/PID_square/{year}{month}{day}/csv"
height_col_name_str   = 'Height_Index'  # 高度欄位名稱
start_time_dt = datetime.strptime(f"{year}-{month}-{day} {start_time_str}", "%Y-%m-%d %H:%M:%S")
end_time_dt   = datetime.strptime(f"{year}-{month}-{day} {end_time_str}", "%Y-%m-%d %H:%M:%S")


def _parse_time_from_filename_str(fname_str):
    """從檔名前 14 碼抓 YYYYmmddHHMMSS → datetime"""
    m = re.search(r"(\d{14})", os.path.basename(fname_str))
    if not m:
        return None
    return datetime.strptime(m.group(1), "%Y%m%d%H%M%S")

## ============================== 只讀時間範圍內檔案 ============================== ##
all_csv_files = sorted(glob.glob(os.path.join(data_folder_path, f"*{station}_{pid}.csv")))

csv_path_list = []
for fp in all_csv_files:

    t = _parse_time_from_filename_str(fp)
    if t is not None and start_time_dt <= t <= end_time_dt:
        csv_path_list.append(fp)
        # print(fp)

if not csv_path_list:
    raise SystemExit("⚠️ 沒有符合時間範圍的 CSV 檔案！")


for variable_col_name_str in ['DS', 'WS', 'CR', 'GR', 'BD', 'RA', 'HR', 'RH']:
    # ## ============================== 合併所有資料 ============================== ##
    records_df = pd.DataFrame()
    ic_flash_count_df  = pd.DataFrame()
    cg_flash_count_df  = pd.DataFrame()

    for fp in csv_path_list:
        # print(fp)
        flash_path = fp.replace('/csv/', '/flash_in_box/').replace(f'{pid}.csv', 'flash_in_box.csv')
        # print(flash_path)

        time_dt = _parse_time_from_filename_str(fp) + timedelta(hours=8)  # 轉成 LCT 
        time_str = time_dt.strftime("%H:%M:%S") # 只取時間部分當欄位名稱


        try:
            one_df = pd.read_csv(fp)
            one_flash_df = pd.read_csv(flash_path)
            # print(one_df)
        except Exception as e:
            print(f"讀檔失敗略過: {fp} -> {e}")
            continue

        # 檢查欄位
        for k in [height_col_name_str, variable_col_name_str]:
            if k not in one_df.columns:
                print(f"⚠️ 檔案缺欄位，略過：{fp}")
                break
        else:
            need_df = one_df[[height_col_name_str, variable_col_name_str]].copy()
            need_df = need_df.rename(columns={variable_col_name_str: time_str})
            need_df = need_df.set_index(height_col_name_str)  # 高度當 index，合併時才會對齊

            # print(need_df)
            records_df = pd.concat([records_df,need_df], axis=1)
        
        ##閃電資料讀取
        # print(one_flash_df)
        ic_flash_count = int(one_flash_df[one_flash_df['lightning_type'] == 'IC']['minute_offset'].count())
        cg_flash_count = int(one_flash_df[one_flash_df['lightning_type'] == 'CG']['minute_offset'].count())
        print(one_flash_df)
        print(f"時間 {time_str} 閃電數量: IC={ic_flash_count}, CG={cg_flash_count}")
        ic_flash_count_df = pd.concat([ic_flash_count_df, pd.DataFrame({time_str: [ic_flash_count]})], axis=1)
        cg_flash_count_df = pd.concat([cg_flash_count_df, pd.DataFrame({time_str: [cg_flash_count]})], axis=1)

    # print(records_df)


    if records_df.empty == True:
        raise SystemExit("⚠️ 符合時間範圍的檔案無有效資料，請檢查欄位名稱。")
    # print(flash_count_df)
    # print(records_df)


    df_t = records_df.T
    df_t.index = pd.to_datetime(df_t.index, format="%H:%M:%S")
    print(df_t)

    ic_flash_df_t = ic_flash_count_df.T
    cg_flash_df_t = cg_flash_count_df.T
    ic_flash_df_t.index = pd.to_datetime(ic_flash_df_t.index, format="%H:%M:%S")
    cg_flash_df_t.index = pd.to_datetime(cg_flash_df_t.index, format="%H:%M:%S")
    # print(flash_df_t)

    # 設定高度（每層 500 m）
    heights = records_df.index.astype(int) * 0.5  # 0, 500, 1000, ..., 10000
    print(heights)

    temp_data_path = f"{data_top_path}/Temp/{year}{month}99.upair.txt"
    column_names_list = ['stno', 'yyyymmddhh', 'Si', 'Press', 'Heigh', 'Tx', 'Td', 'Wd', 'Ws', 'RH']
    df_observation_data = pd.read_csv(
        temp_data_path, 
        sep=r'\s+', 
        skiprows=14, 
        names=column_names_list,
        dtype={'stno': str, 'yyyymmddhh': str}
    )

    # ============================== 取得對應高度的溫度 ============================== #
    # 1. 篩選特定時間的探空資料並轉為數值 (處理原本讀取時可能產生的字串問題)
    df_sub = df_observation_data[df_observation_data['yyyymmddhh'] == f"{year}{month}{day}00"].copy()
    df_sub['Heigh'] = pd.to_numeric(df_sub['Heigh'], errors='coerce')
    df_sub['Tx'] = pd.to_numeric(df_sub['Tx'], errors='coerce')
    df_sub = df_sub.dropna(subset=['Heigh', 'Tx']).sort_values('Heigh') # 確保排序以利內插

    # 2. 使用線性內插找出對應雷達高度的溫度
    # heights 是 km，需乘以 1000 轉換為公尺 (m) 以對齊探空資料
    temp_at_heights = np.interp(heights * 1000, df_sub['Heigh'], df_sub['Tx'])

    # 顯示結果 (高度 km : 溫度 °C)
    df_temp_result = pd.DataFrame({'Altitude_km': heights, 'Temp_C': temp_at_heights})
    print(df_temp_result)

    # # ============================== [修改] 根據溫度篩選資料 ============================== #
    # # 建立遮罩：找出溫度 > 12 或 < -20 的位置
    # invalid_temp_mask = (temp_at_heights > 12) | (temp_at_heights < -20)

    # # 將 df_t 中對應這些高度的欄位設為 0
    # # df_t 的 columns 對應 heights 的順序，因此可以直接使用 boolean mask 進行 iloc 篩選
    # df_t.iloc[:, invalid_temp_mask] = 0

    # print("⚠️ 已將溫度 > 12°C 或 < -20°C 的資料設為 0")
    # ================================================================================= #



    ## ============================== 繪製熱圖 ============================== ##
    fig, ax = plt.subplots(figsize=(16, 6))


    # 把欄名的 "HH:MM:SS" 全部補上同一天日期，統一成 2021-05-30 的 LCT datetime
    # df_t.index = [t for t in df_t.index]  # 保留原樣


    im = ax.imshow(
        df_t.T,                      # 資料要轉置成 [高度, 時間]
        aspect='auto',              # 自動調整比例
        origin='lower',             # 高度從下往上
        cmap='inferno',               # 熱圖配色
        extent=[                    # 設定 X 軸時間與 Y 軸高度範圍
            mdates.date2num(df_t.index[0]),
            mdates.date2num(df_t.index[-1]),
            heights[0],
            heights[-1]
        ]
    )

    # ## ============================== 加入閃電數量折線圖 ============================== ##
    # # 轉成同一天的 datetime（與 df_t.index 一致的時間軸）



    ax2 = ax.twinx()
    ax2.plot(ic_flash_df_t, linewidth=5,c = 'white')
    ax2.plot(ic_flash_df_t, linewidth=1.8,c = 'r', label="IC")
    ax2.plot(cg_flash_df_t, linewidth=5,c = 'white')
    ax2.plot(cg_flash_df_t, linewidth=1.8,c = 'b', label="CG")

    ax2.set_ylabel("Lightning Count")
    ax2.set_ylim(bottom=0)  # 讓下界從 0 開始（不改上界，交給 Matplotlib 自動）


    # 顯示摺線圖的圖例（放右上角）
    ax2.legend(loc="upper right",frameon=True)
    ## ============================== 格式美化 ============================== ##
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    plt.xticks(rotation=45)

    # ↓ 把 10 分鐘一格改成 30 分鐘（或用 AutoDateLocator 改成自動）
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=range(0, 60, 30)))
    # 若想自動： ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10))

    ax.set_ylabel("Altitude[km]")
    ax.set_yticks(np.arange(0, heights[-1]+1, 1))


    if variable_col_name_str == "DS":
        variavle_real_name = 'dry aggregated snow'
    elif variable_col_name_str == "WS":
        variavle_real_name = 'wet snow'
    elif variable_col_name_str == "CR":
        variavle_real_name = 'crystals of various orientations' 
    elif variable_col_name_str == "GR":
        variavle_real_name = 'graupel'
    elif variable_col_name_str == "BD":
        variavle_real_name = 'big drops'
    elif variable_col_name_str == "RA":
        variavle_real_name = 'light and moderate rain'
    elif variable_col_name_str == "HR":
        variavle_real_name = 'heavy rain'
    elif variable_col_name_str == "RH":
        variavle_real_name = 'rain and hail mixture'
    # 標題（同你原本）
    plt.title(f"{variavle_real_name} {year}/{month}/{day} {(datetime.strptime(start_time_str, '%H:%M:%S') + timedelta(hours=8)).strftime('%H:%M')} to {(datetime.strptime(end_time_str, '%H:%M:%S') + timedelta(hours=8)).strftime('%H:%M')} LST")

    # # # 色條調整 fraction/pad，縮小＋加右邊間距，避免壓到右軸
    # cbar = plt.colorbar(im, ax=ax, pad=0.04)
    # cbar.set_label("pixel")

    # 版面留更多右/下邊界，避免文字被裁切或互相重疊
    # plt.subplots_adjust(right=0.82, bottom=0.22)  # 右邊空出給右軸與圖例，下邊留給 X 標籤
    # plt.tight_layout()

    # 加入 colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("pixel")

    save_path = f"{data_top_path}/PID_square/{year}{month}{day}/{variable_col_name_str}_{year}-{month}-{day}_{start_time_str.replace(":", "-")}to{end_time_str.replace(":", "-")}_{pid}_{station}_heatmap.png"
    plt.savefig(save_path,bbox_inches='tight')
    print("✅", save_path)