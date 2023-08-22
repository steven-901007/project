import pandas as pd
import metpy.calc as mpcalc
from metpy.plots import SkewT
from metpy.units import units
import matplotlib.pyplot as plt
from scipy.signal import medfilt
import numpy as np

#metpy要用1.4.1版本CIN的地方才會正確

station = '46692'
time = '2022051500'
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
def cl_j(tg):
    return str(round(float(str(tg)[:str(round(tg)).index('j')]),1))
def cl_d(tg):
    return str(round(float(str(tg)[:str(round(tg)).index('d')]),1))
def cl_del_d(tg):
    return str(round(float(str(tg)[:str(tg).index('d')][1:len(str(tg)[:str(tg).index('d')])-2]),1))
td0 = str(round(df['T'][0]-((100-df['U'][0])/5),1))

#LCL(抬升凝結高度)
lcl_p,lcl_t = mpcalc.lcl(p[0], T[0], Td[0])
# print(lcl_p,lcl_t)

if str(lcl_p)[:3] == 'nan':
    lcl_p = '\nL.C.L= None'
    lcl_t = '\n$T_{LCL}$= None'
else:
    lcl_p = '\nL.C.L= '+cl_h(lcl_p)+'hPa'
    lcl_t = '\n$T_{LCL}$='+cl_d(lcl_t)+r'$\degree$C'

#CCL(對流凝結高度)
ccl_p,ccl_t,t_c = mpcalc.ccl(p,T,Td)
# print(ccl_p,ccl_t,t_c)
if str(ccl_p)[:3] == 'nan':
    ccl_p = '\nC.C.L= None'
    ccl_t = '  $T_{CCL}$= None'
else:
    ccl_p = '\nC.C.L= '+cl_h(ccl_p)+'hPa'
    ccl_t = '  $T_{CCL}$='+cl_d(ccl_t)+r'$\degree$C'

# LFC(自由對流高度)
lfc_p, lfc_t = mpcalc.lfc(p, T, Td,which='bottom')
# print(lfc_p,lfc_t)
if str(lfc_p)[:3] == 'nan':
    lfc_p = '\nL.F.C= None'
    lfc_t = '\n$T_{LFC}$= None'
else:
    lfc_p = '\nL.F.C= '+cl_h(lfc_p) +'hPa'
    lfc_t = '\n$T_{LFC}$='+cl_d(lfc_t) +r'$\degree$C'

#EL(平衡高度)
el_p, el_t = mpcalc.el(p, T, Td)
# print(el_p)
if str(el_p)[:3] == 'nan':
    el_p = '\nE.L= None'
    el_t = '  $T_{EL}$= None'
else:
    el_p = '\nE.L= '+cl_h(el_p) +'hPa'
    el_t = '  $T_{EL}$='+cl_d(el_t) +r'$\degree$C'

#K indx(K指標)
k_index = mpcalc.k_index(p,T,Td)
# print(k_index)
if str(k_index)[:3] == 'nan':
    k_index = '\nK. INDX= None'
else:
    k_index = '\nK. INDX= '+cl_d(k_index)

#TTL(總指標)
tti =  mpcalc.total_totals_index(p,T,Td) 
# print(tti)
if str(tti)[:3] == 'nan':
    tti = '  TOTAL.= None'
else:
    tti = '  TOTAL.= '+cl_d(tti)

#地面氣塊抬升的模擬線
prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
skew.plot(p, prof, 'k', linewidth=2)

#LI(抬升指數)
li = mpcalc.lifted_index(p,T,prof) # 抬升指數
# print(li)
if str(li)[:3] == 'nan':
    li = '\nLifted INDX.= None'
else:
    li = '\nLifted INDX.= '+cl_del_d(li)

#Showalter index
si = mpcalc.showalter_index(p,T,Td)
# print(si)
if str(si)[:3] == 'nan':
    si = '\nShowalter INDX.= None'
else:
    si = '\nShowalter INDX.= '+cl_del_d(si)

#Sweat index
sweatindex = mpcalc.sweat_index(p,T,Td,wind_speed,wind_dir)
# print(sweatindex)
if str(sweatindex)[:3] == 'nan':
    sweatindex = '\nSWEAT INDX.= None'
else:
    sweatindex = '\nSWEAT INDX.= '+cl_del_d(sweatindex)

#CAPE CIN

cape,cin = mpcalc.cape_cin(p,T,Td,prof)
# print(cape,cin)
if str(cape)[:3] == 'nan':
    cape = '\nCAPE= None'
else:
    cape = '\nCAPE= '+cl_j(cape)+ r'$m^2s^2$'
if str(cin)[:3] == 'nan':
    cin = '\nCIN= None'
else:
    cin = '\nCIN= '+cl_j(cin)+ r'$m^2s^2$'


#画能量
skew.shade_cin(p, T, prof)
skew.shade_cape(p, T, prof)
# cin_area = skew.ax.get_children()[0].get_facecolor()[0]
# print(cin_area)


#計算變數，數據文字
text = r'$P_{0}$='+str(df['P'][0])+r'$T_{0}$='+str(df['T'][0])+r'$Td_{0}$='+td0+lcl_p+ccl_p+lfc_p+el_p+lcl_t+ccl_t+lfc_t+el_t+k_index+tti+li+si+sweatindex+cape+cin

plt.text(-43,103,text, horizontalalignment='right',verticalalignment='top',backgroundcolor='w',multialignment='left')    



plt.title('station:'+station+'  time:'+time[:4]+'/'+time[4:6]+'/'+time[6:8]+' '+time[8:10]+':00')
plt.show()