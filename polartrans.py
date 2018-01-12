import numpy as np
from scipy.ndimage import map_coordinates
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy import interpolate

def compute(im, nrad, ntheta, method, cx=0, cy=0):

    rows, cols = im.shape

    if cx == 0:
        cx = cols/2
        cy = rows/2

    if method == 'valid':
        rmax = min([cx-1, cols-cx, cy-1, rows-cy])
    elif method == 'full':
        dx = max([cx-1, cols-cx])
        dy = max([cy-1, rows-cy])
        rmax = np.sqrt(dx**2 + dy**2)

    deltatheta = 2*np.pi/ntheta
    deltarad = float(rmax)/(float(nrad)-1)

    np.arange(0, ntheta, 1) * deltatheta
    np.arange(0, nrad, 1) * deltarad

    theta, radius = np.meshgrid(np.arange(0, ntheta, 1) * deltatheta, np.arange(0, nrad, 1) * deltarad)

    xi = np.multiply(radius, np.cos(theta)) + cx
    yi = np.multiply(radius, np.sin(theta)) + cy

    x, y = np.meshgrid(np.arange(1, cols+1, 1), np.arange(1, rows+1, 1))

    #im_interp = map_coordinates(im, xi, yi)
    #im_interp = map_coordinates(im, [xi, yi], order=3, mode='nearest')
    im_interp = map_coordinates(im, np.array([xi.ravel(), yi.ravel()]), order=3, mode='nearest').reshape(xi.shape)
    #tck = interpolate.bisplrep(x.ravel(), y.ravel(), im, s=0)
    #im_interp = interpolate.bisplev(xi.ravel(), yi.ravel(), tck)
    return im_interp