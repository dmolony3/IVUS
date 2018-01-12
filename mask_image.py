# mask image by converting image to polar coordinates and then converting it back to caratesian
import read_xml
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from PIL import Image

source1 = np.array(Image.open('/home/david/Documents/MATLAB/Shear-Stent/SS40/IVUS_BL/1.tif'))

source = cv2.imread('/home/david/Documents/MATLAB/Shear-Stent/SS40/IVUS_BL/1.tif')

print(source.min(), source.max())
source1 = np.mean(source1, axis=2)
img64_float = np.mean(source.astype(np.float64), 2)

Mvalue =np.sqrt(((img64_float.shape[0]/2.0)**2.0)+((img64_float.shape[1]/2.0)**2.0))
print(img64_float.shape)

#polar_image = cv2.linearPolar(img64_float, (250, 360), Mvalue,cv2.WARP_FILL_OUTLIERS)
polar_image = cv2.linearPolar(img64_float, (img64_float.shape[0]/2, img64_float.shape[1]/2), Mvalue,cv2.WARP_FILL_OUTLIERS)
print(polar_image.shape)
cartesian_image = cv2.linearPolar(polar_image, (img64_float.shape[0]/2, img64_float.shape[1]/2), Mvalue,(250),cv2.WARP_INVERSE_MAP)

#cartesian_image = cartesian_image/200

polar_image = polar_image/255


BLxmlpath = '/home/david/Documents/MATLAB/Shear-Stent/SS40/IVUS_BL/SS40_BL.xml'
BLcontours, x, y, resolution = read_xml.read(BLxmlpath)
# sort into inner and outer contours
xInnerBL = [x[i] for i in range(0, len(x), 2)]
yInnerBL = [y[i] for i in range(0, len(y), 2)]
xOuterBL = [x[i] for i in range(1, len(x), 2)]
yOuterBL = [y[i] for i in range(1, len(y), 2)]

plt.figure()
plt.imshow(polar_image)
plt.show()

plt.figure()
plt.imshow(cartesian_image, cmap=cm.gray)
plt.hold('on')
plt.plot(xInnerBL[1], yInnerBL[1], 'r')
plt.show()

s = lambda x, y: (x, y)
#xInnerBL[0].map(s)
#[(i[0], y) for i, j in range(0,len(xInnerBL[1]))]
x=[]
for i in range(1, 2):
    for j in range(0, len(xInnerBL[i])):
        x.append((xInnerBL[i][j], yInnerBL[i][j]))

x1 = np.squeeze(np.asarray(x, dtype=int))

out=[]
for i in range(1, 2):
    for j in range(0, len(xOuterBL[i])):
        out.append((xOuterBL[i][j], yOuterBL[i][j]))
out1 = np.squeeze(np.asarray(out, dtype=int))


print((x1))
print((out))
# cv2 inputs, image, contour, contour no. to draw, contour color, contour fill
img=cv2.drawContours(source1, [x1], 0, -1, -1)
temp = img.copy()
img2=cv2.drawContours(source1, [out1], 0, -1, -1)
print(type(temp))
plt.figure()
plt.subplot(1,2,1)
plt.imshow(temp)
plt.subplot(1,2,2)
plt.imshow(img2)
plt.show()

