import matplotlib.pyplot as plt
import numpy as np
import metpy.calc as mpcalc
from metpy.plots import SkewT
from metpy.units import units

# 定義初始條件
pressure = np.linspace(1000, 100, 100) * units.hPa
surface_temperature = 300 * units.kelvin  # 地表溫度
mixing_ratio = 15 * units('g/kg')  # 濕度

# 計算混合比
mixing_ratio = mixing_ratio.to('dimensionless')

# 計算露點溫度
dew_point_surface = mpcalc.dewpoint(mpcalc.vapor_pressure(pressure[0], mixing_ratio))

# 計算溫度剖面
temperature = mpcalc.dry_lapse(pressure, surface_temperature)

# 計算露點剖面
dew_point = np.full_like(temperature, dew_point_surface)

# 計算LCL
lcl_pressure, lcl_temperature = mpcalc.lcl(pressure[0], surface_temperature, dew_point_surface)

# 檢查壓力剖面，確保包含足夠的值來計算LFC和EL
if np.min(pressure.magnitude) > lcl_pressure.magnitude:
    raise ValueError("壓力剖面中沒有足夠的值來計算LFC和EL。請擴展壓力範圍。")

# 計算LFC和EL
try:
    parcel_profile = mpcalc.parcel_profile(pressure, surface_temperature, dew_point_surface)
    lfc_pressure, lfc_temperature = mpcalc.lfc(pressure, temperature, dew_point)
    el_pressure, el_temperature = mpcalc.el(pressure, temperature, dew_point)
except ValueError as e:
    print(f"計算LFC和EL時出錯: {e}")
    lfc_pressure, lfc_temperature = np.nan * units.hPa, np.nan * units.degC
    el_pressure, el_temperature = np.nan * units.hPa, np.nan * units.degC

# 繪製斜溫圖
fig = plt.figure(figsize=(10, 10))
skew = SkewT(fig, rotation=45)

# 添加溫度和露點溫度線
skew.plot(pressure, temperature.to('degC'), 'r', label='Temperature')
skew.plot(pressure, dew_point.to('degC'), 'g', label='Dew Point Temperature')

# 添加LCL點
skew.plot(lcl_pressure, lcl_temperature.to('degC'), 'ko', markerfacecolor='black', label='LCL')

# 添加LFC點
if not np.isnan(lfc_pressure.magnitude):
    skew.plot(lfc_pressure, lfc_temperature.to('degC'), 'bo', markerfacecolor='blue', label='LFC')

# 添加EL點
if not np.isnan(el_pressure.magnitude):
    skew.plot(el_pressure, el_temperature.to('degC'), 'go', markerfacecolor='green', label='EL')

# 添加parcel profile線
skew.plot(pressure, parcel_profile.to('degC'), 'k', label='Parcel Profile')

# 添加乾絕熱線
skew.plot_dry_adiabats()

# 添加濕絕熱線
skew.plot_moist_adiabats()

# 添加混合比線
skew.plot_mixing_lines()

# 標示LCL、LFC和EL
plt.text(lcl_pressure.m, lcl_temperature.m, 'LCL', verticalalignment='bottom', horizontalalignment='right')
if not np.isnan(lfc_pressure.magnitude):
    plt.text(lfc_pressure.m, lfc_temperature.m, 'LFC', verticalalignment='bottom', horizontalalignment='right')
if not np.isnan(el_pressure.magnitude):
    plt.text(el_pressure.m, el_temperature.m, 'EL', verticalalignment='bottom', horizontalalignment='right')

# 設置圖表標題和坐標標籤
plt.title('Skew-T Log-P Diagram')
plt.xlabel('Temperature (°C)')
plt.ylabel('Pressure (hPa)')
plt.legend()
plt.grid(True)

plt.show()

# 計算濕靜能和飽和濕靜能
L_v = 2.5e6 * units.joule / units.kilogram  # J/kg
q_v = mixing_ratio  # kg/kg
C_p = 1005 * units.joule / (units.kilogram * units.kelvin)  # J/(kg K)
R_d = 287 * units.joule / (units.kilogram * units.kelvin)  # J/(kg K)
T = temperature

h_m = C_p * T + L_v * q_v
h_m_s = C_p * T  # 假設飽和濕靜能為沒有潛熱釋放的情況

# 計算高度
height = (np.log(1000 / pressure.m) * 7) * units.kilometer  # 假設大氣壓隨高度變化

# 繪製濕靜能和飽和濕靜能的高度剖面
plt.figure(figsize=(10, 6))
plt.plot(h_m.magnitude, height.magnitude, label='Moist Static Energy')
plt.plot(h_m_s.magnitude, height.magnitude, label='Saturated Moist Static Energy')
plt.axhline(y=(lcl_pressure.m / 1000), color='r', linestyle='--', label='LCL')  # 標示LCL
if not np.isnan(lfc_pressure.magnitude):
    plt.axhline(y=(lfc_pressure.m / 1000), color='b', linestyle='--', label='LFC')  # 標示LFC
if not np.isnan(el_pressure.magnitude):
    plt.axhline(y=(el_pressure.m / 1000), color='g', linestyle='--', label='EL')  # 標示EL
plt.xlabel('Energy (J/kg)')
plt.ylabel('Height (km)')
plt.title('Moist Static Energy Profile')
plt.legend()
plt.grid(True)

plt.show()
