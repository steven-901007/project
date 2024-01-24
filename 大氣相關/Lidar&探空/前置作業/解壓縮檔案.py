import gzip
import glob
import rarfile
import os


locate = '松山'
year = '108'
path = "C:/Users/steve/python_data/lidar&sonding/" #資料夾存放位置


def fileset(path):    #建立資料夾
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 
    else:
        print(path + " 建立過了")  

fileset(path+'lidar_raw_data')
fileset(path+'lidar_raw_data/'+locate)
fileset(path+'lidar_raw_data/'+locate+'/'+year)

def un_gf(file_name):   #解壓縮gz檔(若無錯誤檔案則不會顯示東西)
    f_name = file_name.replace(".gz","")
    g_file = gzip.GzipFile(file_name)
    try:
        open(f_name,"wb+").write(g_file.read())
        g_file.close()
        os.remove(file_name)
    except:
        g_file.close()
        os.remove(file_name)
        print(file_name + 'error')
        

errorfile = []
months  =glob.glob(path+'lidar_raw_data/'+locate+'/'+year+'/**')
for month in months:
    # print(month)
    days  =glob.glob(month+"/**")
    # print(days)
    for day in days:
        hours = glob.glob(day+'/wind_reconstruction_data/**')
        for hour in hours:
            # print(hour)    
            hour = hour+'/**.gz'
            result  =glob.glob(hour)
            # print(result)
            for f in result: 
                un_gf(f)    


if len(errorfile) > 1:
    print('以下為解壓縮時出現錯誤的日期')
    print(errorfile)

