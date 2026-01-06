# -*- coding: utf-8 -*-
"""
繪製2025/07/28~2025/08/04 嘉義、台南閃電分布
每小時一張圖
主圖：該小時的閃電分布
上方 inset：當天 IC / CG 每小時閃電總數（X 軸為當地時間小時 H）
"""

import os
import pandas as pd
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from matplotlib.font_manager import FontProperties
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

## ============================== 路徑設定 ============================== ##
data_top_path = r"/home/steven/python_data/2025CWA_flash_plan"
flash_data_path = f"{data_top_path}/raw_data/flash/CWA/2025_0701-0811.csv"
county_shp_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
result_folder_path = f"{data_top_path}/result/one_hour_one_pic/"
os.makedirs(result_folder_path, exist_ok=True)

## ============================== 中文字型設定 ============================== ##
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=15)
leg_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=30)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=24)

## ============================== 參數設定 ============================== ##
start_lct_dt = pd.Timestamp(2025, 7, 28, 0, 0, 0, tz='Asia/Taipei')
end_lct_dt   = pd.Timestamp(2025, 8, 4, 23, 59, 59, tz='Asia/Taipei')

## ============================== 讀取與處理 ============================== ##
flash_data_df = pd.read_csv(flash_data_path)
flash_data_df['time'] = pd.to_datetime(flash_data_df['Epoch Time'], utc=True)
flash_data_df['lat'] = flash_data_df['Latitude']
flash_data_df['lon'] = flash_data_df['Longitude']
flash_data_df['type'] = flash_data_df['Cloud or Ground']
flash_data_df['time_lct'] = flash_data_df['time'].dt.tz_convert('Asia/Taipei')
# print(flash_data_df)
# 篩時間
mask_time = (flash_data_df['time_lct'] >= start_lct_dt) & (flash_data_df['time_lct'] <= end_lct_dt)
flash_data_df = flash_data_df.loc[mask_time].copy()
print(f"篩選後筆數: {len(flash_data_df)}")

## ============================== 繪圖相關函式 ============================== ##
def _draw_base_map(ax):
    county_shp_reader = Reader(county_shp_path)
    county_records = county_shp_reader.records()

    for record in county_records:
        props = record.attributes
        name = props.get('COUNTYNAME', props.get('COUNTY_NA', ''))

        if name in ['嘉義縣', '嘉義市', '臺南市']:
            edge_color = 'r'
            lw = 1
            z = 3
        else:
            edge_color = 'gray'
            lw = 1
            z = 2

        ax.add_geometries(
            [record.geometry],
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor=edge_color,
            linewidth=lw,
            zorder=z
        )


def _plot_flash(ax, df):
    if df.empty:
        return
    df_ic = df[df['type'] == 'Cloud']
    df_cg = df[df['type'] == 'Ground']

    # IC (Cloud)
    ax.scatter(
        df_ic['lon'], df_ic['lat'],
        s=10, marker='o',
        edgecolors="#002FFFFF", facecolors='none',
        linewidths=0.5, alpha=1,
        transform=ccrs.PlateCarree(),
        label='IC', zorder=5
    )

    # CG (Ground)
    ax.scatter(
        df_cg['lon'], df_cg['lat'],
        s=10, marker='x', c="#058A00FF",
        linewidths=0.5, alpha=1,
        transform=ccrs.PlateCarree(),
        label='CG', zorder=4
    )


def _draw_one_hour(df_hour, hourly_counts_df, hour_dt, title, out_path_name):
    """
    df_hour: 這一小時的閃電資料
    hourly_counts_df: 當天 0–23H IC/CG 統計（columns: 'Cloud','Ground'）
    hour_dt: 這一小時的時間（Timestamp, LST）
    """

    ## ==========================================================
    ## 建立整張圖（上：主圖，下：折線圖）
    ## ==========================================================
    fig = plt.figure(figsize=(8, 12))

    # 主圖（地圖）位置：左10%，右90%，底25%，高70%
    ax = fig.add_axes([0.10, 0.25, 0.80, 0.70], projection=ccrs.PlateCarree())

    # 下方獨立折線圖區塊
    inset_ax = fig.add_axes([0.10, 0.08, 0.80, 0.15])  # 位置用 figure fraction

    ## ==========================================================
    ##                主圖內容：地圖 + 閃電
    ## ==========================================================
    _draw_base_map(ax)
    _plot_flash(ax, df_hour)

    # 全台範圍
    ax.set_extent(
        [lon_min_float, lon_max_float, lat_min_float, lat_max_float],
        crs=ccrs.PlateCarree()
    )

    ax.set_title(title, fontproperties=title_font)

    ax.legend(
        loc='lower right',
        prop=leg_font,
        markerscale=5,
        handlelength=2.5,
        handletextpad=0.5
    )

    ## ==========================================================
    ##                下方折線圖：IC / CG 逐時統計
    ## ==========================================================
    x_values = list(range(24))  # 0–23 小時
    current_hour = hour_dt.hour

    # =================== IC ===================
    if 'Cloud' in hourly_counts_df.columns:
        ic_values = hourly_counts_df['Cloud'].values

        # 已經過去時間：線 + 點
        inset_ax.plot(
            x_values[:current_hour+2], ic_values[:current_hour+2],
            color="#002FFFFF", linewidth=3, label="IC"
        )

        # 未來時間：淡色點
        inset_ax.plot(
            x_values[current_hour+1:], ic_values[current_hour+1:],
            color="#1F82F3D8", linewidth=2
        )

    # =================== CG ===================
    if 'Ground' in hourly_counts_df.columns:
        cg_values = hourly_counts_df['Ground'].values

        inset_ax.plot(
            x_values[:current_hour+2], cg_values[:current_hour+2],
            color="#058A00FF", linewidth=3, label="CG"
        )

        inset_ax.plot(
            x_values[current_hour+1:], cg_values[current_hour+1:],
            color="#82F07EA6", linewidth=2
        )

    # =================== x 軸設定 ===================
    inset_ax.set_xlim(-0.5, 23.5)
    inset_ax.set_xticks(range(0, 24, 3)) 
    inset_ax.set_xticklabels(
        [f"{h:02d}" for h in range(0, 24, 3)],
        fontproperties=myfont,
        fontsize=15
    )

    # inset_ax.set_ylabel("Count", fontproperties=myfont, fontsize=10)

    # inset_ax.legend(fontsize=8)

    ## ==========================================================
    ## 儲存
    ## ==========================================================
    out_name = f"{hour_dt.strftime('%Y%m%d_%H')}00_{out_path_name}_onecolor.png"
    out_path = os.path.join(result_folder_path, out_name)
    plt.savefig(out_path, dpi=600)
    # plt.show()
    plt.close(fig)
    print(f"已輸出： {out_path}")



## ============================== 每小時一張 ============================== ##
# 固定全台範圍（你可以之後再開嘉義台南 zoom-in）
lon_min_float, lon_max_float = 119.7, 122.3
lat_min_float, lat_max_float = 21.5, 25.5

# 以「天」為單位先切開，方便做當天 0–23H 統計
for single_date in pd.date_range(start=start_lct_dt.normalize(),
                                 end=end_lct_dt.normalize(),
                                 freq='D'):

    # single_date 已有 tz，不可再 tz_localize
    day_start = single_date
    day_end   = day_start + pd.Timedelta(days=1)

    # 當天所有閃電
    df_day_all = flash_data_df[
        (flash_data_df['time_lct'] >= day_start) &
        (flash_data_df['time_lct'] < day_end)
    ].copy()

    if df_day_all.empty:
        print(f"{single_date.strftime('%Y-%m-%d')} 無資料（全日），略過。")
        continue

    # 建立 hour 欄位（0–23）
    df_day_all['hour'] = df_day_all['time_lct'].dt.hour

    # 當天 0–23 小時統計
    hourly_counts_df = (
        df_day_all
        .groupby(['hour', 'type'])
        .size()
        .unstack(fill_value=0)
        .reindex(range(24), fill_value=0)
    )


    # 這一天內，以每小時為單位畫圖
    for hour in range(24):
        hour_start = day_start + pd.Timedelta(hours=hour)
        hour_end   = hour_start + pd.Timedelta(hours=1)

        # 還要符合整體時間範圍（start_lct_dt ~ end_lct_dt）
        if (hour_start > end_lct_dt) or (hour_end < start_lct_dt):
            continue

        df_hour = df_day_all[
            (df_day_all['time_lct'] >= hour_start) &
            (df_day_all['time_lct'] < hour_end)
        ].copy()

        if df_hour.empty:
            print(f"{hour_start.strftime('%Y-%m-%d %H:00')} 無資料，略過。")
            continue

        title = f"{hour_start.strftime('%Y/%m/%d %H:00')}–{hour_end.strftime('%H:00')} (LST)"

        _draw_one_hour(
            df_hour=df_hour,
            hourly_counts_df=hourly_counts_df,
            hour_dt=hour_start,
            title=title,
            out_path_name="taiwan_flash"
        )

print("全部完成！")
