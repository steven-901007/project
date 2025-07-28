def draw_PID_count_hotmap(
    data_top_path,
    year,
    month,
    day,
    hh,
    mm,
    ss,
    lon0,
    lat0,
    lon1,
    lat1,
):
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import pyart
    from matplotlib.font_manager import FontProperties
    import matplotlib.patheffects as path_effects

    cmap_name='ocean'
    class_names = ['Rain', 'Melting Layer', 'Wet Snow', 'Dry Snow', 'Graupel', 'Hail']
    pid_types = np.arange(len(class_names))

    myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
    title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
    plt.rcParams['axes.unicode_minus'] = False

    time_str = f"{year}{month}{day}{hh}{mm}{ss}"
    file_path = f"{data_top_path}/PID/{year}{month}{day}/{time_str}.nc"
    save_dir = f"{data_top_path}/PID_square/{year}{month}{day}"
    os.makedirs(save_dir, exist_ok=True)
    save_path_heatmap = f"{save_dir}/{time_str}_PID_count_heatmap.png"

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

    hydro_data = grid.fields['hydro_class']['data']
    gz = grid.z['data'] / 1000  # km
    gx = grid.x['data'] / 1000  # km
    gy = grid.y['data'] / 1000

    radar_lon = radar.longitude['data'][0]
    radar_lat = radar.latitude['data'][0]

    lons = radar_lon + gx / 111
    lats = radar_lat + gy / 111
    lon2d, lat2d = np.meshgrid(lons, lats, indexing='xy')

    lon_min_box = min(lon0, lon1)
    lon_max_box = max(lon0, lon1)
    lat_min_box = min(lat0, lat1)
    lat_max_box = max(lat0, lat1)

    mask_box = (lon2d >= lon_min_box) & (lon2d <= lon_max_box) & \
               (lat2d >= lat_min_box) & (lat2d <= lat_max_box)

    nz = hydro_data.shape[0]
    count_matrix = np.zeros((nz, len(pid_types)), dtype=int)

    for iz in range(nz):
        slice_data = hydro_data[iz]
        data_in_box = slice_data[mask_box]
        valid = data_in_box[~data_in_box.mask]
        for i, pid_type in enumerate(pid_types):
            count_matrix[iz, i] = np.sum(valid == pid_type)

    # ==== 修正邊界 ====
    x_edges = np.arange(len(class_names)+1) - 0.5
    y_edges = np.append(gz, gz[-1]+(gz[-1]-gz[-2]))

    fig, ax = plt.subplots(figsize=(9, 6))
    pc = ax.pcolormesh(x_edges, y_edges, count_matrix, cmap=cmap_name, shading='auto')
    cbar = plt.colorbar(pc, ax=ax)
    cbar.set_label("數量(網格點)", fontproperties=myfont)
    ax.set_ylabel("高度 (km)", fontproperties=myfont)
    ax.set_title("hydro_class [pixel]", fontproperties=title_font)
    ax.set_xticks(np.arange(len(class_names)))
    ax.set_xticklabels(class_names, fontproperties=myfont)

    # ======= 每格加數字 =======
    for iz in range(nz):
        for ix in range(len(pid_types)):
            val = count_matrix[iz, ix]
            # x 中心 = ix + 0.5
            # y 中心 = (gz[iz] + gz[iz+1])/2 (但要確保 gz 有補一層)
            if iz < nz - 1:
                y_center = (gz[iz] + gz[iz+1]) / 2
            else:
                y_center = gz[iz] + (gz[iz] - gz[iz-1]) / 2
            txt = ax.text(
                ix, y_center, f"{val}",  # x=ix, y=格中間
                ha='center', va='center',
                color='white' if pc.norm(val) > 0.5 * pc.norm.vmax else 'black',
                fontsize=9, fontproperties=myfont
            )        # 加白色外框（PathEffects）
            txt.set_path_effects([
                path_effects.Stroke(linewidth=2, foreground='white'),
                path_effects.Normal()
            ])

    plt.tight_layout()
    plt.savefig(save_path_heatmap, dpi=150)
    print(f"✅ 儲存熱圖：{save_path_heatmap}")

    plt.close()

def draw_PID_percent_hotmap(
    data_top_path,
    year,
    month,
    day,
    hh,
    mm,
    ss,
    lon0,
    lat0,
    lon1,
    lat1,
    ):
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    import pyart
    from matplotlib.font_manager import FontProperties
    import matplotlib.patheffects as path_effects

    cmap_name='Purples'
    class_names = ['Rain', 'Melting Layer', 'Wet Snow', 'Dry Snow', 'Graupel', 'Hail']
    pid_types = np.arange(len(class_names))

    myfont = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=14)
    title_font = FontProperties(fname=f'{data_top_path}/msjh.ttc', size=20)
    plt.rcParams['axes.unicode_minus'] = False

    time_str = f"{year}{month}{day}{hh}{mm}{ss}"
    file_path = f"{data_top_path}/PID/{year}{month}{day}/{time_str}.nc"
    save_dir = f"{data_top_path}/PID_square/{year}{month}{day}"
    os.makedirs(save_dir, exist_ok=True)
    save_path_heatmap = f"{save_dir}/{time_str}_PID_percent_heatmap.png"

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

    hydro_data = grid.fields['hydro_class']['data']
    gz = grid.z['data'] / 1000  # km
    gx = grid.x['data'] / 1000  # km
    gy = grid.y['data'] / 1000

    radar_lon = radar.longitude['data'][0]
    radar_lat = radar.latitude['data'][0]

    lons = radar_lon + gx / 111
    lats = radar_lat + gy / 111
    lon2d, lat2d = np.meshgrid(lons, lats, indexing='xy')

    lon_min_box = min(lon0, lon1)
    lon_max_box = max(lon0, lon1)
    lat_min_box = min(lat0, lat1)
    lat_max_box = max(lat0, lat1)

    mask_box = (lon2d >= lon_min_box) & (lon2d <= lon_max_box) & \
               (lat2d >= lat_min_box) & (lat2d <= lat_max_box)

    nz = hydro_data.shape[0]
    ratio_matrix = np.zeros((nz, len(pid_types)), dtype=float)

    # ...前略...
    for iz in range(nz):
        slice_data = hydro_data[iz]
        data_in_box = slice_data[mask_box]
        valid = data_in_box[~data_in_box.mask]
        total = len(valid)
        if total > 0:
            for i, pid_type in enumerate(pid_types):
                ratio_matrix[iz, i] = np.sum(valid == pid_type)*100 / total

    # ==== 修正邊界 ====
    x_edges = np.arange(len(class_names)+1) - 0.5
    y_edges = np.append(gz, gz[-1]+(gz[-1]-gz[-2]))
    y_centers = (y_edges[:-1] + y_edges[1:]) / 2

    fig, ax = plt.subplots(figsize=(9, 6))
    pc = ax.pcolormesh(x_edges, y_edges, ratio_matrix, cmap=cmap_name, vmin=0, vmax=100, shading='auto')
    cbar = plt.colorbar(pc, ax=ax)
    cbar.set_label("比例(%)", fontproperties=myfont)
    cbar.set_ticks([0,20,40,60,80,100])
    cbar.ax.set_yticklabels([f"{int(x)}%" for x in cbar.get_ticks()])
    ax.set_ylabel("高度 (km)", fontproperties=myfont)
    ax.set_title("hydro_class [%]", fontproperties=title_font)
    ax.set_xticks(np.arange(len(class_names)))
    ax.set_xticklabels(class_names, fontproperties=myfont)

    # ======= 每格加比例數字 =======
    for iz in range(nz):
        for ix in range(len(pid_types)):
            val = ratio_matrix[iz, ix]
            percent = f"{val:.1f}"
            font_color = 'white' if pc.norm(val) > 0.5 * pc.norm.vmax else 'black'
            txt = ax.text(
                ix, y_centers[iz], percent,
                ha='center', va='center',
                color=font_color,
                fontsize=9, fontproperties=myfont
            )
            txt.set_path_effects([
                path_effects.Stroke(linewidth=2, foreground='white'),
                path_effects.Normal()
            ])

    plt.tight_layout()
    plt.savefig(save_path_heatmap, dpi=150)
    print(f"✅ 儲存熱圖：{save_path_heatmap}")
    plt.close()
