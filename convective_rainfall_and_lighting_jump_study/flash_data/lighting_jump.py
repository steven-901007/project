import pandas as pd
from glob import glob
from tqdm import tqdm
import os


year = '2021'     # 年分
month = '07'      # 月份
data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
alpha = 2         # 統計檢定
dis = 36          #檢定區半徑
data_source = 'EN'#閃電資料來源



# pd.set_option('display.max_rows', None)

##建立資料夾
def file_set(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
        print(file_path + " 已建立")
file_set(f"{data_top_path}/閃電資料/{data_source}/lighting_jump/{data_source}_{year}{month}_{dis}km")

# 計算 SR (閃電數累積值)
def calculate_sr(flash_datas, window=5):
    sr_list = []
    for i in range(len(flash_datas)):
        if i < window:  # 如果時間點少於窗口大小，則 SR 為 0
            sr_list.append(0)
        else:
            current_time = flash_datas.index[i]
            # 計算當前時間之前的 5 分鐘內的閃電數累積值
            prev_window_data = flash_datas['flash_count'].iloc[i-window:i]  # 取得前5分鐘的數據
            sr_value = prev_window_data.sum()  # 累積值
            sr_list.append(sr_value)
    return sr_list

# 補全缺失數據
def add_missing_data(flash_datas, window=5):
    new_rows = []
    for i in range(len(flash_datas)):
        current_time = flash_datas.index[i]
        # 往後看 5 分鐘內是否有資料
        for j in range(1, window+1):
            future_time = current_time + pd.Timedelta(minutes=j)
            if future_time not in flash_datas.index:
                # 如果這個未來的時間點不存在，則補上 flash_count = 0
                new_rows.append({'data time': future_time, 'flash_count': 0})

    # 將新補的資料添加到原始資料中
    if new_rows:
        new_df = pd.DataFrame(new_rows).set_index('data time')
        flash_datas = pd.concat([flash_datas, new_df]).sort_index()

    # 去除重複時間點的數據
    flash_datas = flash_datas[~flash_datas.index.duplicated(keep='first')]

    return flash_datas

# 判斷是否發生 LJ
def calculate_lj(flash_datas, window=5):
    lj_list = []
    for i in range(window, len(flash_datas)):
        prev_window_data = flash_datas['SR'].iloc[i-window:i]  # 取得前5筆資料，不包含當前資料
        
        # 確認前5筆資料中沒有 0 或 NaN
        if (prev_window_data == 0).any() or prev_window_data.isna().any():
            lj_list.append(2)  # 如果前5筆資料有0或NaN，則跳過
        else:
            sr_mean = prev_window_data.mean()  # 前5筆資料的平均值
            sr_std = prev_window_data.std(ddof=0)  # 前5筆資料的母體標準差 (ddof=0)
            threshold = sr_mean + alpha * sr_std  # 閾值 = mean + 2*std
            
            current_sr = flash_datas['SR'].iloc[i]  # 當前資料的SR
            
            # 當前 SR 大於 閾值，且當前 SR 不等於 0，則判定為 Lightning Jump
            if current_sr > threshold and current_sr != 0:
                lj_list.append(1)
            else:
                lj_list.append(0)
    
    # 對前 window 筆資料補 0，因為它們沒有足夠的資料進行判斷
    lj_list = [0] * window + lj_list
    
    return lj_list

# 將數據放入 DataFrame
result = glob(f"{data_top_path}/閃電資料/{data_source}/依測站分類/{data_source}_{year}{month}_{dis}km/**.csv")
for flash_data_path in tqdm(result,desc='data setting...'):
    # print(flash_data_path)
    station_name = os.path.basename(flash_data_path).split('.')[0]
    # print(station_name)

# 讀取數據
# station_name = '00H710'
# flash_data_path = f"{data_top_path}/閃電資料/依測站分類/{year}_{month}_{dis}km/{station_name}.csv"
    flash_datas = pd.read_csv(flash_data_path)

    # 將 'data time' 轉換為 datetime 格式並設置為索引
    flash_datas['data time'] = pd.to_datetime(flash_datas['data time'])
    flash_datas.set_index('data time', inplace=True)
    flash_datas.sort_index(inplace=True)

    # 補全缺失數據
    flash_datas = add_missing_data(flash_datas)

    # 計算 SR
    flash_datas['SR'] = calculate_sr(flash_datas)

    # 計算 LJ
    flash_datas['LJ'] = calculate_lj(flash_datas)

    # 顯示結果
    # print(flash_datas)
    save_data = flash_datas[flash_datas['LJ'] == 1].index
    if save_data.empty is False:
        save_data = pd.DataFrame(save_data)
        save_data.columns = ['LJ_time']
        # 保存結果
        output_path = f"{data_top_path}/閃電資料/{data_source}/lighting_jump/{data_source}_{year}{month}_{dis}km/{station_name}.csv"
        save_data.to_csv(output_path,index=False)

print(f"資料來源：{data_source}、Time：{year}{month}、dis：{dis}")
