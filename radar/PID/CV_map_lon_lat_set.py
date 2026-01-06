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

def lon_lat_set(
    data_top_path,
    year,
    month,
    day,
    hh,
    mm,
    ss,
    station,
    point_num,
    range_radius,
    add_flash=False,
    flash_data_top_path=None,


):
    """
    畫 composite reflectivity+剖面線+雷達位置，可疊加 EN 閃電點。

    - add_flash: 是否加閃電（預設 False）

    """

    shapefile_path = f"{data_top_path}/Taiwan_map_data/COUNTY_MOI_1090820.shp"
    myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
    title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
    plt.rcParams['axes.unicode_minus'] = False

    # EN閃電時間字串
    vol_file = f"{data_top_path}/data/{year}{month}{day}_u.{station}/{year}{month}{day}{hh}{mm}{ss}.VOL"
    if not os.path.exists(vol_file):
        print(f"❌ 檔案不存在：{vol_file}")
        return

    try:
        radar = pyart.io.read_nexrad_archive(vol_file)
        time_str = os.path.basename(vol_file).split('.')[0]
        time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
        time_str_LCT = (time_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M:%S")
        time_str_for_flash = (time_dt + timedelta(hours=8)).strftime("%Y%m%d%H%M")

        # ==== 製作Grid資料 ====
        grid = pyart.map.grid_from_radars(
            radar,
            grid_shape=(31, 241, 241),
            grid_limits=((0, 15000), (-150000, 150000), (-150000, 150000)),
            fields=['reflectivity'],
            weighting_function='Nearest',
        )

        # ==== Beam遮罩 ====
        x = grid.x['data'] / 1000  # km
        y = grid.y['data'] / 1000
        z = grid.z['data']  # m

        radar_lon = radar.longitude['data'][0]
        radar_lat = radar.latitude['data'][0]

        x2d, y2d = np.meshgrid(x * 1000, y * 1000)  # m
        r = np.sqrt(x2d**2 + y2d**2)
        sweep_elevs = radar.fixed_angle['data']
        beam_heights = []
        for elev in sweep_elevs:
            h_beam = np.sqrt(r**2 + 8500000**2 + 2 * r * 8500000 * np.sin(np.radians(elev))) - 8500000
            beam_heights.append(h_beam)
        min_beam_height = np.min(np.array(beam_heights), axis=0)

        # ==== Composite Reflectivity ====
        reflectivity_data = grid.fields['reflectivity']['data']
        for i in range(reflectivity_data.shape[0]):
            height = z[i]
            reflectivity_data[i][height < min_beam_height] = np.nan
        comp_reflect = np.nanmax(reflectivity_data, axis=0)

        # ==== 經緯度格點 ====
        lon_grid = radar_lon + (x / 111) / np.cos(np.radians(radar_lat))
        lat_grid = radar_lat + (y / 111)

        # ==== 閃電資料處理 ====
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
                        flash_df["minute_offset"] = -i  # 紀錄是哪一分鐘前
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

        # ==== 畫圖 ====
        fig = plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())

        mesh = ax.pcolormesh(
            lon_grid, lat_grid, comp_reflect,
            # cmap='pyart_NWSRef',
            cmap='NWSRef',
            vmin=0, vmax=65,
            transform=ccrs.PlateCarree(),
            zorder = 2,alpha=0.9
        )

        # 標題與 colorbar
        ax.set_title(
            f"CV 測站:{station}\n觀測時間:{time_str_LCT}",
            fontproperties=title_font
        )
        cbar = plt.colorbar(mesh, ax=ax, shrink=0.8)
        cbar.set_label("反射率 (dBZ)", fontproperties=myfont)
        cbar.set_ticks(np.arange(0, 70, 5))

        # 台灣邊界
        ax.add_geometries(
            Reader(shapefile_path).geometries(),
            crs=ccrs.PlateCarree(),
            facecolor='none',
            edgecolor='black',
            linewidth=1,
        )

        dis = 36
        # 雷達中心與 36km 圓
        ax.plot(radar_lon, radar_lat, 'ro', transform=ccrs.PlateCarree())
        # 畫 36km 藍圈
        ## 基本參數
        center_lon = radar_lon
        center_lat = radar_lat
        radius_m = dis * 1000

        ## 產生兩段圓：第一段從 0°~180°，第二段從 90°~360°
        circle1 = geodesic.Geodesic().circle(lon=center_lon, lat=center_lat, radius=radius_m, n_samples=180, endpoint=False)
        circle2 = geodesic.Geodesic().circle(lon=center_lon, lat=center_lat, radius=radius_m, n_samples=180, endpoint=False)
        # 把第二段的角度往後平移 90°
        circle2 = np.roll(circle2, shift=90, axis=0)

        
        ax.plot(circle1[:, 0], circle1[:, 1], color='lime',linestyle='--', transform=ccrs.PlateCarree())
        ax.plot(circle2[:, 0], circle2[:, 1], color='lime',linestyle='--', transform=ccrs.PlateCarree(), label=f'{dis}km')

        ax.plot(radar_lon, radar_lat, 'x', color='r', zorder=5, markersize=15, label='Radar')

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
                        alpha = 0.7,
                        label= f'{label}',
                        transform=ccrs.PlateCarree(),
                        zorder=1
                    )
                    # ax.scatter(
                    #     df_minute['lon'], df_minute['lat'],
                    #     s=100,
                    #     marker="x",
                    #     c='black',
                    #     linewidths=3,
                    #     alpha = 1,
                    #     transform=ccrs.PlateCarree(),
                    #     label= f'{label}',
                    #     zorder=2
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
        else:
            # 沒有閃電或未指定資料夾，不顯示 legend
            pass

        # ==== 顯示範圍 ====
        lon_min = np.min(lon_grid)
        lon_max = np.max(lon_grid)
        lat_min = np.min(lat_grid)
        lat_max = np.max(lat_grid)
        margin_lon = (lon_max - lon_min) * 0.02
        margin_lat = (lat_max - lat_min) * 0.02
        ax.set_extent([lon_min - margin_lon, lon_max + margin_lon,
                       lat_min - margin_lat, lat_max + margin_lat])
        gl = ax.gridlines(draw_labels=True)
        gl.right_labels = False

        plt.tight_layout()

        selected_points = []

        print(f"請用滑鼠在圖上點選 {point_num} 個點，將回傳經緯度")
        points = plt.ginput(point_num, timeout=0)  # 等你點n下
        if point_num == 1:
            lon_center, lat_center = points[0]
            selected_points = [
                (lon_center - range_radius, lat_center - range_radius),
                (lon_center + range_radius, lat_center + range_radius)
            ]
        elif point_num == 2:
            selected_points = points
        for i, (lon, lat) in enumerate(selected_points):
            print(f'第{i+1}點：經度={lon:.5f}, 緯度={lat:.5f}')
        plt.close()


        return selected_points
    
    except Exception as e:
        print(f"❌ 讀取錯誤：{vol_file}\n原因：{e}")

# ======= 使用範例 =======
# cross_section_map(
#     data_top_path = "C:/Users/steve/python_data/radar",
#     year = '2024',
#     month = '05',
#     day = '23',
#     hh = '00',
#     mm = '02',
#     ss = '00',
#     lon0 = 121.77305603027344,
#     lat0 = 25.073055267333984,
#     lon1 = 121.77305603027344,
#     lat1 = 26.07,
#     show = True,
#     add_flash = True,
#     flash_data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
# )
