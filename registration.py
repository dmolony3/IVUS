import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import frame
import crosscorr
import xcorrPeriodic
import find_path
import cost_matrix
import imlook3d
import area_distance
import imutils
import remove_lumen
import correlate_image
import contourshift_image
import evaluate_registration
import plot_features
import gif_features
from PIL import Image

# patientname
pname = 'my_patient'

# flag indicating whether the perivascular and plaque correlation have already been precomputed (1)
precompute=0

# flag indicating whether the registration should be evaluated against manual registration (1)
evaluate = 0

# start and end frames in format [BL, FU]
start_idx = [1, 2]
end_idx = [10, 10]

# BL files
BLpath = os.path.join(os.getcwd(), 'BL')
BLxmlpath = os.path.join(os.getcwd(), 'BL/BL_data.xml')

# FU files
FUpath = os.path.join(os.getcwd(), 'FU')
FUxmlpath = os.path.join(os.getcwd(), 'FU/FU_data.xml')

# load images and contours
BL = frame.Frame(BLpath, BLxmlpath)
BL.contour()
IVUS_images_BL = BL.IVUS
FU = frame.Frame(FUpath, FUxmlpath)
FU.contour()
IVUS_images_FU = FU.IVUS


# get plaque thickness and lumen, plaque area
BL_thick = BL.getthickness()
BL_lumenarea, BL_plaquarea, BL_vesselarea = BL.getarea()
FU_thick = FU.getthickness()
FU_lumenarea, FU_plaquarea, FU_vesselarea = FU.getarea()

# create masked perivascular and plaque image
periMaskBL, plaqueMaskBL = BL.getplaque()
periMaskFU, plaqueMaskFU = FU.getplaque()

# convert centroids to array
center1 = np.asarray(BL.centroid)
center2 = np.asarray(FU.centroid)

# determine the minimum no. of images
num_BL = min(IVUS_images_BL.shape[0], len(BL.centroid))
num_FU = min(IVUS_images_FU.shape[0], len(FU.centroid))

# convert images to polar domain and remove lumen so that first depth pixel corresponds to lumen boundary
IVUSPolBL, _ = remove_lumen.ToPolar(IVUS_images_BL, center1, 0)
IVUSPolFU, _ = remove_lumen.ToPolar(IVUS_images_FU, center2, 0)

# create perivascular and plaque masks in polar domain
periMaskPolBL, periContourPolBL = remove_lumen.ToPolar(periMaskBL, center1, 1)
periMaskPolFU, periContourPolFU = remove_lumen.ToPolar(periMaskFU, center2, 1)
plaqueMaskPolBL, plaqueContourPolBL = remove_lumen.ToPolar(plaqueMaskBL, center1, 1)
plaqueMaskPolFU, plaqueContourPolFU = remove_lumen.ToPolar(plaqueMaskFU, center2, 1)

# shift the image/contour so that the first depth pixel corresonds to the lumen boundary
plaqueBLShifted = contourshift_image.shift(IVUSPolBL*plaqueMaskPolBL, plaqueContourPolBL)
plaqueFUShifted = contourshift_image.shift(IVUSPolFU*plaqueMaskPolFU, plaqueContourPolFU)

# shift the image/contour so that the first depth pixel corresponds to the plaque (outer) boundary
periBLshifted = contourshift_image.shift(IVUSPolBL*periMaskPolBL, periContourPolBL)
periFUshifted = contourshift_image.shift(IVUSPolFU*periMaskPolFU, periContourPolFU)

# determine the perivascular and plaque correlation between BL and FU images
if precompute == 0:
    plaqueCorr = correlate_image.compute(plaqueBLShifted, plaqueFUShifted, 5)
    periCorr = correlate_image.compute(periBLshifted, periFUshifted, 5)
    np.save(pname+'plaque_corr', plaqueCorr)
    np.save(pname+'peri_corr', periCorr)
else:
    plaqueCorr = np.load(pname+'plaque_corr.npy')
    periCorr = np.load(pname + 'peri_corr.npy')

# set the number of angular coordinates to skip i.e. 0:skip:360
skip = 5

# get plaque area and thickness correlation
thickCorr = np.zeros([num_BL, 360/skip, num_FU])
areaCorr = np.zeros([num_BL, 360/skip, num_FU])


# determine the thickness and area correlations between BL and FU images
for i in range(0,num_BL):
    for k in range(0, num_FU):
        thickCorr[i, :, k] = xcorrPeriodic.corr(BL_thick[i, ::skip], FU_thick[k, ::skip], [0, (360 / skip)-1])
        area_dist = area_distance.compute(BL_lumenarea[i], FU_lumenarea[k])
        areaCorr[i, :, k] = np.repeat(area_dist, 360 / skip).reshape(1, 360 / skip)


# set area cost between 0 and 1
areaCorr = areaCorr/np.max(areaCorr)


# plot features for the specified BL and FU images
BL_frame = 4
FU_frame = 5
plot_features.plot(1 - periCorr, 1 - plaqueCorr, 1 - thickCorr, areaCorr, BL_frame, FU_frame)

# determine global and local cost through dynamic programming
G, L = cost_matrix.compute(periCorr, plaqueCorr, thickCorr, areaCorr)
np.save(pname+'Cost', G)
np.save(pname+'Total_cost', L)

# find optimum path through cost matrix
optimum_path = find_path.optimum(G, L, start_idx, end_idx)
optimum_path = optimum_path.astype(np.int)
optimum_path[:, 2] = optimum_path[:, 2]*skip

# perform rotation of the FU images and print rotated images to file
FU_registered = np.zeros([optimum_path.shape[0], IVUS_images_FU.shape[1], IVUS_images_FU.shape[2]])
for k in range(optimum_path.shape[0]):
    FU_registered[k, :, :] = imutils.rotate(IVUS_images_FU[optimum_path[k, 1], :, :], -optimum_path[k, 2])
    Image.fromarray(FU_registered[k, :, :].astype(np.uint8)).save(pname + '_' + str(optimum_path[k,1])+'.tif')

# print co-registration data to file
np.savetxt(pname + '_registered.csv', optimum_path, fmt='%d', delimiter=',', header='BL, FU, angle')

# perform evaluation with manual co-registration
if evaluate == 1:
    manual_coreg = np.loadtxt(os.path.join(os.getcwd(), 'coregister_circ.txt'))
    error_axial, error_circ = evaluate_registration.eval(optimum_path, manual_coreg)