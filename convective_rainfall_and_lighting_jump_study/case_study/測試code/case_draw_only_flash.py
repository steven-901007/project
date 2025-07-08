import pandas as pd
import matplotlib.pyplot as plt
import datetime
from tqdm import tqdm
from matplotlib.dates import DateFormatter, MinuteLocator
import os
from glob import glob


def fileset(path):    #建立資料夾
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 


##統計計算(mean+2std)
def statistics(a,row):
    if row['SR6'] > row['mean'] + a*row['std']:
        return 1
    else:
        return 0

##計算某個SR裡的數值
def count_funtion(SR_time_late,row,data):
    start_time = row['data time'] + pd.Timedelta(minutes=int(SR_time_late)-1)
    end_time = start_time + pd.Timedelta(minutes=5)
    # if SR_time_late == 1:
    # print(row['if_lj_time'],start_time,end_time)

    return data[((data['data time'] >= start_time) & (data['data time'] < end_time))]['flash_count'].sum()

##maxma_rain_data填色
def assign_status(x):
    if x >= 10:
        return 'r'
    else:
        return 'g'


def case_draw(year,month,day,time_start,time_end,dis,station_name,data_top_path,alpha,flash_source):
    pd.set_option('display.max_rows', None)

    #將時間的type改成時間型態
    time_start_time_type = datetime.datetime(int(year),int(month),int(day),time_start)
    time_end_time_type = datetime.datetime(int(year),int(month),int(day),time_end)
    #生成時間df
    full_time_range = pd.date_range(start=time_start_time_type, end=time_end_time_type, freq='min')# 生成完整的每分鐘時間範圍
    full_time_df = pd.DataFrame(full_time_range, columns=['data time'])# 建立一個 DataFrame 包含完整的時間範圍

    ##測站資料
    data_path = f"{data_top_path}/rain_data/測站資料/{year}_{month}.csv"
    position_data = pd.read_csv(data_path)
    point_real_name = position_data[position_data['station name'] == station_name]['station real name'].iloc[0]
    ##資料讀取
    case_root_path =  f"{data_top_path}/case_study/{station_name}/{dis}_{flash_source}_{year}{month}{day}_{str(time_start).zfill(2)}00to{str(time_end).zfill(2)}00"
    rain_data_path = case_root_path + '/rain_raw_data.csv'
    flash_data_path = case_root_path + f'/{flash_source}_flash_data.csv'
    rain_data = pd.read_csv(rain_data_path)
    flash_data = pd.read_csv(flash_data_path)

    flash_data['data time'] = pd.to_datetime(flash_data['data time'])
    # print(flash_data)


    # print(flash_data)
    # print(full_time_df)

    ## 每分鐘flash_data
    flash_data_for_every_min_df = pd.merge(flash_data,full_time_df,on='data time', how='outer').fillna(0)# 與原始資料合併，缺少的時間點補上 count = 0
    # print(flash_data_for_every_min_df)

    ## lighting jump and SR6
    flash_data_for_lighting_jump_and_SR6_df = flash_data.copy()
    flash_data_for_lighting_jump_and_SR6_df = pd.merge(flash_data_for_lighting_jump_and_SR6_df,full_time_df,on='data time', how='outer').fillna(0)
    
    #建立if lj time (如果有lj要用這個)
    flash_data_for_lighting_jump_and_SR6_df['if_lj_time'] = flash_data_for_lighting_jump_and_SR6_df['data time'] + pd.Timedelta(minutes=10)
    #建立SR1~6
    for SR in range(1,7):
        flash_data_for_lighting_jump_and_SR6_df['SR' + str(SR)] = flash_data_for_lighting_jump_and_SR6_df.apply(lambda row: count_funtion(SR, row,flash_data_for_lighting_jump_and_SR6_df), axis=1)
    # print(flash_data_for_lighting_jump_and_SR6_df)
    flash_data_for_SR6_df = flash_data_for_lighting_jump_and_SR6_df.copy()
    flash_data_for_lighting_jump_and_SR6_df = flash_data_for_lighting_jump_and_SR6_df[(flash_data_for_lighting_jump_and_SR6_df[['SR1', 'SR2', 'SR3', 'SR4', 'SR5']] != 0).all(axis=1)]#刪除SR1 ～SR5 任意比 = 0的資料
    # #計算mean and std
    flash_data_for_lighting_jump_and_SR6_df['mean'] = flash_data_for_lighting_jump_and_SR6_df[['SR1', 'SR2', 'SR3', 'SR4', 'SR5']].mean(axis=1)
    flash_data_for_lighting_jump_and_SR6_df['std'] = flash_data_for_lighting_jump_and_SR6_df[['SR1', 'SR2', 'SR3', 'SR4', 'SR5']].std(ddof=0,axis=1)

    flash_data_for_lighting_jump_and_SR6_df['lighting_jump_or_not'] = flash_data_for_lighting_jump_and_SR6_df.apply(lambda row: statistics(alpha, row), axis=1)

    flash_data_for_lighting_jump_df = flash_data_for_lighting_jump_and_SR6_df[flash_data_for_lighting_jump_and_SR6_df['lighting_jump_or_not'] == 1][['if_lj_time','SR6']]

    
    # flash_data_for_SR6_df = pd.merge(flash_data_for_lighting_jump_and_SR6_df,full_time_df,on='data time', how='outer').fillna(0)
    # print(flash_data_for_lighting_jump_and_SR6_df)



    ##總雨量 and 單站最大雨量 and >10mm/min的測站個數

    total_rain_data = rain_data[['data time','rain data']].groupby(['data time'])['rain data'].sum().reset_index()
    total_rain_data['data time'] = pd.to_datetime(total_rain_data['data time'])
    total_rain_data = pd.merge(total_rain_data,full_time_df,on='data time', how='outer').fillna(0)

    maxma_rain_data = rain_data[['data time','rain data']].groupby(['data time'])['rain data'].max().reset_index()
    maxma_rain_data['data time'] = pd.to_datetime(maxma_rain_data['data time'])
    maxma_rain_data = pd.merge(maxma_rain_data,full_time_df,on='data time', how='outer').fillna(0)
    maxma_rain_data['color'] = maxma_rain_data['rain data'].apply(assign_status)
    # print(maxma_rain_data['color'])

    filtered_data = rain_data[rain_data['rain data'] >= 10]
    count_rain_data = filtered_data[['data time', 'rain data']].groupby(['data time'])['rain data'].count().reindex()
    count_rain_data.index = pd.to_datetime(count_rain_data.index)
    count_rain_data = count_rain_data.reset_index()
    count_rain_data.columns = ['data time', 'count']
    count_rain_data = pd.merge(count_rain_data,full_time_df,on='data time', how='outer').fillna(0)
    # print(rain_data)
    # print(count_rain_data)

    
    # this_case_prefigurance_hit_persent_paths = f"{data_top_path}/case_study/前估命中個案/{year}_{month}/{station_name}_**.csv"
    # # print(glob(this_case_prefigurance_hit_persent_paths))    
    # this_case_prefigurance_hit_persent_path = glob(this_case_prefigurance_hit_persent_paths)[0]
    # this_case_prefigurance_hit_persent_datas = pd.read_csv(this_case_prefigurance_hit_persent_path,parse_dates=['time data'])['time data']
    # this_case_prefigurance_hit_persent_data = this_case_prefigurance_hit_persent_datas[(this_case_prefigurance_hit_persent_datas >= time_start_time_type) & (this_case_prefigurance_hit_persent_datas <= time_end_time_type)]
    # this_case_prefigurance_hit_count = this_case_prefigurance_hit_persent_data.count()

    # print(time_start_time_type,time_end_time_type)

    # 繪製圖表
    fig, ax1 = plt.subplots(figsize = (19,9))

    plt.rcParams['font.sans-serif'] = [u'MingLiu'] #細明體
    plt.rcParams['axes.unicode_minus'] = False #設定中文
    
    # 繪製每分鐘閃電量，右側y軸
    ax2 = ax1.twinx()
    ax2.plot(flash_data_for_every_min_df['data time'], flash_data_for_every_min_df['flash_count'], c='skyblue', zorder=3, label='1-min ICandCG') #每分鐘閃電量
    # ax2.bar(total_rain_data['data time'],total_rain_data['rain data'],color = 'lime', width=0.001,zorder=1,label = '總雨量')
    # ax2.bar(maxma_rain_data[maxma_rain_data['color'] == 'g']['data time'], 
    #     maxma_rain_data[maxma_rain_data['color'] == 'g']['rain data'],
    #     color ='g', width=0.001, zorder=2,label = '最大單站雨量')
    # ax2.bar(maxma_rain_data[maxma_rain_data['color'] == 'r']['data time'], 
    #     maxma_rain_data[maxma_rain_data['color'] == 'r']['rain data'], 
    #     color='red', width=0.001, zorder=2, label='最大單站雨量>=10mm/10min')
    # ax2.bar(count_rain_data['data time'],count_rain_data['count']*10,color = 'black', width=0.0005, zorder=3,label = '>10mm站數(*10)')
    # ax2.axhline(10,c = "r" , ls = "--" , lw = 2)
    ax2.set_ylabel('雨量/1-min ICandCG',size = 20)
    # ax2.set_ylim(0,1100)
    
    

    # 繪製SR6和lighting jump的SR6，左側y軸
    # ax1.scatter(flash_data_for_lighting_jump_df['if_lj_time'], flash_data_for_lighting_jump_df['SR6'], c='red', s=2, zorder=1, label='jump threshold') #Lighting Jump的SR6
    # ax1.plot(flash_data_for_SR6_df['if_lj_time'], flash_data_for_SR6_df['SR6'], c='yellow', zorder=1, label='SR6') #SR6
    # ax1.set_ylim(-10)
    ax1.set_ylabel('SR6/jump threshold',size = 20)


    # 設置x軸標籤和旋轉角度
    ax1.xaxis.set_major_locator(MinuteLocator(byminute=range(0, 60, 10)))  # 每10分钟一个刻度
    ax1.xaxis.set_major_formatter(DateFormatter("%H:%M"))  # 格式化为时:分
    # ax1.grid(True, which='both', axis='x', linestyle='--', linewidth=0.5)  # 添加网格线
    plt.setp(ax1.get_xticklabels(), rotation=90)


    plt.title(f"測站：{point_real_name}({station_name})\n半徑：{dis}\n日期：{year}/{month}/{day} {str(time_start).zfill(2)}:00~{str(time_end).zfill(2)}:00\nflash source：{flash_source}")
    # plt.title(f"測站：{point_real_name}({station_name})\n日期：{year}/{month}/{day}\n時間{str(time_start).zfill(2)}:00~{str(time_end).zfill(2)}:00\n前估命中數：{this_case_prefigurance_hit_count}")
    fig.legend()

    # 顯示and儲存圖表
    pic_save_path = case_root_path + '/picture.png'

    
    # ##一次處理一個月資料用
    # case_root_path = f"{data_top_path}/case_study/{station_name}_{dis}_{year}{month}_{str(time_start).zfill(2)}00to{str(time_end).zfill(2)}00"
    # fileset(case_root_path)
    # pic_save_path = f"{case_root_path}/{year}{month}{day}.png" 
    
    # plt.savefig(pic_save_path, bbox_inches='tight', dpi=300)
    print(f"已生成照片：\n測站：{point_real_name}({station_name})\n半徑：{dis}\n日期：{year}/{month}/{day} {str(time_start).zfill(2)}:00~{str(time_end).zfill(2)}:00\nflash source：{flash_source}")    # plt.show()
    plt.show()
    


data_top_path = "C:/Users/steve/python_data/convective_rainfall_and_lighting_jump"
year = '2021' #年分
month = '06' #月份
day = '29'
time_start = 00
time_end = 23
dis = 36
alpha = 2 #統計檢定
flash_source = 'EN' # EN or TLDS
# station_name = 'O1P470' #前估max
# station_name = '466880' #板橋
# station_name = 'C0V800' #六龜
# station_name = '466920' #台北
station_name = '01P190'

case_draw(year,month,day,time_start,time_end,dis,station_name,data_top_path,alpha,flash_source)
