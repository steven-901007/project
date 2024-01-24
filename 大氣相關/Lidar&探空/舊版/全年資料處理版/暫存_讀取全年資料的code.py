from openpyxl import Workbook
import csv
import glob
import math
import numpy as np
import time as T
import os


locate = '松山'
year = '108'
confidence_level = 100


startTime = T.time()


def fileset(path):    #建立資料夾
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 
    else:
        print(path + " 建立過了")  

fileset('C:/Users/steve/python_data/lidar&sonding/one_year_version/'+locate+"/"+year+'/lidar_need_information')

months =glob.glob("C:/Users/steve/python_data/lidar&sonding/lidar_raw_data/" + locate + "/" + year + "/**")
for month in months:
    month = os.path.basename(month)
    # print(month)

    days = glob.glob("C:/Users/steve/python_data/lidar&sonding/lidar_raw_data/" + locate + "/" + year + "/"+month + "/**")
    for day in days:
        day = os.path.basename(day)
        # print(day)
    
        hours = glob.glob("C:/Users/steve/python_data/lidar&sonding/lidar_raw_data/" + locate + "/" + year + "/"+month + "/" + day + "/wind_reconstruction_data/**")
        for hour in hours:
            hour = os.path.basename(hour)
            # print(hour)
            fileset("C:/Users/steve/python_data/lidar&sonding/one_year_version/" + locate + "/" + year + "/lidar_need_information/" + month + "/" + day + "/" + hour)    #建立日期資料夾

            # minutes = glob.glob("C:/Users/steve/python_data/lidar&sonding/lidar_raw_data/" + locate + "/" + year + "/"+month + "/" + day + "/wind_reconstruction_data/" + hour + "/**")
            # for minute in minutes:
                # print(minute)