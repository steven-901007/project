from openpyxl import Workbook ,load_workbook
from glob import glob
import math
import numpy as np
import time as T
import os
import pandas as pd

day = '2019-01-01' #時間
locate_number = 46692 #站號

start_time = T.time()

def fileset(path):    #建立資料夾
    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立") 
    else:
        print(path + " 建立過了")  


year = day[:4]
month = day[5:7]
date = day[8:]
# print(date)
path = "C:/Users/steve/python_data/lidar&sonding/sonding_raw_data/BANQIAO_Sounding/"+year+"/"+month+"/"+str(locate_number)+"-"+year+month+date+"00.shr.txt"

inf = pd.read_csv(path)
print(inf)