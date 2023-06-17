from netCDF4 import Dataset
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import math
from math import *
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.colors as mcolors

path = "C:/Users/steven.LAPTOP-8A1BDJC6/Downloads/a.nc"
dst = Dataset(path, mode='r', format="netCDF4")
# print(dst.variables.keys())
nb = 0
for i in dst.variables.keys():
    data = dst.variables[i][:]
    # print(str(nb)+','+i+str(data.shape))  #資料名稱(一維資料筆數,二維資料筆數,三維資料筆數)
    nb += 1
HGTs = dst.variables['HGT'][:]

# print(HGTs.shape)

HGT = HGTs[0] #最底層的U

# print(HGT)
# print(len(HGT))

R210 = range(210)
lv = [0,100]

plt.rcParams['font.sans-serif'] = [u'MingLiu'] #細明體
plt.rcParams['axes.unicode_minus'] = False #設定中文

fig1,axes1 = plt.subplots(1,1)

a= axes1.contourf(R210,R210,HGT,levels = lv)
plt.colorbar(a)
plt.title('地型')


    
plt.show()