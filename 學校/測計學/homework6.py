import re
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from math import *
import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.cm as cm

path_1 = "G:/我的雲端硬碟/大氣/測計學/homework6/HW6/edt2_20231113_0555.txt"

delimiter_pattern = re.compile(r'\s+|\n')
elements = []
with open(path_1, 'r') as file:
    for line in file:
        # 使用正則表達式來分割每一行
        element = re.split(delimiter_pattern, line.strip())
        # print(element)
        elements.append(element)
# print(elements)
Y = []
inf_1 = [[]for i in range(8)] #height,T,RH,P,wind_velocity,wind_dic,U,V
for i in range(6,len(elements),10):
    Y.append(1)
    inf_1[0].append(elements[i][2]) #height
    # inf_1[1].append(elements[i][4]) #T
    # inf_1[2].append(elements[i][5]) #RH
    # inf_1[3].append(elements[i][3]) #P
    wv = float(elements[i][8])
    wd = float(elements[i][7])
    inf_1[4].append(wv) #winv
    inf_1[5].append(wd) #wind
    inf_1[6].append(-wv*np.cos(wd*np.pi/180))
    inf_1[7].append(-wv*np.sin(wd*np.pi/180))
# print(inf_1)



# mode = 6
# path_2 = "G:/我的雲端硬碟/大氣/測計學/homework6/HW6/LoRa_20231113_062740.csv"
# df = pd.read_csv(path_2,encoding = 'BIG5',header= None)
# print(df[df[1] == mode])

# X = []
# inf_2 = [[]for i in range(8)] #height,T,RH,P,wind_velocity,wind_dic
# for i in range(len(df[df[1] == mode])):
#     X.append(i)
# inf_2[0].append(df[df[1] == mode][9]/100) #height
# inf_2[1].append(df[df[1] == mode][3]/100) #T
# inf_2[2].append(df[df[1] == mode][4]/100) #RH
# inf_2[3].append(round(df[df[1] == mode][5]/100)) #P
# inf_2[4].append(df[df[1] == mode][15]) #winv
# inf_2[5].append(df[df[1] == mode][16]/100) #wind
# # inf_2[6].append(df[df[1] == mode][7]) #經
# # inf_2[7].append(df[df[1] == mode][8]) #偉

# print(inf_2)
# print(len(elements))
# print(elements[len(elements)-1][2])




# for i in range(1,6):
#     fig = plt.figure() #底圖(一張空白map可以在上面自行加上各種ax)
#     ax = fig.add_subplot()
#     ax.scatter(Y,inf_1[i],color = 'blue',s=10)
#     # ax.scatter(X,inf_2[i],color = 'blue',s=10)
#     if i == 0:
#         plt.title('height')
#     elif i == 1:
#         plt.title('T')
#     elif i == 2:
#         plt.title("RH")
#     elif i == 3:
#         plt.title("P")
#     elif i == 4:
#         plt.title("winv")
#     elif i == 5:
#         plt.title("wind")
#     # plt.xticks(X,df[df[1] == mode][0],rotation = 90)
# plt.show()



# -------繪圖區------------------

#新型為風標上色+colorbar,可以依照資料風速的極值差距繪圖，沒有固定的colorbar間距,要增加組數只需增加colorbax的顏色數量

colorbox = ['purple', 'blue', 'deepskyblue', 'turquoise', 'mediumturquoise', 'chartreuse','greenyellow', 'yellow', 'gold', 'orange', 'orangered']
Colors = []
Z = []
for i in range(len(inf_1[0])-1): #為風標上色

    u = inf_1[6][i]
    v = inf_1[7][i]
    if u != -999 and v != -999:
        z = round(sqrt(pow(u,2) +pow(v,2)),2)
    else:
        z = -999
    Z.append(z)
# print(Z)
n = (max(Z)-min(Z))/len(colorbox)+min(Z)

# ------colorbar-----------

level = []
for i in range(len(colorbox)+1):
    level.append(round(n*i,2))
    # print(round(n*i,2))
# print(level)
for i in range(len(inf_1[0])-1):
    for j in range(len(level)):
        if level[j]<Z[i]<=level[j+1]:
            Colors.append(colorbox[j])
        elif Z[i] == -999:
            Colors.append('w')

# print(Colors)

nlevel = len(level)
cmap1 = mpl.colors.ListedColormap(colorbox, N=nlevel)
cmap1.set_over('fuchsia')
cmap1.set_under('black')
norm1 = mcolors.Normalize(vmin=min(level), vmax=max(level))
norm1 = mcolors.BoundaryNorm(level, nlevel, extend='max')
im = cm.ScalarMappable(norm=norm1, cmap=cmap1)
cbar1 = plt.colorbar(im, extend='both', ticks=level)
# ------colorbar-----------



plt.rcParams['font.sans-serif'] = [u'MingLiu'] #細明體
plt.rcParams['axes.unicode_minus'] = False 

plt.barbs(Y,inf_1[0],inf_1[6],inf_1[7],color = Colors)
plt.title('單位:m/s')
plt.show()