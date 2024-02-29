import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from openpyxl import load_workbook

wb = load_workbook("C:/Users/steve/python_data/thermodynamics/CA1/Temperature.xlsx")
ws = wb['Temperature']
X = ws.max_column-1
Y = ws.max_row-1
print(X,Y)

DATA = []
P = []
H = []
#有效資料認證
for h in range(Y-1):
    data_list = []
    for t in range(X-2):
        data = ws.cell(h+2,t+3).value
        # print(data)        
        data_list.append(data)
    if data_list.count(-999) == 0:
        DATA.append(data_list)
        P.append(ws.cell(h+2,1).value)
        H.append(ws.cell(h+2,2).value)
# print(DATA) [T]
# print(P) [pa]
# print(H) [m]

        2021/03/01 資料處理完畢剩下繪圖


#繪圖區

#散佈圖
plt.rcParams['font.sans-serif'] = [u'MingLiu'] #細明體
plt.rcParams['axes.unicode_minus'] = False 
fig = plt.figure()
ax = fig.add_subplot()

hight = []
for i in range(Y):
    hight.append(ws.cell(i+2,1).value/1000)
# print(hight)
            
for i in range(X):
    data = []
    for h in range(Y):
        data.append(ws.cell(h+2,i+2).value)
    # print(data)
    ax.plot(data,hight)



data_ave = []
for h in range(Y):
    sum = 0
    for t in range(X):
        sum+= ws.cell(h+2,t+2).value
    data_ave.append(sum/X)
    
ax.plot(data_ave,hight,color ='black',lw = 3,label = 'average')
ax.tick_params(axis='x', labelsize=12) 
ax.tick_params(axis='y', labelsize=12) 
plt.legend()
plt.xlabel('Temperature[°C]',fontsize = 20)
plt.ylabel('Height[km]',fontsize = 20)
plt.title('tpe20110802cln\n苗栗站(24.56457N,120.82458E)',fontsize = 20)
plt.show()