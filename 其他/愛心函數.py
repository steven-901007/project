import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider

# 創建數據，範圍從 -2 到 2
x = np.linspace(-np.sqrt(np.pi), np.sqrt(np.pi), 400)

# 創建圖形和軸
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25)
a = 0

# 初始的 y 值
y1 = x**(2/3) + np.e/3 * np.sqrt(np.pi - x**2) * np.sin(a * np.pi * x)
y2 = (-x)**(2/3) + np.e/3 * np.sqrt(np.pi - (-x)**2) * np.sin(a * np.pi * -x)

# 繪製初始的曲線
line1, = plt.plot(x, y1, lw=3,color ='r')
line2, = plt.plot(x, y2, lw=3,color = 'r')
ax.set_xlim(-np.sqrt(np.pi), np.sqrt(np.pi))
ax.set_ylim(-1.5, 2.5)
# ax.set_title()



#創建滑動條來控制 a 的值
ax_slider = plt.axes([0.25, 0.1, 0.65, 0.03])
slider = Slider(ax_slider, 'a', 0, 20, valinit=0)

# 更新函數
def update(val):
    a = slider.val
    # 計算 y1 和 y2 的值，同時過濾掉不合法的數值
    y1 = np.zeros_like(x)
    y2 = np.zeros_like(x)
    mask1 = x**2 <= np.pi
    mask2 = (-x)**2 <= np.pi
    y1[mask1] = x[mask1]**(2/3) + np.e/3 * np.sqrt(np.pi - x[mask1]**2) * np.sin(a * np.pi * x[mask1])
    y2[mask2] = (-x[mask2])**(2/3) + np.e/3 * np.sqrt(np.pi - (-x[mask2])**2) * np.sin(a * np.pi * -x[mask2])
    line1.set_ydata(y1)
    line2.set_ydata(y2)
    fig.canvas.draw_idle()

slider.on_changed(update)

# 動畫的更新函數
def animate(i):
    slider.set_val(i / 1)

# 創建動畫
ani = animation.FuncAnimation(fig, animate, frames=20, interval=200)

plt.show()
