import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import image_correlation
import timeit
import pstats, cProfile


def crosscorr(im1, im2, center1, center2, skip):
    # this function perform 2d normalized cross correlation in 2 inputs images of the same size
    # im1 - reference image
    # im2 - interplated image

    #pr=cProfile.Profile()
    #pr.enable()

    nSteps = 360/skip

    # create meshgrid
    X1, Y1 = np.meshgrid(np.linspace(0, im1.shape[0], im1.shape[1]), np.linspace(0, im2.shape[0], im2.shape[1]))
    X2 = X1.copy()
    Y2 = Y1.copy()

    # shift the baseline coordinates to match the origin
    X1 = X1 - center1[0]
    Y1 = Y1 - center1[1]
    X2 = X2 - center2[0]
    Y2 = Y2 - center2[1]

    # get coordinates of mask
    r,c = np.where(im1 != 0)
    interp_rgb = np.zeros([len(r), nSteps])

    # compute reference image statistics (ignore zeros)
    ref_image = im1[r, c]
    ref_image_std = np.std(ref_image)
    ref_image_mean = np.mean(ref_image)

    # get x,y coordinates of masked region
    x = X1[r, c]
    y = Y1[r, c]

    # reshape to 2D
    x = x.reshape(len(x), 1)
    y = y.reshape(len(y), 1)



    interp_rgb = np.zeros([len(x), nSteps])

    # flatten image so that we can access it using index
    im2flat = im2.flatten()
    # convert from uint8 to int32 for cython use
    im2flat = im2flat.astype(np.int32)

    rotation_center = center2
    inds = np.arange(0, len(x))
    [tmp, thetas] = image_rot_corr(X1, Y1, x, y, X2, Y2, im1, im2flat, nSteps)
    interp_rgb = tmp

    #pr.disable()
    #pr.print_stats(sort='time')

    # set nans to zero
    interp_rgb[np.isnan(interp_rgb)] = 0

    # compute mean and standard deviation
    comp_image_std = np.std(interp_rgb)
    comp_image_means = np.mean(interp_rgb)

    # pre-compute denominator
    denom = ref_image_std*comp_image_std

    # ensure denominator is not zero
    denom = denom + 1e-9

    # compute de-meaned values
    g_minus_g_mean = interp_rgb - comp_image_means # broadcast value over all angles
    f_minus_f_mean = ref_image - ref_image_mean

    # product of two images (matrix multiplication)
    #product = (f_minus_f_mean.reshape(r.shape[0], 1)*g_minus_g_mean)/denom
    #product = np.sum(f_minus_f_mean.reshape(r.shape[0], 1)*g_minus_g_mean, axis=0)/denom
    product = np.dot(f_minus_f_mean.reshape(1, r.shape[0]),g_minus_g_mean)/denom
    # normalize by the no. of pixels
    corr = product/len(x)
    # clamp between 0 and 1
    corr = (corr+1)/2
    return corr

def plot_points(points, points1, im1, im2, cc):
    # this function plots the points (rotated im1) and points1 (masked points of im1)

    plt.figure()
    #X, Y = np.meshgrid(np.linspace(0, im1.shape[0], im1.shape[1]), np.linspace(0, im1.shape[0], im1.shape[1]))
    #plt.scatter(X.flatten(), Y.flatten(), c=im1.flatten())
    plt.subplot(1, 3, 1)
    plt.scatter(points[:, 0], points[:, 1], c=im1.flatten(), cmap='gray')
    plt.subplot(1, 3, 2)
    plt.scatter(points1[:,0], points1[:, 1], c=cc, cmap='gray')
    plt.subplot(1, 3, 3)
    plt.scatter(points1[:,0], points1[:, 1], c=cc, cmap='gray')
    plt.scatter(points[:, 0], points[:, 1], c=im1.flatten(), cmap='gray')

def image_rot_corr(X1, Y1, x, y, X2, Y2, im1, im2, NSteps):
    # Get correlation between reference image and interpolated image
    # X, Y - grid defining points of interpolated image (prior to rotation)
    # x, y -  shifted points of reference image mask
    # im2 - flattened interpolated image mask

    # z coordinate for matrix multiplication
    a = np.zeros([1, len(X1.flatten())])
    a=a.flatten()

    # angle values in radians
    #theta = np.linspace(5, 360, (360 / 5))
    theta = np.linspace((2*np.pi)/72, 2*np.pi, 72)

    #n = im1.shape[0] * im2.shape[1]
    # initialize array
    tmp = np.zeros([len(x), NSteps])
    count = 0

    # determine imsize of flattened image
    imsize = im2.shape[0]

    # points of masked region of im1 (with image centroid shifted to im2)
    points1 = np.concatenate((x, y), axis=1).astype(np.float32)

    # perform rotation
    for angle in theta:


        rotMat = np.array([[np.cos(angle), -np.sin(angle), 0],
                           [np.sin(angle), np.cos(angle), 0],
                           [0, 0, 1]])

        points = np.array([X2.flatten(), Y2.flatten(), a])
        # rotate FU image
        points_rotated = np.dot(rotMat, points)
        #points = np.array([X1.flatten('C'), Y1.flatten('C')], dtype=np.float32)
        points = np.concatenate((points_rotated[0,:].reshape(imsize, 1), points_rotated[1,:].reshape(imsize, 1)), axis=1).astype(np.float32)

        # perform image correlation by interpolating
        cc = image_correlation.corr(points, points1, im2)
        tmp[:, count] = cc
        #plot_points(points, points1, im1, im2, cc)
        #plot_points(np.concatenate((X2.reshape(imsize, 1), Y2.reshape(imsize, 1)), axis=1), points1, im1, im2, cc)

        count += 1

        #print(angle)
    return tmp, theta