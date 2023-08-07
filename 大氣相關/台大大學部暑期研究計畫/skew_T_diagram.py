import pandas as pd
import metpy.calc as mpcalc
from metpy.plots import SkewT
from metpy.units import units
import matplotlib.pyplot as plt
from scipy.signal import medfilt
import numpy as np

station = '46692'
time = '2022080500'
file = "C:/Users/steve/Desktop/python相關資料/NTU探空/sounding/"+time[:8]+"/"+station+"-"+time+".edt.txt"

data = []
with open(file,encoding='utf-8',errors='replace') as file: 
    lines = file.readlines() 
    data = [line.strip().split() for line in lines] 
data = [[item.rstrip(',') for item in row] for row in data]
data.remove(data[0])
data.remove(data[0])
# print(data)
df = pd.DataFrame(data[1:],columns=data[0])
# print(df['P'])

df = df.apply(pd.to_numeric, errors='coerce')# 使用 NaN 替换无效的数据（例如，'////////'）


df = df.dropna(how='all') # 删除所有值均为 NaN 的行
#將下落的資料移除
df =  df.loc[df['Ascent'].astype(int)>=0] #保留特定的數據
#查看一下数据里面的信息
# df.info()


# print(df['T'])
df['WS'] = df['WS'].astype(float)
df['WD'] = df['WD'].astype(float)

df['T'] = df['T'].astype(float)
df['U'] = df['U'].astype(float)
df['dewpoint'] = df['T']-((100-df['U'])/5)


#读取各类数据，并进行单位转化
p = df['P'].values * units.hPa
T = df['T'].values * units.degC
Td = df['dewpoint'].values * units.degC
wind_speed = df['WS'].values * units.knots
wind_dir = df['WD'].values * units.degrees
u, v = mpcalc.wind_components(wind_speed, wind_dir)


#--------------繪圖------------------

#背景圖

fig = plt.figure(figsize=(9, 9))
skew = SkewT(fig, rotation=45)
smoothed_p = medfilt(p, kernel_size=3)


skew.ax.set_ylim(1050, 100)
skew.ax.set_xlim(-30, 40)

skew.ax.set_ylabel('Height/hPa')
skew.ax.set_xlabel('T/(℃)')

skew.plot_dry_adiabats() #乾絕熱(位溫線) 紅色
skew.plot_moist_adiabats() #濕絕熱 藍色
skew.plot_mixing_lines() #等混和比 綠色



#溫度露點曲線
skew.plot(p, T, 'blue') #溫度
skew.plot(p, Td, 'r') #露點溫度


#風標設定

# 設定間距
spacing = 100  

# 计算需要绘制的行索引
idx = np.arange(0, len(p), spacing)

# 繪製風標
skew.plot_barbs(p[idx], u[idx], v[idx])



#計算變數
def cl_h(tg):
    return str(round(float(str(tg)[:str(round(tg)).index('h')])))
def cl_d(tg):
    return str(round(float(str(tg)[:str(round(tg)).index('d')]),1))
td0 = str(round(df['T'][0]-((100-df['U'][0])/5),1))
#LCL
lcl_p,lcl_t = mpcalc.lcl(p[0], T[0], Td[0])
# print(lcl_p)

if str(lcl_p)[:3] == 'nan':
    lcl = 'None'
else:
    lcl = cl_h(lcl_p)+'hPa'
# LFC
lfc_p, lfc_t = mpcalc.lfc(p, T, Td,which='bottom')
# print(lfc_p,lfc_t)

if str(lfc_p)[:3] == 'nan':
    lfc = 'None'
else:
    lfc = cl_h(lfc_p) +'hPa'

el_p, el_t = mpcalc.el(p, T, Td)
# print(el_p)

if str(el_p)[:3] == 'nan':
    el = 'None'
else:
    el = cl_h(el_p) +'hPa'

tti =  mpcalc.total_totals_index(p,T,Td) #總指標
# print(tti)
if str(tti)[:3] == 'nan':
    tti = 'None'
else:
    tti = cl_d(tti)

#地面氣塊抬升的模擬線
prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
skew.plot(p, prof, 'k', linewidth=2)


li = mpcalc.lifted_index(p,T,prof) # 抬升指數
print(li)
if str(li)[:3] == 'nan':
    li = 'None'
else:
    li = str(round(float(str(li)[:str(li).index('d')][1:len(str(li)[:str(li).index('d')])-2]),1))



#画能量
skew.shade_cin(p, T, prof)
skew.shade_cape(p, T, prof)
# cin_area = skew.ax.get_children()[0].get_facecolor()[0]
# print(cin_area)


#計算變數，數據文字
text = r'$P_{0}$='+str(df['P'][0])+r' $T_{0}$='+str(df['T'][0])+r' $Td_{0}$='+td0+'\nL.C.L= '+lcl+'\nL.F.C= '+lfc+'\nE.L= '+el+'\nTTI= '+tti+'\nLI= '+li

plt.text(-43,103,text, horizontalalignment='right',verticalalignment='top',backgroundcolor='w',multialignment='left')    



plt.title('station:'+station+'  time:'+time[:4]+'/'+time[4:6]+'/'+time[6:8]+' '+time[8:10]+':00')
plt.show()