import pyart
import numpy as np

import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
from glob import glob
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy import geodesic
from matplotlib.font_manager import FontProperties
import pandas as pd

def square_map(
    data_top_path,
    year,
    month,
    day,
    hh,
    mm,
    ss,
    lon0, lat0, lon1, lat1,
    show,
    station,
    add_flash=False,
    flash_data_top_path=None,
    set_extent=None,
):
    """
    畫 composite reflectivity+剖面線+雷達位置，可疊加 EN 閃電點，
    並畫出以剖面線為對角線的正方形。
    建立區域內閃電量資料 csv 檔，位於flash_in_box資料夾內。

    - add_flash: 是否加閃電（預設 False）
    - set_extent: 顯示範圍，預設 None 自動調整 格式: [lon_min, lon_max, lat_min, lat_max]
    """

    shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
    myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
    title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
    plt.rcParams['axes.unicode_minus'] = False

    vol_file = f"{data_top_path}/data/{year}{month}{day}_u.{station}/{year}{month}{day}{hh}{mm}{ss}.VOL"
    if not os.path.exists(vol_file):
        print(f"❌ 檔案不存在：{vol_file}")
        return None  # ★ 保持舊行為，但顯式回傳

    # === 先把統計結果的預設回傳容器準備好（即使未加閃電也能有一致回傳） ===
    flash_inrange_per_minute_dict = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}  # ★ 分分鐘
    flash_inrange_total_int = 0                                       # ★ 總數

    try:
        radar = pyart.io.read_nexrad_archive(vol_file)
        time_str = os.path.basename(vol_file).split('.')[0]
        time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
        time_str_LCT = (time_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M")
        time_str_for_flash = (time_dt + timedelta(hours=8)).strftime("%Y%m%d%H%M")

        grid = pyart.map.grid_from_radars(
            radar,
            grid_shape=(31, 241, 241),
            grid_limits=((0, 15000), (-150000, 150000), (-150000, 150000)),
            fields=['reflectivity'],
            weighting_function='Nearest',
        )

        x = grid.x['data'] / 1000
        y = grid.y['data'] / 1000
        z = grid.z['data']

        radar_lon = radar.longitude['data'][0]
        radar_lat = radar.latitude['data'][0]

        x2d, y2d = np.meshgrid(x * 1000, y * 1000)
        r = np.sqrt(x2d**2 + y2d**2)
        sweep_elevs = radar.fixed_angle['data']
        beam_heights = []
        for elev in sweep_elevs:
            h_beam = np.sqrt(r**2 + 8500000**2 + 2 * r * 8500000 * np.sin(np.radians(elev))) - 8500000
            beam_heights.append(h_beam)
        min_beam_height = np.min(np.array(beam_heights), axis=0)

        reflectivity_data = grid.fields['reflectivity']['data']
        for i in range(reflectivity_data.shape[0]):
            height = z[i]
            reflectivity_data[i][height < min_beam_height] = np.nan
        comp_reflect = np.nanmax(reflectivity_data, axis=0)

        lon_grid = radar_lon + (x / 111) / np.cos(np.radians(radar_lat))
        lat_grid = radar_lat + (y / 111)

        flash_data_all = []
        flash_colors = ['#000000', "#151515", "#232323", "#333333", "#3E3E3E"]
        if add_flash and flash_data_top_path is not None:
            try:
                base_time = datetime.strptime(time_str_for_flash, "%Y%m%d%H%M")
                for i in range(5):
                    flash_time = base_time - timedelta(minutes=i)
                    flash_min_str = flash_time.strftime("%Y%m%d%H%M")
                    flash_path = f"{flash_data_top_path}/flash_data/EN/sort_by_time/{year}/{month}/{flash_min_str}.csv"
                    if os.path.exists(flash_path):
                        flash_df = pd.read_csv(flash_path)
                        flash_df["minute_offset"] = -i
                        flash_data_all.append(flash_df)
                    else:
                        print(f"⚠️ 閃電資料不存在：{flash_path}")
                if flash_data_all:
                    flash_data_all_df = pd.concat(flash_data_all, ignore_index=True)
                else:
                    flash_data_all_df = None
            except Exception as e:
                print(f"⚠️ 閃電資料處理失敗: {e}")
                flash_data_all_df = None
        else:
            flash_data_all_df = None

        # ========================
        # ★★★ 新增：在範圍內的閃電數量統計 ★★★
        # ========================
        if (flash_data_all_df is not None) and (not flash_data_all_df.empty):
            ## 先把邊界整理成「左下/右上」以避免 lon0>lon1 或 lat0>lat1 的情況
            lon_min_box = min(lon0, lon1)
            lon_max_box = max(lon0, lon1)
            lat_min_box = min(lat0, lat1)
            lat_max_box = max(lat0, lat1)

            ## 只留在框內的點
            in_box_mask = (
                (flash_data_all_df["lon"] >= lon_min_box) & (flash_data_all_df["lon"] <= lon_max_box) &
                (flash_data_all_df["lat"] >= lat_min_box) & (flash_data_all_df["lat"] <= lat_max_box)
            )
            flash_in_box_df = flash_data_all_df.loc[in_box_mask].copy()

            ## 分分鐘統計（minute_offset = 0, -1, -2, -3, -4）→ 對齊成 {0..4}
            for i in range(5):
                cnt_i = (flash_in_box_df["minute_offset"] == -i).sum()
                flash_inrange_per_minute_dict[i] = int(cnt_i)

            ## 總數
            flash_inrange_total_int = int(len(flash_in_box_df))
            # print(flash_in_box_df)
            ##建立閃電的csv檔
            output_flash_dir = f"{data_top_path}/PID_square/{year}{month}{day}/flash_in_box"
            os.makedirs(output_flash_dir, exist_ok=True)
            output_flash_path = f"{output_flash_dir}/{time_str}_{station}_flash_in_box.csv"
            flash_in_box_df.to_csv(output_flash_path, index=False)
            ## 輸出到終端（不主動存檔，避免加你未要求的條件）
            print("====== 閃電數量（框內）======")
            print(f"時間(LST)：{time_str_LCT}，站台：{station}")
            print(f"經緯度框：lon[{lon_min_box:.4f}, {lon_max_box:.4f}], lat[{lat_min_box:.4f}, {lat_max_box:.4f}]")
            for i in range(5):
                print(f"  - {i} 分鐘前（minute_offset = -{i}）：{flash_inrange_per_minute_dict[i]} 筆")
            print(f"  → 總數：{flash_inrange_total_int} 筆")

        # ========================

        fig = plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())

        mesh = ax.pcolormesh(
            lon_grid, lat_grid, comp_reflect,
            # cmap='pyart_NWSRef',
            cmap='NWSRef',
            vmin=0, vmax=65,
            transform=ccrs.PlateCarree(),
            zorder = 2,alpha=0.8
        )

        ax.set_title(f"{time_str_LCT} LST CV", fontproperties=title_font)
        cbar = plt.colorbar(mesh, ax=ax, shrink=0.8)
        cbar.set_label("[dBZ]", fontproperties=myfont)
        cbar.set_ticks(np.arange(0, 70, 5))

        ax.add_geometries(
            Reader(shapefile_path).geometries(),
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor='green',
            linewidth=1,
        )

        # 原始範圍
        if set_extent == None:
            lon_min = np.min(lon_grid)
            lon_max = np.max(lon_grid)
            lat_min = np.min(lat_grid)
            lat_max = np.max(lat_grid)
            margin_lon = (lon_max - lon_min) * 0.02
            margin_lat = (lat_max - lat_min) * 0.02
            ax.set_extent([lon_min - margin_lon, lon_max + margin_lon,
                           lat_min - margin_lat, lat_max + margin_lat])
        else:
            ax.set_extent(set_extent)

        # ==== 剖面線與正方形 ====
        for lon in [lon0, lon1]:
            ax.plot([lon]*2, [lat0, lat1], '-', color='black', zorder=3, linewidth=2, transform=ccrs.PlateCarree())
        for lat in [lat0, lat1]:
            ax.plot([lon0, lon1], [lat]*2, '-', color='black', zorder=3, linewidth=2, transform=ccrs.PlateCarree())

        # ==== 閃電點（每分鐘一種顏色）====
        if add_flash and (flash_data_all_df is not None) and (not flash_data_all_df.empty):
            for i in range(5):
                df_minute = flash_data_all_df[flash_data_all_df["minute_offset"] == -i]

                if not df_minute.empty:
                    label = (time_dt - timedelta(minutes=i)+timedelta(hours=8)).strftime("%H:%M")
                    ax.scatter(
                        df_minute['lon'], df_minute['lat'],
                        s=100,
                        marker="x",
                        c=[flash_colors[i]],
                        edgecolors='black',
                        linewidths=2,
                        alpha = 1,
                        label= f'{label}',
                        transform=ccrs.PlateCarree(),
                        zorder=1
                    )
                    # ax.scatter(
                    #     df_minute['lon'], df_minute['lat'],
                    #     s=100,
                    #     marker="x",
                    #     c='black',
                    #     edgecolors='black',
                    #     linewidths=3,
                    #     alpha = 0.7,
                    #     transform=ccrs.PlateCarree(),
                    #     zorder=9-i
                    # )

        ax.legend(
            loc='upper right',
            fontsize=10,
            prop=myfont,
            frameon=True,        # 顯示外框
            framealpha=0.8,        # 透明度
            facecolor="#D0EFD1FF",   # 圖例背景色
            edgecolor='black'
        )
        plt.tight_layout()
        save_dir = f"{data_top_path}/PID_square/{year}{month}{day}/map"
        os.makedirs(save_dir, exist_ok=True)
        save_path = f"{save_dir}/{time_str}_{station}_map.png"
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ 儲存圖檔：{save_path}")
        if show:
            plt.show()
        plt.close()



    except Exception as e:
        print(f"❌ 讀取錯誤：{vol_file}\n原因：{e}")
        return None
