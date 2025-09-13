import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import numpy as np
from matplotlib import patheffects as path_effects  # 文字白描邊用
from tqdm import tqdm


## ============================== 共同參數 ============================== ##
start_time_str = "2025-08-15 06:00:00"  # 繪圖起始（含）
end_time_str   = "2025-08-18 06:00:00"  # 繪圖結束（含）
temp_min, temp_max = 24, 45             # 色階上下限（溫度）
data_top_path = r"C:/Users/steve/python_data/2025DAAN_park"
base_folder = rf"{data_top_path}\20250815-0818觀測坪"  # #1～#7 子資料夾都在這底下
output_folder_path = rf"{data_top_path}\TemperatureMinuteMaps"  # 每分鐘輸出的圖檔資料夾
os.makedirs(output_folder_path, exist_ok=True)

## 背景圖設定（單張底圖；使用像素座標）
bg_image_path_str = r"C:\Users\steve\python_data\2025DAAN_park\圖片\IMG_6290.jpg"  # TODO: 換成你的底圖路徑

## 7 個測站在背景圖上的像素座標（(x, y)，原點左上；與 imshow(origin='upper') 一致）
sensor_pos_dict = {  # TODO: 依你的底圖像素座標填好
    "#1": (2262,2404),
    "#2": (3445,1726),
    "#3": (3286,1320),
    "#4": (3514,1099),
    "#5": (2414,937),
    "#6": (1935,1208),
    "#7": (459, 1958),
}

## 顏色與標記大小
cmap_name_str = "viridis"               # 需要改色盤再告訴我
norm_for_temp = Normalize(vmin=temp_min, vmax=temp_max)
dot_size_int = 900
tag_fontsize_int = 10

## ============================== 資料處理 ============================== ##
def build_minute_temperature_for_1to7():
    """
    讀取 #1～#7 每站所有 CSV 檔案，取出 Time(第5欄索引4) 與 Temp(第2欄索引1)，
    依照 5 分鐘（center=True）平滑後，再以 1 分鐘頻率取樣。
    回傳：
        tag_minute_df_dict = {
            '#1': DataFrame(['DateTime','Temp']),
            ...,
            '#7': DataFrame(['DateTime','Temp'])
        }
    """
    ## 完整時間表（每 2 秒）
    full_time_df = pd.DataFrame({'DateTime': pd.date_range(start=start_time_str, end=end_time_str, freq='2s')})

    tag_minute_df_dict = {}  # #i -> 分鐘資料
    for i in range(1, 8):
        tag_str = f"#{i}"
        csv_folder_path = os.path.join(base_folder, tag_str)
        all_files_list = sorted(glob.glob(os.path.join(csv_folder_path, "*.csv")))

        if not all_files_list:
            print(f"{tag_str}: 找不到 CSV 檔案，略過")
            continue

        df_list = []
        for file_path in tqdm(all_files_list,desc=f'{i}號測站資料處理中...'):
            ## 單檔：讀取 Temp(索引1) + Time(索引4)
            data_df = pd.read_csv(
                file_path,
                header=None,
                usecols=[1, 4],
                dtype={4: str},         # Time 以字串讀入
                engine='python',
                on_bad_lines='skip'
            )
            data_df.columns = ['Temp', 'Time']  # 你既有命名

            ## 轉 datetime
            data_df['DateTime'] = pd.to_datetime(data_df['Time'], format='%Y%m%d%H%M%S', errors='coerce')
            data_df = data_df[['DateTime', 'Temp']]
            df_list.append(data_df)

        if not df_list:
            print(f"{tag_str}: 沒有可用資料，略過")
            continue

        merged_data_df = pd.concat(df_list, ignore_index=True)
        ## 與完整時間表合併（左合併，確保 2 秒頻率）
        merged_data_df = pd.merge(full_time_df, merged_data_df, on='DateTime', how='left')
        merged_data_df['Temp'] = pd.to_numeric(merged_data_df['Temp'], errors='coerce').astype(float)

        ## 5 分鐘 centered 平滑 + 1 分鐘取樣
        merged_data_df = merged_data_df.sort_values('DateTime').set_index('DateTime')
        smooth_series = merged_data_df['Temp'].rolling('5min', center=True, min_periods=1).mean()  # 5min 視窗
        minute_df = smooth_series.resample('1min').mean().to_frame(name='Temp').reset_index()

        ## 限制時間範圍（避免畫到設定外）
        mask = (minute_df['DateTime'] >= pd.Timestamp(start_time_str)) & (minute_df['DateTime'] <= pd.Timestamp(end_time_str))
        minute_df = minute_df.loc[mask].copy()

        tag_minute_df_dict[tag_str] = minute_df

    return tag_minute_df_dict

## ============================== 每分鐘繪圖 ============================== ##
def draw_minute_maps_for_1to7(tag_minute_df_dict):
    """
    以 tag_minute_df_dict（鍵 '#1'~'#7'）為輸入，
    在背景圖上逐分鐘畫七個固定點的溫度著色。
    每張圖輸出到 output_folder_path。
    """
    ## 建立分鐘時間軸（含兩端）
    minute_time_index = pd.date_range(start=start_time_str, end=end_time_str, freq='1min')

    ## 讀背景圖
    if not os.path.exists(bg_image_path_str):
        raise FileNotFoundError(f"找不到背景圖：{bg_image_path_str}")
    bg_img = plt.imread(bg_image_path_str)

    for curr_ts in tqdm(minute_time_index,desc='繪圖中..'):
        fig = plt.figure(figsize=(8, 6))
        ax = plt.gca()
        ax.imshow(bg_img, origin='upper')  # 以影像像素座標顯示
        ax.set_axis_off()

        point_x_list, point_y_list, point_temp_list, point_tag_list = [], [], [], []

        ## 蒐集七點此分鐘的值
        for tag in ["#1", "#2", "#3", "#4", "#5", "#6", "#7"]:
            minute_df = tag_minute_df_dict.get(tag, None)
            if minute_df is None:
                continue
            row = minute_df.loc[minute_df['DateTime'] == curr_ts]
            if row.empty:
                continue
            temp_value = row.iloc[0]['Temp']
            if pd.isna(temp_value):
                continue
            if tag not in sensor_pos_dict:
                continue
            x_pix, y_pix = sensor_pos_dict[tag]
            point_x_list.append(x_pix)
            point_y_list.append(y_pix)
            point_temp_list.append(float(temp_value))
            point_tag_list.append(tag)

        ## 畫散點（以溫度上色）
        if len(point_x_list) > 0:
            sc = ax.scatter(point_x_list, point_y_list, c=point_temp_list,
                            s=dot_size_int, cmap=cmap_name_str, norm=norm_for_temp,
                            edgecolors='k', linewidths=0.8)

            ## 在點旁標註測站編號
            for (xv, yv, tg) in zip(point_x_list, point_y_list, point_tag_list):
                ax.text(xv, yv+150, tg, ha='center', va='top', fontsize=tag_fontsize_int,
                        color='black',
                        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.6))  # 小白底易讀
                    ## 畫散點（以溫度上色）
            if len(point_x_list) > 0:
                sc = ax.scatter(point_x_list, point_y_list, c=point_temp_list,
                                s=dot_size_int, cmap=cmap_name_str, norm=norm_for_temp,
                                edgecolors='k', linewidths=0.8)

                ## 在點旁標註測站編號（你原本就有）
                for (xv, yv, tg) in zip(point_x_list, point_y_list, point_tag_list):
                    ax.text(xv, yv+150, tg, ha='center', va='top', fontsize=tag_fontsize_int,
                            color='black',
                            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.6))  # 小白底易讀

                ## === 在圓點正中心標示「白外框黑字」的溫度 === ##
                for (xv, yv, tv) in zip(point_x_list, point_y_list, point_temp_list):
                    txt = ax.text(xv, yv, f"{tv:.1f}", ha='center', va='center',
                                fontsize=10, color='black')  # 置中對齊
                    txt.set_path_effects([
                        path_effects.withStroke(linewidth=3, foreground='white')  # 白色外框
                    ])

            ## colorbar（使用 temp_min~temp_max）
            cbar = plt.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label("°C")

        ## 標題：YYYY-mm-dd HH:MM
        plt.title(curr_ts.strftime("%Y-%m-%d %H:%M")+' [°C]')
        plt.tight_layout()

        ## 檔名
        save_name_str = curr_ts.strftime("%Y%m%d_%H%M") + "_Temp_1-7.png"
        minute_plot_save_path_str = os.path.join(output_folder_path, save_name_str)
        # plt.show()
        plt.savefig(minute_plot_save_path_str, dpi=150)
        plt.close(fig)

## ============================== 主流程 ============================== ##
def main():
    ## 讀檔 + 平滑 + 取 1 分鐘
    tag_minute_df_dict = build_minute_temperature_for_1to7()
    if not tag_minute_df_dict:
        print("沒有任何感測器的分鐘資料，結束。")
        return

    ## 每分鐘出圖
    draw_minute_maps_for_1to7(tag_minute_df_dict)

if __name__ == "__main__":
    main()
