import pyart
import numpy as np
import matplotlib.pyplot as plt
from pyproj import Geod
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from matplotlib.font_manager import FontProperties
from datetime import datetime, timedelta


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
    show,
    station
):

    time_str = f"{year}{month}{day}{hh}{mm}{ss}"
    time_dt = datetime.strptime(time_str, "%Y%m%d%H%M%S")
    time_str_LCT = (time_dt + timedelta(hours=8)).strftime("%Y/%m/%d %H:%M")
    
    # ==== 中文顯示 ====
    # 請確保字型路徑正確，否則中文會變方框
    myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=12) 
    
    plt.rcParams['axes.unicode_minus'] = False
    file_path = f"{data_top_path}/PID/{year}{month}{day}_{station}_{pid}/{time_str}.nc"
    
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
    fig, ax = plt.subplots(figsize=(10, 6)) # 稍微加大畫布方便放圖例

    zz, xx = np.meshgrid(gz, np.linspace(0, dist / 1000, len(x)), indexing='ij')
    masked_cross_section = np.ma.masked_invalid(cross_section)
    
    # ==========================================
    # 設定顏色與標籤 (PID Dictionary)
    # ==========================================
# 自訂 colormap
    if pid == 'park':
        # Park et al. (2009) 修正後的正確定義
        # 論文編號 1~10 對應 Python 索引 0~9
        
        custom_colors = [
            "#BEBEBE",  # 0: GC/AP - Ground Clutter (地雜波/異常傳播) -> 灰色
            "#8B4513",  # 1: BS    - Biological Scatterers (生物散射體) -> 棕色
            "#00FFFF",  # 2: DS    - Dry Snow (乾雪) -> 青色
            "#0099CC",  # 3: WS    - Wet Snow (濕雪) -> 深青色
            "#E0FFFF",  # 4: CR    - Crystals (冰晶) -> 淡青色
            "#FFFF00",  # 5: GR    - Graupel (軟雹/霰) -> 黃色
            "#FF8C00",  # 6: BD    - Big Drops (大雨滴) -> 橙色
            "#00FF00",  # 7: RA    - Light/Moderate Rain (輕/中度雨) -> 亮綠色
            "#008000",  # 8: HR    - Heavy Rain (強降雨) -> 深綠色
            "#FF0000",  # 9: RH    - Rain/Hail Mixture (雨/冰雹混合) -> 紅色
        ]
        
        # 修正後的名稱標籤
        label_names = [
            '0: GC/AP (雜波)', 
            '1: BS (生物)', 
            '2: DS (乾雪)', 
            '3: WS (濕雪)', 
            '4: CR (冰晶)', 
            '5: GR (霰)', 
            '6: BD (大雨滴)', 
            '7: RA (中/小雨)', 
            '8: HR (強降雨)',    # 修正：Heavy Rain
            '9: RH (雨雹混合)'   # 修正：Rain/Hail Mixture
        ]

    elif pid == 'way':
        custom_colors = [
            "#1FE4F3",  # 0 Drizzle
            "#1FE4F3",  # 1 Rain
            "#2ca02c",  # 2 Weak Snow
            "#2ca02c",  # 3 Strong Snow
            "#2ca02c",  # 4 Wet Snow
            "#f51010",  # 5 Dry Graupel
            "#f51010",  # 6 Wet Graupel
            "#3c00ff",  # 7 Small Hail
            "#3c00ff",  # 8 Large Hail
            "#ebff0e",  # 9 Rain-Hail Mixture
            "#f49d07",  # 10 Supercooled water
        ]
        label_names = [
            '0: Drizzle', '1: Rain', '2: Weak Snow', '3: Strong Snow', '4: Wet Snow',
            '5: Dry Graupel', '6: Wet Graupel', '7: Small Hail', '8: Large Hail', 
            '9: Rain-Hail Mix', '10: Supercooled'
        ]

    # 建立 Colormap
    cmap = ListedColormap(custom_colors)
    
    # 繪製剖面圖
    # vmin= -0.5, vmax= len-0.5 是為了讓顏色塊準確對齊整數刻度中心
    mesh = ax.pcolormesh(xx, zz, masked_cross_section, cmap=cmap, 
                         vmin=-0.5, vmax=len(custom_colors)-0.5, shading='auto')

    # 標籤與標題
    ax.set_xlabel("距離 (km)", fontproperties=myfont)
    ax.set_ylabel("高度 (km)", fontproperties=myfont)
    ax.set_title(f"{station} PID Cross-Section: {time_str_LCT}", fontsize=16)

    # ==== 圖例 (Legend) ====
    # 建立圖例 Patch 物件
    patches = [mpatches.Patch(color=custom_colors[i], label=label_names[i]) for i in range(len(custom_colors))]
    
    # 將圖例放在圖外右側，避免擋住剖面
    ax.legend(handles=patches, loc='upper left', bbox_to_anchor=(1.02, 1), 
              prop=myfont, title="Hydrometeor Type")

    plt.tight_layout()

    save_path = f"{data_top_path}/PID_CS/{year}{month}{day}/{time_str}_{pid}_PID.png"
    # 確保輸出資料夾存在
    import os
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    plt.savefig(save_path, dpi=150, bbox_inches='tight') # bbox_inches='tight' 避免圖例被切掉
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

