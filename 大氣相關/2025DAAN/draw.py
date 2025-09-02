import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re

## === 共同參數 ===
start_time_str = "2025-08-15 06:00:00"
end_time_str   = "2025-08-18 06:00:00"
temp_min,temp_max = 24, 45
# 顯示範圍
xlim_start = pd.Timestamp("2025-08-15 06:00:00")
xlim_end   = pd.Timestamp("2025-08-18 06:00:00")
data_top_path = r"C:/Users/steve/python_data/2025DAAN_park"
base_folder = rf"{data_top_path}\20250815-0818觀測坪"

year_month = '2025/08/15~18'

tg = '1-7'            # 1-7 or 8-11 or 12 or all
col = 1                # 溫度=1；光照=9（第10欄，含 $）


def draw(tg,col):

    ## 依資料欄位選擇名稱/單位
    if col == 1:
        datatype = {4: 'string'}        # Time 以字串讀，後面再 to_datetime
        name = 'Temp'                   # y 欄名
        long_name = 'Temperature'
        y_unit = '°C'
    elif col == 9:
        datatype = {4: 'string'}
        name = 'Lux'                    # 改成 Lux
        long_name = 'Illuminance'
        y_unit = 'lux'
    else:
        raise ValueError("目前僅支援 col=1(Temp) 或 col=9(Lux)")

    ## 完整時間表（每 2 秒）
    full_time_df = pd.DataFrame({'DateTime': pd.date_range(start=start_time_str, end=end_time_str, freq='2s')})

    ## #1 特殊修正
    target_basename_str = "109_2025_08_05_03.csv"
    old_time_str = '20250805031108'
    new_time_str = '20250805031102'

    plt.figure(figsize=(14, 7))

    ## 要畫哪些測站
    if tg == '1-7':
        data_range = range(1, 8)
        pic_name = '#1~#7'
    elif tg == '8-11':
        data_range = range(8, 12)
        pic_name = '#8~#11'
    elif tg == '12':
        data_range = [12]
        pic_name = '#12'
    elif tg == 'all':
        data_range = range(1, 13)
        pic_name = '#1~#12'
    else:
        raise ValueError("tg 只能是 '1-7'、'8-11' 、 '12' 或 'all'")


    ## 依序處理
    for tag in [f"#{i}" for i in data_range]:
        csv_folder_path = os.path.join(base_folder, tag)
        all_files_list = sorted(glob.glob(os.path.join(csv_folder_path, "*.csv")))
        print(tag)
        if not all_files_list:
            print(f"{tag}: 找不到 CSV 檔案，略過")
            continue

        df_list = []
        for file_path in all_files_list:
            # === 讀檔 ===
            if col == 9:
                # 讀 Time(索引4) + 第10欄(索引9，可能含 $)
                data_df = pd.read_csv(
                    file_path,
                    header=None,
                    usecols=[4, 9],
                    dtype={4: 'string'},  # Time 先以字串
                    converters={
                        9: lambda x: pd.to_numeric(re.sub(r'[^0-9.\-]', '', str(x)), errors='coerce')
                    },
                    engine='python',
                    on_bad_lines='skip'
                )
                # ★ 重新命名
                data_df.columns = ['Time', name]
            elif col == 1:
                # 讀 Time(索引4) + Temp(索引1)
                data_df = pd.read_csv(
                    file_path,
                    header=None,
                    usecols=[1, 4],
                    dtype={4: str},
                    engine='python',        # 比較寬鬆，遇到不規則分隔較穩
                    on_bad_lines='skip'     # 有壞行就跳過，避免整檔報錯
                )
            # ★ 重新命名（這行是你缺的）
                data_df.columns = [name, 'Time']


            # #1 檔案第一筆時間修正（轉 datetime 前）
            if tag == "#1" and os.path.basename(file_path) == target_basename_str:
                if str(data_df.at[0, 'Time']) == old_time_str:
                    data_df.at[0, 'Time'] = new_time_str

            # 轉成 datetime
            data_df['DateTime'] = pd.to_datetime(data_df['Time'], format='%Y%m%d%H%M%S', errors='coerce')

            # 只保留需要欄位
            data_df = data_df[['DateTime', name]]
            df_list.append(data_df)


        merged_data_df = pd.concat(df_list, ignore_index=True)

        # 與完整時間表合併（左合併）
        final_df = pd.merge(full_time_df, merged_data_df, on='DateTime', how='left')
        # 將 Y 欄位轉為 float，將 pd.NA 轉為 np.nan，避免 Matplotlib 出錯
        final_df[name] = pd.to_numeric(final_df[name], errors='coerce').astype(float)

        # 畫到同一張
        plt.plot(final_df['DateTime'], final_df[name], label=f'{tag}')


    ## X 軸：每天 00/06/12/18
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 6, 12, 18]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %H:%M'))
    plt.xticks(rotation=45)

    # 顯示範圍
    # xlim_start = pd.Timestamp('2025-08-05 00:00:00')
    # xlim_end   = pd.Timestamp('2025-08-08 20:00:00')
    ax.set_xlim(xlim_start, xlim_end)

    # y 範圍：只在畫溫度時限定，畫光照則讓它自動
    if col == 1 and tg != '12':
        ax.set_ylim(temp_min,temp_max)


    plt.xlabel('Time')
    plt.ylabel(f'{long_name} ({y_unit})')
    plt.title(f'{year_month} {long_name} ({pic_name})')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    save_name = base_folder.split('/')[-1].split('\\')[-1]
    output_folder = rf"{data_top_path}\{long_name}"
    os.makedirs(output_folder, exist_ok=True)
    save_path = rf"{output_folder}/{save_name}_{tg}.png"
    plt.savefig(save_path)
    plt.show()


# for col in [1,9]:
#     for tg in ['1-7','8-11','12']:
#         draw(tg,col)
for col in [9]:
    tg = 'all'
    draw(tg,col)