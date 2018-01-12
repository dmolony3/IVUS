# this function shifts an image so that its contour forms the first row
import numpy as np
from matplotlib import cm, pyplot as plt
def shift(image, contour):
    # size of single image
    imsize = np.array([image.shape[1] - np.min(contour), image.shape[2]]).astype(int)
    # volume of single images
    shifted_image = np.zeros([image.shape[0], imsize[0], imsize[1]])
    for i in range(0, image.shape[0]):
        # get an aline which corresponds to 1 degree of one of the images
        for j in range(0, imsize[1]):
            aline = image[i, contour[i, j]:, j]
            shifted_image[i, 0:aline.shape[0], j] = aline
    #plt.figure()
    #plt.imshow(shifted_image[i, :, :], cmap=cm.gray)
    #plt.show()
    return shifted_image