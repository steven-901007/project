# -*- coding: utf-8 -*-
"""
繪製2025/07/28~2025/08/04 嘉義、台南閃電分布
區分IC/CG閃電，每天輸出一張（導入微軟正黑體；IC/CG 共用每小時顏色；附 HH colorbar）
"""

import os
import pandas as pd
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from matplotlib.font_manager import FontProperties
from matplotlib import colors  # 色階正規化
from mpl_toolkits.axes_grid1.inset_locator import inset_axes  # 內嵌色條
import numpy as np
from matplotlib.colors import ListedColormap

## ============================== 路徑設定 ============================== ##
data_top_path = r"/home/steven/python_data/2025CWA_flash_plan"
flash_data_path = f"{data_top_path}/raw_data/flash/CWA/2025_0701-0811.csv"
county_shp_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
result_folder_path = f"{data_top_path}/result/flash_pattern/one_hour_one_color/"
os.makedirs(result_folder_path, exist_ok=True)

## ============================== 中文字型設定 ============================== ##
# 中文字型（微軟正黑）
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=12)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=12)

## ============================== 參數設定 ============================== ##
start_lct_dt = pd.Timestamp(2025, 7, 28, 0, 0, 0, tz='Asia/Taipei')  # 起
end_lct_dt   = pd.Timestamp(2025, 8, 4, 23, 59, 59, tz='Asia/Taipei')  # 迄(含)

## ============================== 每小時顏色（IC/CG共用） ============================== ##

# 先用 turbo 或 rainbow 產生 24 小時顏色
base_cmap = plt.colormaps.get_cmap("turbo")  # 或 'rainbow'
hour_colors_raw = [base_cmap(v) for v in np.linspace(0, 1, 24)]

# 讓紅色出現在下午 4 點（16 時） → 將顏色序列「右移」使第 16 位是紅色
shift_hours = 16
hour_color_list = hour_colors_raw[-shift_hours:] + hour_colors_raw[:-shift_hours]

# 建立 colormap 給 colorbar 用
hour_cmap = ListedColormap(hour_color_list, name="rainbow_shifted")

## ============================== 讀取與處理 ============================== ##
flash_data_df = pd.read_csv(flash_data_path)
flash_data_df['time'] = pd.to_datetime(flash_data_df['Epoch Time'], utc=True)  # UTC
flash_data_df['lat'] = flash_data_df['Latitude']
flash_data_df['lon'] = flash_data_df['Longitude']
flash_data_df['type'] = flash_data_df['Cloud or Ground']  # 'Cloud' / 'Ground'
flash_data_df['time_lct'] = flash_data_df['time'].dt.tz_convert('Asia/Taipei')  # 轉LCT

# 篩時間
mask_time = (flash_data_df['time_lct'] >= start_lct_dt) & (flash_data_df['time_lct'] <= end_lct_dt)
flash_data_df = flash_data_df.loc[mask_time].copy()
# print(f"篩選後筆數: {flash_data_df}")

## ============================== 繪圖函式 ============================== ##
def _draw_base_map(ax):
    county_shp_reader = Reader(county_shp_path)
    county_records = county_shp_reader.records()

    for record in county_records:
        # 嘗試抓縣市名稱欄位（各版 shapefile 命名略有不同）
        props = record.attributes
        name = props.get('COUNTYNAME', props.get('COUNTY_NA', props.get('COUNTY', '')))

        # 嘉義、台南縣市 → 綠色，其餘灰色；並將嘉義/台南層級拉高
        target_names = ['嘉義縣', '嘉義市', '臺南市', '台南市', 'Chiayi County', 'Chiayi City', 'Tainan City']
        if name in target_names:
            edge_color = 'green'
            lw = 1.0
            z = 5  # 往上層
        else:
            edge_color = 'gray'
            lw = 0.6
            z = 2

        ax.add_geometries(
            [record.geometry],
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor=edge_color,
            linewidth=lw,
            zorder=z
        )

def _plot_flash(ax, df_day):
    if df_day.empty:
        return

    ## 依型態分組
    df_ic_df = df_day[df_day['type'] == 'Cloud'].copy()   # 雲閃
    df_cg_df = df_day[df_day['type'] == 'Ground'].copy()  # 地閃

    ## 取小時（台灣時間）
    if not df_ic_df.empty:
        df_ic_df['hour'] = df_ic_df['time_lct'].dt.hour  # 0~23
    if not df_cg_df.empty:
        df_cg_df['hour'] = df_cg_df['time_lct'].dt.hour  # 0~23
    # print(df_cg_df)
    ## 依每小時畫點（IC/CG 共用同一套顏色）
    # IC：空心圓（邊框用對應小時顏色）
    # --- IC ---
    if not df_ic_df.empty:
        ic_label_done = False
        for h in range(24):
            ic_h_df = df_ic_df[df_ic_df['hour'] == h]
            if ic_h_df.empty:
                continue
            ax.scatter(
                ic_h_df['lon'], ic_h_df['lat'],
                s=1, marker='o',
                facecolors='none',
                edgecolors=[hour_color_list[h]],
                linewidths=0.2, alpha=1,
                transform=ccrs.PlateCarree(),
                label='IC' if not ic_label_done else None,  # 只第一次加
                zorder=5
            )
            ic_label_done = True  # 後續不再加 label

    # --- CG ---
    if not df_cg_df.empty:
        cg_label_done = False
        for h in range(24):
            cg_h_df = df_cg_df[df_cg_df['hour'] == h]
            if cg_h_df.empty:
                continue
            ax.scatter(
                cg_h_df['lon'], cg_h_df['lat'],
                s=1, marker='x',
                c=[hour_color_list[h]],
                linewidths=0.2, alpha=1,
                transform=ccrs.PlateCarree(),
                label='CG' if not cg_label_done else None,  # 只第一次加
                zorder=4
            )
            cg_label_done = True


def _add_hour_colorbar(ax):
    """底部離散色條：24 格（00~23），tick 位於色塊中心"""
    import numpy as np
    from matplotlib.colors import ListedColormap, BoundaryNorm
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes

    n_hours = 24
    bounds = np.arange(0, n_hours + 1, 1)          # 邊界：0,1,...,24（共 25 個）
    ticks = np.arange(0.5, n_hours, 1.0)           # tick：0.5,1.5,...,23.5（位於每格中心）
    tick_labels = [f"{h:02d}" for h in range(n_hours)]  # "00"~"23"

    # 離散 colormap + BoundaryNorm → colorbar 會畫出 24 個色塊（不漸層）
    discrete_cmap = ListedColormap(hour_color_list, name="hour24")
    norm = BoundaryNorm(boundaries=bounds, ncolors=n_hours, clip=False)

    sm = plt.cm.ScalarMappable(norm=norm, cmap=discrete_cmap)
    sm.set_array([])

    # 放在圖下方，適度下移避免壓到圖框
    cax = inset_axes(
        ax,
        width="100%", height="3%",
        loc="lower center",
        bbox_to_anchor=(0, -0.10, 1, 1),   # 需要更下移就把 -0.10 再調大一些（如 -0.14）
        bbox_transform=ax.transAxes,
        borderpad=0
    )

    cb = plt.colorbar(
        sm, cax=cax,
        orientation="horizontal",
        ticks=ticks,
        spacing="proportional"  # 與 BoundaryNorm 一起使用，確保每格寬度一致
    )
    cb.set_ticklabels(tick_labels)
    cb.set_label('hour(LST)', fontproperties=myfont, labelpad=2)

    cb.ax.tick_params(labelsize=6, length=0)  # 小字、不畫刻度線
    cb.outline.set_visible(False)             # 移除外框

    # 讓刻度標籤斜 45 度、貼近色條
    for label in cb.ax.get_xticklabels():
        label.set_rotation(45)
        # label.set_ha('right')  # 需要就打開
        # label.set_va('top')


def _draw(df_day, title, out_path_name):
    fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()})
    _draw_base_map(ax)
    _plot_flash(ax, df_day)
    ax.set_extent([lon_min_float, lon_max_float, lat_min_float, lat_max_float], crs=ccrs.PlateCarree())
    ax.set_title(title, fontproperties=title_font)

    # 圖例：放大符號但維持文字大小
    ax.legend(
        loc='upper right',
        prop=myfont,
        markerscale=7.0,
        handlelength=1.0,
        handletextpad=0.4,
    )

    # 單一 colorbar（顯示 HH）
    _add_hour_colorbar(ax)

    out_name = f"{single_date.strftime('%Y%m%d')}_{out_path_name}_one_hour_one_color.png"
    out_path = os.path.join(result_folder_path, out_name)
    plt.savefig(out_path, dpi=600, bbox_inches='tight')
    # plt.show()
    plt.close(fig)
    print(f"已輸出： {out_path}")

## ============================== 每日一張 ============================== ##
for single_date in pd.date_range(start=start_lct_dt, end=end_lct_dt, freq='D'):
    next_day = single_date + pd.Timedelta(days=1)

    df_day = flash_data_df[
        (flash_data_df['time_lct'] >= single_date) &
        (flash_data_df['time_lct'] < next_day)
    ].copy()

    if df_day.empty:
        print(f"{single_date.strftime('%Y-%m-%d')} 無資料，略過。")
        continue

    # 全台範圍
    lon_min_float, lon_max_float = 119.7, 122.3
    lat_min_float, lat_max_float = 21.5, 25.5
    _draw(df_day, f"全台閃電分布\n{single_date.strftime('%Y/%m/%d')}", "taiwan_flash")

    # 嘉義、台南範圍
    lon_min_float, lon_max_float = 120.0, 121.0
    lat_min_float, lat_max_float = 22.8, 23.66

    # 空間篩選（嘉義＋台南）
    df_day_ct = df_day[
        (df_day['lon'] >= lon_min_float) & (df_day['lon'] <= lon_max_float) &
        (df_day['lat'] >= lat_min_float) & (df_day['lat'] <= lat_max_float)
    ].copy()

    if df_day_ct.empty:
        print(f"{single_date.strftime('%Y-%m-%d')} 嘉義台南無資料，略過。")
        continue

    _draw(df_day_ct, f"嘉義、台南閃電分布\n{single_date.strftime('%Y/%m/%d')}", "chiayi_tainan_flash")

print("全部完成！")




# -*- coding: utf-8 -*-
"""
繪製2025/07/28~2025/08/04 嘉義、台南大雨閃電分布
區分IC/CG閃電，每天輸出一張（導入微軟正黑體）
不分小時都用同一種顏色
"""

import os
import pandas as pd
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from matplotlib.font_manager import FontProperties
from matplotlib import cm, colors

## ============================== 路徑設定 ============================== ##
data_top_path = r"/home/steven/python_data/2025CWA_flash_plan"
flash_data_path = f"{data_top_path}/raw_data/flash/CWA/2025_0701-0811.csv"
county_shp_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
result_folder_path = f"{data_top_path}/result/flash_pattern/onecolor/"
os.makedirs(result_folder_path, exist_ok=True)

## ============================== 中文字型設定 ============================== ##
# 中文字型（微軟正黑）
myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=12)
title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=12)

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

# 篩時間
mask_time = (flash_data_df['time_lct'] >= start_lct_dt) & (flash_data_df['time_lct'] <= end_lct_dt)
flash_data_df = flash_data_df.loc[mask_time].copy()
print(f"篩選後筆數: {len(flash_data_df)}")

## ============================== 繪圖函式 ============================== ##
def _draw_base_map(ax):
    county_shp_reader = Reader(county_shp_path)
    county_records = county_shp_reader.records()

    for record in county_records:
        # 嘗試抓縣市名稱欄位（各版 shapefile 命名略有不同）
        props = record.attributes
        name = props.get('COUNTYNAME', props.get('COUNTY_NA', ''))

        # 嘉義、台南縣市 → 綠色，其餘灰色
        if name  in ['嘉義縣', '嘉義市', '臺南市']:
            edge_color = 'r'
            lw = 0.5
            z = 3
        else:
            edge_color = 'gray'
            lw = 0.5
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
    ax.scatter(df_ic['lon'], df_ic['lat'], s=1,marker ='o',edgecolors='blue',facecolors='none', linewidths = 0.2, alpha=1,
               transform=ccrs.PlateCarree(), label='IC',zorder = 5)

    # CG (Ground)
    ax.scatter(df_cg['lon'], df_cg['lat'], s=1,marker = 'x', c='green',linewidths = 0.2, alpha=1,
               transform=ccrs.PlateCarree(), label='CG',zorder = 4)

def _draw(df_day,title,out_path_name):
    fig, ax = plt.subplots( subplot_kw={'projection': ccrs.PlateCarree()})
    _draw_base_map(ax)
    _plot_flash(ax, df_day)
    ax.set_extent([lon_min_float, lon_max_float, lat_min_float, lat_max_float], crs=ccrs.PlateCarree())
    ax.set_title(title, fontproperties=title_font)
    ax.legend(
        loc='upper right',
        prop=myfont,        # 保持字型與字體大小
        markerscale=3.0,    # ← 圖例符號放大倍率（預設 1.0，可試 2~3）
        handlelength=1.8,   # 控制圖例符號與文字距離
        handletextpad=0.4   # 控制間距
        )

    out_name = f"{single_date.strftime('%Y%m%d')}_{out_path_name}_onecolor.png"
    out_path = os.path.join(result_folder_path, out_name)
    plt.savefig(out_path,dpi = 600,bbox_inches='tight')
    # plt.show()
    plt.close(fig)
    print(f"已輸出： {out_path}")

## ============================== 每日一張 ============================== ##
for single_date in pd.date_range(start=start_lct_dt, end=end_lct_dt, freq='D'):
    next_day = single_date + pd.Timedelta(days=1)

    df_day = flash_data_df[
        (flash_data_df['time_lct'] >= single_date) &
        (flash_data_df['time_lct'] < next_day)
    ].copy()



    if df_day.empty:
        print(f"{single_date.strftime('%Y-%m-%d')} 無資料，略過。")
        continue

    # 全台範圍
    lon_min_float, lon_max_float = 119.7, 122.3
    lat_min_float, lat_max_float = 21.5, 25.5
    
    _draw(df_day, f"全台閃電分布\n{single_date.strftime('%Y/%m/%d')} (LST)", "taiwan_flash")


    # 嘉義、台南範圍
    lon_min_float, lon_max_float = 120.0, 121.0
    lat_min_float, lat_max_float = 22.8, 23.66
    # 空間篩選（嘉義＋台南）
    df_day = df_day[
        (df_day['lon'] >= lon_min_float) & (df_day['lon'] <= lon_max_float) &
        (df_day['lat'] >= lat_min_float) & (df_day['lat'] <= lat_max_float)
    ].copy()

    if df_day.empty:
        print(f"{single_date.strftime('%Y-%m-%d')} 無資料，略過。")
        continue


    _draw(df_day, f"嘉義、台南閃電分布\n{single_date.strftime('%Y/%m/%d')} (LST)", "chiayi_tainan_flash")

print("全部完成！")







# -*- coding: utf-8 -*-
"""
每日全台 IC / CG 閃電量摺線圖（不做時區轉換）
輸入：CWA rawdata
輸出：每日一張圖
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

## ============================== 路徑設定 ============================== ##
data_top_path = r"/home/steven/python_data/2025CWA_flash_plan"
flash_data_path = f"{data_top_path}/raw_data/flash/CWA/2025_0701-0811.csv"
result_folder_path = f"{data_top_path}/result/flash_daily_line/"
os.makedirs(result_folder_path, exist_ok=True)

## ============================== 中文字型 ============================== ##
font_path = f"{data_top_path}/msjh.ttc"
myfont = FontProperties(fname=font_path, size=11)

## ============================== 範圍設定 ============================== ##
lon_min, lon_max = 119.7, 122.3
lat_min, lat_max = 21.5, 25.5

## ============================== 讀取資料 ============================== ##
df = pd.read_csv(flash_data_path)
df["time_raw"] = pd.to_datetime(df["Epoch Time"], errors="coerce", utc=False)  # 不做 tz 轉換
df["lat"] = df["Latitude"]
df["lon"] = df["Longitude"]
df["type"] = df["Cloud or Ground"]

# 篩範圍
df = df[(df["lon"] >= lon_min) & (df["lon"] <= lon_max) &
        (df["lat"] >= lat_min) & (df["lat"] <= lat_max)].copy()

df = df.dropna(subset=["time_raw"])
print(f"全台範圍內資料筆數: {len(df)}")

## ============================== 日期迴圈 ============================== ##
for single_date in pd.date_range(df["time_raw"].min().floor("D"), df["time_raw"].max().floor("D"), freq="D"):

    next_day = single_date + pd.Timedelta(days=1)
    df_day = df[(df["time_raw"] >= single_date) & (df["time_raw"] < next_day)].copy()

    if df_day.empty:
        print(f"{single_date.strftime('%Y-%m-%d')} 無資料，略過。")
        continue

    # 加入小時欄位
    df_day["hour"] = df_day["time_raw"].dt.hour

    # 計算每小時 IC/CG 筆數
    ic_hourly = df_day[df_day["type"] == "Cloud"].groupby("hour").size().reindex(range(24), fill_value=0)
    cg_hourly = df_day[df_day["type"] == "Ground"].groupby("hour").size().reindex(range(24), fill_value=0)

    # 繪圖
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(ic_hourly.index, ic_hourly.values, marker="o", label="IC", color="blue")
    ax.plot(cg_hourly.index, cg_hourly.values, marker="x", label="CG", color="green")

    ax.set_title(f"全台閃電量（{single_date.strftime('%Y/%m/%d')}，原始時間）", fontproperties=myfont)
    ax.set_xlabel("小時 (原始時間)", fontproperties=myfont)
    ax.set_ylabel("閃電筆數", fontproperties=myfont)
    ax.set_xticks(range(0, 24, 2))
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(prop=myfont)

    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontproperties(myfont)

    out_name = f"{single_date.strftime('%Y%m%d')}_flash_line.png"
    out_path = os.path.join(result_folder_path, out_name)
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"已輸出： {out_path}")

print("全部完成！")
