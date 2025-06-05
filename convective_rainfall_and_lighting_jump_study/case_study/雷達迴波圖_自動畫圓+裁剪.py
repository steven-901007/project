import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import pandas as pd
from glob import glob
import os
from tqdm import tqdm


## 因為地圖似乎有被扭曲 因此直接找要畫的位置 把target x、y 改成那個數字就好 記得要開plt.show


year = '2021' #年分
month = '06' #月份(01~12)
day = '08'
time_start = 13 #(00~23)
time_end = 17 #(00~23)

dis = 36
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
station_name = '01D180'
# station_name = '01A430'


##測站位置(圖上的)
target_x = 1939.4
target_y = 1436

##剪裁範圍
cut_or_not = True ##是否要剪裁
x_min = 1527
x_max = 2222
y_min = 1155
y_max = 1800

##是否在調整座標等等數值
Adjustment = True



def fileset(path):    #建立資料夾
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 

##測站real name
station_name_lon_lat_path = f"{data_top_path}/雨量資料/測站資料/{year}_{month}.csv"
station_name_lon_lat_datas = pd.read_csv(station_name_lon_lat_path)
station_name_lon_lat_data = station_name_lon_lat_datas[station_name_lon_lat_datas['station name'] == station_name]
target_realname = station_name_lon_lat_data['station real name'].iloc[0]

##時間
time_start = str(time_start).zfill(2)
time_end = str(time_end).zfill(2)
fileset(f"{data_top_path}/CWA圖/雷達迴波/{year}{month}{day}{time_start}00{time_end}00_{target_realname}測站個案圖/circle_draw")


if cut_or_not == True:
    target_x = target_x - x_min
    target_y = target_y - y_min

result = glob(f"{data_top_path}/CWA圖/雷達迴波/{year}{month}{day}{time_start}00{time_end}00_{target_realname}測站個案圖/rawdata/**.png")

for img_path in tqdm(result, desc='地圖繪製中...'):
    # print(img_path)
    save_data_name = os.path.basename(img_path.split('.')[0])
    save_data_name = save_data_name.split('_')[-1][8:]
    # 讀取圖片
    img = Image.open(img_path)
    img_array = np.array(img)

    # 建立畫布
    fig, ax = plt.subplots()

    if cut_or_not == True:
        img_array = img_array[y_min:y_max, x_min:x_max]

    ax.imshow(img_array)



    # 標記點
    ax.plot(target_x,target_y, 'ro', markersize=3)  # 紅色點
    ##畫圓
    circle = plt.Circle((target_x, target_y), 110, color='blue', fill=False, linewidth=1.5)
    ax.add_patch(circle)


    ##左上角加上時間
    plt.text(30,80,save_data_name, fontsize=22,bbox=dict(facecolor='white', alpha=1))


    ax.axis('off')

    # 儲存結果圖
    output_path = f"{data_top_path}/CWA圖/雷達迴波/{year}{month}{day}{time_start}00{time_end}00_{target_realname}測站個案圖/circle_draw/{save_data_name}.png"
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)


    if Adjustment == True:
    # #調整座標位置用
        plt.show()
        break

    plt.close()


