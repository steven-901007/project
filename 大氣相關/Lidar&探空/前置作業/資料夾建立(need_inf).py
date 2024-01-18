import os


locate = '松山'
year = '108'

day = ""#目標月日(若處理全年資料則不填)

path = "C:/Users/steve/python_data/lidar&sonding/" #資料夾存放位置

def fileset(path):    #建立資料夾

    if not os.path.exists(path):
        os.makedirs(path)
        print(path + " 已建立")
    else:
        print(path + " 建立過了")

fileset(path+'/lidar_need_information')
fileset(path+'/lidar_need_information/'+locate)
fileset(path+'/lidar_need_information/'+locate+"/"+year)
