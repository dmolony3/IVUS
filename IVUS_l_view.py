# this function plots l views of IVUS pullbacks

import numpy as np
from matplotlib import cm, pyplot as plt
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D

def show(IVUS_images, resolution, IVUS_pullback=0):

    # get image shape
    imsize = IVUS_images.shape
    midpoint = int(imsize[1]//2)
    # set default pullback distance to be 0.5mm
    if IVUS_pullback == 0:
        IVUS_pullback = np.arange(0, imsize[0]*0.5, 0.5)

    cmin = IVUS_images.min()
    cmax = IVUS_images.max()

    scalarmap = cm.ScalarMappable(norm=Normalize(vmin=cmin, vmax=cmax), cmap=cm.gray)
    cmap = scalarmap.to_rgba(IVUS_images[:, :, midpoint])

    x, y, z = np.meshgrid(np.arange(0, imsize[1], 1), np.arange(0, imsize[0], 1), np.arange(0, imsize[2], 1))
    x = x*resolution
    y = y*resolution
    #z = z*IVUS_pullback.reshape(imsize[0], 1, 1)

    z = np.array([[IVUS_pullback, ] * imsize[1], ] * imsize[1])
    z = np.transpose(z, [2, 1, 0])

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.view_init(-90, 90)
    # ax.plot_surface(x[:, :, 250], y[: ,:, 250], z[:,:,250], facecolors=cmap, antialiased=True)
    ax.plot_surface(z[:, :, midpoint], x[:, :, midpoint], np.zeros_like(y[:, :, midpoint]), rstride=1, cstride=1, facecolors=cmap,
                    antialiased=True)
    ax.axis('equal')
    ax.axis('off')