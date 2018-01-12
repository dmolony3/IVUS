# this function computes the correlation between two polar domain images
# The images should have been shifted so that the lumen is removed
# image1 and image2 are arrays of format(no. images, depth, angle)
import numpy as np
from matplotlib import pyplot as plt


def compute(image1, image2, step):

    # ensure that the input are 3D arrays
    if len(image1.shape) == 2:
        image1 = np.reshape(image1, [1, image1.shape[0], image1.shape[1]])
        image2 = np.reshape(image2, [1, image2.shape[0], image2.shape[1]])

    num_images1 = image1.shape[0]
    num_images2 = image2.shape[0]
    corr = np.zeros([num_images1, 360/step, num_images2])
    angles = np.linspace(step, 360, 360 / step, dtype=np.int)
    # permute so that num_images is third dimension
    image1 = np.transpose(image1, [1, 2, 0])
    image2 = np.transpose(image2, [1, 2, 0])

    # determine the depth limit to operate over
    max_depth = min(image1.shape[0], image2.shape[0])
    # remove pixels outside the max depth
    image1 = image1[0:max_depth, :, :]
    image2 = image2[0:max_depth, :, :]

    for i in range(num_images1):
        for j in range(angles.shape[0]):
            # rotate image clockwise
            image2_shifted = np.roll(image2, -angles[j], axis=1)
            corr[i, j, :] = correlation(image1[:,:,i], image2_shifted)
#            plt.figure()
#            plt.subplot(1, 2, 1)
#            plt.imshow(image1[:,:,i])
#            plt.subplot(1, 2, 2)
#            plt.imshow(image2_shifted[:,:,0])
        print("Processing image {}".format(i))


    return corr


def correlation(image1, image2):
    # image1 is the reference image (mxn), image2 is the rotated image (mxnxp)
    #ref_image_std = np.std(image1, axis=(1,2))
    #ref_image_mean = np.mean(image1, axis=(1,2))
    ref_image_std = np.std(image1)
    ref_image_mean = np.mean(image1)

    rot_image_std = np.std(image2, axis=(0,1))
    rot_image_mean = np.mean(image2, axis=(0,1))

    # compute the denominator (elementwise multiplication)
    denom = ref_image_std*rot_image_std

    # flatten images so we can perform matrix multiplication
    image1 = np.reshape(image1, (-1, 1), order = 'F') # use fortran (matlab) indexing
    image2 = np.reshape(image2, (image2.shape[0]*image2.shape[1], -1), order = 'F')
    # compute de-meaned values
    g_minus_g_mean = image2 - rot_image_mean
    f_minus_f_mean = image1 - ref_image_mean

    # compute the product of two images
    product = np.dot(f_minus_f_mean.T, g_minus_g_mean)/denom
    #product = (f_minus_f_mean.reshape(image1.shape[0], image1.shape[1], 1)*g_minus_g_mean)/denom

    corr = product/(image1.shape[0]*image1.shape[1])
    corr = (corr+1)/2
    return corr