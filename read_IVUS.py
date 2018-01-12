# this function reads in IVUS images

from PIL import Image
from matplotlib import pyplot as plt
from matplotlib import cm
import numpy as np
import read_xml
import os

def read(path):
    #path = '/home/david/Documents/MATLAB/Shear-Stent/SS40/IVUS_BL'

    # read files with the .tif extension
    files = [name for name in os.listdir(path) if name.endswith('.tif')]
    # sort files so that the images are loaded in the correct order
    files = [int(name.split('.tif')[0]) for name in files]
    files.sort()

    # read first image and check if grayscale or VH
    IVUS_image = np.array(Image.open(path + '/' + str(files[0]) + '.tif'), dtype=np.uint8)
    if (IVUS_image[:, :, 1] == IVUS_image[:, :, 0]).all():
        grayscale = 1
        # pre-allocate memory
        IVUS_images = np.zeros([len(files), 500, 500], dtype=np.uint8)
    else:
        grayscale = 0
        # pre-allocate memory
        IVUS_images = np.zeros([len(files), 500, 500, 3], dtype=np.uint8)

    # read all images
    for i in range(len(files)):
        IVUS_image = np.array(Image.open(path+'/' + str(files[i]) + '.tif'), dtype=np.uint8)
        # remove color dimension if images are grayscale
        if grayscale == 1:
            IVUS_images[i, :, :] = IVUS_image[:, :, 0]
        else:
            IVUS_images[i, :, :, :] = IVUS_image

    print(IVUS_images.shape)

    return IVUS_images