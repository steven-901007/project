import matplotlib.pyplot as plt
import numpy as np
import cv2
import pylab

img = cv2.imread("C:/Users/steve/Downloads/123/dem_20m.tif",-1)
plt.figure(dpi=180)
plt.imshow(img)

x = np.linspace(1,10175)
y = np.linspace(1,19112)
X,Y = np.meshgrid(x,y)
Z = img


plt.contourf(X,Y,Z,20,alpha=.6,cmap=plt.cm.jet)
# plt.contour(X,Y,Z,100,colors = 'black')
# plt.clabel(C,inline=True,fontsize=10)
plt.colorbar()
plt.show()