# convert cartesian image to polar coordinates
import numpy as np
from scipy.ndimage.interpolation import geometric_transform, map_coordinates
from scipy.interpolate import interp2d

def polar(img, order=5):
    max_radius = 0.5*np.linalg.norm(img.shape)
    def transform(coords):
        theta = (2.0*np.pi*coords[1])/(img.shape[1] -1.)
        radius = (max_radius*coords[0])/img.shape[0]
        i = 0.5*img.shape[0] - radius*np.sin(theta) + 250
        j = radius*np.cos(theta) + 0.5*img.shape[1] + 250
        return i, j

    impolar = geometric_transform(img, transform, order=order, mode='nearest', prefilter=True)

    return impolar

def polar2(img, nradius, ntheta):


    rows, cols = img.shape

    # get center of image
    cx = cols/2
    cy = rows/2

    rmax = np.min([cx-1, cols-cx, cy-1, rows-cy])

    #  increments in radius and theta
    deltatheta = 2*np.pi/ntheta
    deltarad = float(rmax)/float((nradius-1))
    theta, rad = np.meshgrid(np.linspace(0, ntheta, ntheta)*deltatheta, np.linspace(0, nradius, nradius)*deltarad)
    print(deltarad)
    # convert polar grid to cartesian
    xi = np.multiply(rad, np.cos(theta)) + cx
    yi = np.multiply(rad, np.sin(theta)) + cy

    x, y = np.meshgrid(np.linspace(1, img.shape[0], 500), np.linspace(1, img.shape[1], 500))
    print(x.shape)

    x = np.arange(0, img.shape[0])
    y = np.arange(0, img.shape[1])
    print(xi[:,0])
    print(yi[:,0])
    f = interp2d(x, y, img)
    pim = f(xi[:,0], yi[0,:])
    pim = map_coordinates(img, )
    return pim


def polar2cart(r, theta, center):
    x = r * np.cos(theta) + center[0]
    y = r * np.sin(theta) + center[1]

    return x, y

def polar3(img, center, final_radius, initial_radius = None, phase_width = 3000):
    if initial_radius is None:
        initial_radius = 0

    theta, R = np.meshgrid(np.linspace(0, 2*np.pi, phase_width),
                           np.arange(initial_radius, final_radius))

    Xcart, Ycart = polar2cart(R, theta, center)

    Xcart = Xcart.astype(int)
    Ycart = Ycart.astype(int)

    if img.ndim == 3:
        polar_img = img[Ycart, Xcart, :]
        polar_img = np.reshape(polar_img, (final_radius-initial_radius, phase_width, 3))
    else:
        polar_img = img[Ycart, Xcart]
        polar_img = np.reshape(polar_img, (final_radius-initial_radius, phase_width))

    return polar_img





