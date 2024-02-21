import re
import math
import numpy as np
import matplotlib.pyplot as plt
from math import *
import matplotlib as mpl
import matplotlib.colors as mcolors
import matplotlib.cm as cm
path = "G:/我的雲端硬碟/學校/大氣/測計學/homework5/HW5/TD105_data_sample.txt"

delimiter_pattern = re.compile(r'\s+|\n')
elements = []
with open(path, 'r') as file:
    for line in file:
        # 使用正則表達式來分割每一行
        element = re.split(delimiter_pattern, line.strip())
        if element != ['']:
            if len(element) == 4:
                elements.append(element)
                # print(element)

# print(elements)
Hight = []
X = []

wind_inf_U_V = [[],[]] #[U,V]
for i in range(len(elements)-1):
    Z = int(elements[i][1])
    A = float(elements[i][2])
    E = float(elements[i][3])
    Z1 = int(elements[i+1][1])
    A1 = float(elements[i+1][2])
    E1 = float(elements[i+1][3])
    hight = 150/60*Z
    Hight.append(hight)
    X.append(1)
    # print(Z,A,E)-
    # print(Z1,A1,E1)
    u = round(Z1/np.tan(E1*np.pi/180)*np.sin(A1*np.pi/180) - Z/np.tan(E*np.pi/180)*np.sin(A*np.pi/180),3)
    v = round(Z1/np.tan(E1*np.pi/180)*np.cos(A1*np.pi/180) - Z/np.tan(E*np.pi/180)*np.cos(A*np.pi/180),3)
    wind_inf_U_V[0].append(u)
    wind_inf_U_V[1].append(v)
    # print(Z,hight,u,v)

U = wind_inf_U_V[0]
V = wind_inf_U_V[1]

#新型為風標上色+colorbar,可以依照資料風速的極值差距繪圖，沒有固定的colorbar間距,要增加組數只需增加colorbax的顏色數量

colorbox = ['purple', 'blue', 'deepskyblue', 'turquoise', 'mediumturquoise', 'chartreuse','greenyellow', 'yellow', 'gold', 'orange', 'orangered']
Colors = []
Z = []
for i in range(len(Hight)-1): #為風標上色

    u = U[i]
    v = V[i]
    if u != -999 and v != -999:
        z = round(sqrt(pow(u,2) +pow(v,2)),2)
    else:
        z = -999
    Z.append(z)
print(Z)
n = (max(Z)-min(Z))/len(colorbox)+min(Z)

level = []
for i in range(len(colorbox)+1):
    level.append(round(n*i,2))
    # print(round(n*i,2))
print(level)
for i in range(len(Hight)-1):
    for j in range(len(level)):
        if level[j]<Z[i]<=level[j+1]:
            Colors.append(colorbox[j])
        elif Z[i] == -999:
            Colors.append('w')

print(Colors)


# ------colorbar-----------
# level = [0,1,2,3,4,5,6,7,8,9,10,11]
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

plt.barbs(X,Hight,U,V,color = Colors)
plt.title('單位:m/s')
plt.show()