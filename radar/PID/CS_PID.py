import pyart
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Geod
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from matplotlib.font_manager import FontProperties
from datetime import datetime, timedelta


def hydrometeor_cross_section(
    data_top_path,
    year,
    month,
    day,
    hh,
    mm,
    ss,
    lon0, lat0, lon1, lat1,
    pid,
    show=True,
):

    time_str = f"{year}{month}{day}{hh}{mm}{ss}"
    time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
    time_str_LCT = (time_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M")
    # ==== 中文顯示 ====
    myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
    title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
    plt.rcParams['axes.unicode_minus'] = False
    file_path = f"{data_top_path}/PID/{year}{month}{day}_{pid}/{time_str}.nc"
    # ==== 讀取雷達 Grid 資料 ====
    radar = pyart.io.read(file_path)
    grid = pyart.map.grid_from_radars(
        radar,
        grid_shape=(21, 400, 400),
        grid_limits=((0, 10000), (-150000, 150000), (-150000, 150000)),
        fields=['hydro_class'],
        gridding_algo='map_gates_to_grid',
        weighting_function='Barnes',
        roi_func='dist_beam',
    )

    # ==== 地理→雷達座標轉換 ====
    geod = Geod(ellps='WGS84')
    az12, _, dist = geod.inv(lon0, lat0, lon1, lat1)
    npoints = 300
    distances = np.linspace(0, dist, npoints)
    lons, lats, _ = geod.fwd(np.full(npoints, lon0), np.full(npoints, lat0), np.full(npoints, az12), distances)

    radar_lon = radar.longitude['data'][0]
    radar_lat = radar.latitude['data'][0]
    azs, _, dists = geod.inv(np.full(npoints, radar_lon), np.full(npoints, radar_lat), lons, lats)
    x = dists * np.sin(np.radians(azs)) / 1000  # km
    y = dists * np.cos(np.radians(azs)) / 1000  # km

    # ==== 擷取 Grid 資料 ====
    gx = grid.x['data'] / 1000
    gy = grid.y['data'] / 1000
    gz = grid.z['data'] / 1000
    hydro = grid.fields['hydro_class']['data']

    cross_section = np.full((len(gz), len(x)), np.nan)
    for i, (px, py) in enumerate(zip(x, y)):
        ix = np.argmin(np.abs(gx - px))
        iy = np.argmin(np.abs(gy - py))
        column = hydro[:, iy, ix]
        if np.ma.is_masked(column):
            column = column.astype(float).filled(np.nan)
        cross_section[:, i] = column

    # ==== 畫圖 ====
    fig, ax = plt.subplots()

    zz, xx = np.meshgrid(gz, np.linspace(0, dist / 1000, len(x)), indexing='ij')
    masked_cross_section = np.ma.masked_invalid(cross_section)
    
    # 自訂 colormap（紅色給 Graupel）
    if pid == 'park':
        custom_colors = [
            "#1FE4F3FF",  # Rain
            "#ebff0e",  # Melting Layer
            "#2ca02c",  # Wet Snow
            "#27d638",  # Dry Snow
            "#f51010",  # Graupel（紅）
            "#3c00ff",  # Hail
        ]
        label_names = ['Rain', 'Melting Layer', 'Wet Snow', 'Dry Snow', 'Graupel', 'Hail']
    elif pid == 'way':
        custom_colors = [
            "#1FE4F3FF",  # 0 Drizzle
            "#1FE4F3FF",  # 1 Rain
            "#2ca02c",  # 2 Weak Snow
            "#2ca02c",  # 3 Strong Snow
            "#2ca02c",  # 4 Wet Snow
            "#f51010",  # 5 Dry Graupel
            "#f51010",  # 6 Wet Graupel
            "#3c00ff",  # 7 Small Hail
            "#3c00ff",  # 8 Large Hail
            "#ebff0e",  # 9 Rain-Hail Mixture
            "#f49d07",  # 10 Suppercooled water
        ]
        label_names = [
        'Drizzle', 'Rain', 'Weak Snow', 'Strong Snow', 'Wet Snow',
        'Dry Graupel', 'Wet Graupel', 'Small Hail', 'Large Hail', 'Rain-Hail Mixture','Suppercooled water'
        ]



    cmap = ListedColormap(custom_colors)
    ax.pcolormesh(xx, zz, masked_cross_section, cmap=cmap, vmin=0, vmax=len(custom_colors) - 1, shading='auto')



    # ax.pcolormesh(xx, zz, masked_cross_section, cmap=cmap, vmin=0, vmax=9, shading='auto')

    # 標籤與標題
    ax.set_xlabel("km", fontproperties=myfont)
    ax.set_ylabel("高度 (km)", fontproperties=myfont)
    ax.set_title(f"{time_str_LCT}",
                #  f"Hydrometeor Cross-Section\n{time_str_LCT}",
                 fontsize=16)

    # 圖例

    # patches = [mpatches.Patch(color=cmap(i), label=label_names[i]) for i in range(len(custom_colors))]
    # ax.legend(handles=patches, loc='upper right')

    plt.tight_layout()

    save_path = f"{data_top_path}/PID_CS/{year}{month}{day}/{time_str}_{pid}_PID.png"
    plt.savefig(save_path, dpi=150)
    print(f"✅ 圖檔已儲存：{save_path}")
    if show:
        plt.show()
    plt.close()


# ========== 使用範例 ==========
# hydrometeor_cross_section(
#     file_path = "C:/Users/steve/python_data/radar/PID/20240523/20240523000200.nc",
#     time_str = "20240523000200",
#     lon0 = 121.77305603027344,
#     lat0 = 25.073055267333984,
#     lon1 = 121.77305603027344,
#     lat1 = 26.07,
#     font_name = 'MingLiu',
#     save_path = None,   # 若指定存檔路徑，例如 "output.png"
#     show = True,
#     figsize = (12, 6)
# )

