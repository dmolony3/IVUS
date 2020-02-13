import xml.etree.ElementTree as et
import os
import re
import argparse
import datetime
import numpy as np
import PIL.Image as im
import matplotlib.path as mplPath
from skimage import measure

# read images
def mask_image(mask, catheter):
    # mask values outside perivascular as the image max
    mask.setflags(write=1)

    # set catheter values equal to lumen values
    if catheter == 1:
        mask[mask == 1] = 2
        mask[mask < 2] = mask.max()
    else:
        mask[mask < 1] = mask.max()

    return mask


def label_contours(image, levels):
    """generate contours for labels"""
    # Find contours at a constant value
    contours1 = measure.find_contours(image, levels[0])
    contours2 = measure.find_contours(image, levels[1])

    lumen = []
    plaque = []

    for contour in contours1:
        # lumen.append(np.array((contour[:,0]*IVUS_spacing, contour[:,1]*resolution)))
        lumen.append(np.array((contour[:, 0], contour[:, 1])))

    for contour in contours2:
        # plaque.append(np.array((contour[:,0]*IVUS_spacing, contour[:,1]*resolution)))
        plaque.append(np.array((contour[:, 0], contour[:, 1])))

    return lumen, plaque


def keep_largest_contour(contours, image_shape):
    # this function returns the largest contour (num of points) in a list of contours
    max_length = 0
    for contour in contours:
        if keep_valid_contour(contour, image_shape):
            if len(contour[0]) > max_length:
                keep_contour = contour
                max_length = len(contour[0])

    return keep_contour

def keep_valid_contour(contour, image_shape):
    # this function check that the contour is valid if the image centroid is contained within the mask region
    bbPath = mplPath.Path(np.transpose(contour))
    centroid = [image_shape[0]//2, image_shape[1]//2]
    return bbPath.contains_point(centroid)

def keep_central_contour(contours, image_shape):
    # this function returns the contour with its centroid closest to the image centroid
    centroids = np.zeros((len(contours), 2))
    for j, contour in enumerate(contours):
        centroids[j, :] = [np.mean(contour[0, :]), np.mean(contour[1, :])]
    # find distance from image centroid to all centroids
    dist = np.sqrt((centroids[:, 0] - image_shape[0]//2)**2 + (centroids[:, 1] - image_shape[1]//2)**2)
    keep_contour = contours[np.argmin(dist)]
    return keep_contour

parser = argparse.ArgumentParser(description='Generate xml file from labelmaps that can be read by Echoplaque')
parser.add_argument('--dir', type=str, help="Enter the directory containing the labels")
parser.add_argument('--res', default=0.02, type=float, help="Enter the image resolution")
parser.add_argument('--frames', type=int, help="Enter the total number of frames in the pullback")
parser.add_argument('--gated', default='', type=str, help="Enter the path to the file with the gated frames")
parser.add_argument('--speed', default=0.5, type=float, help="Enter the pullback speed")

# this code reads in a directory containing prediction images and outputs an xml file readable by EchoPlaque
full_path = os.getcwd()

args = parser.parse_args()
pred_dir = args.dir
resolution = args.res
num_frames = args.frames
gated = args.gated
speed = args.speed

pname = os.path.split(pred_dir)[-1]

# read prediction images
pred_files = os.listdir(pred_dir)
pred_files = [pred for pred in pred_files if '.png' in pred]
pred_files.sort(key=lambda var:[int(x) if x.isdigit() else x for x in re.findall(r'[^0-9]|[0-9]+', var)])

frames = [int(file.split('pred_image')[1].split('.png')[0]) for file in pred_files]
# read gated frames
if gated != '':
  f = open(gated, 'r')
  data = f.read()
  data = data.split('\n')
  data = [int(val) for val in data if val]
  f.close()
  frames = data
 
# open first image to determine image size
catheter=0
if catheter == 1:
  levels = [2.5, 3.5]
else:
  levels = [1.5, 2.5]
image_shape = im.open(os.path.join(pred_dir, pred_files[0])).size
preds = np.zeros((len(pred_files), image_shape[0],image_shape[1]), dtype=np.uint8)
for i, pred_file in enumerate(pred_files):
    preds[i, :, :] = np.asarray(im.open(os.path.join(pred_dir, pred_file)))
preds = mask_image(preds, catheter)

# get contours for each image
lumen_pred = []
plaque_pred = []
x = []
y = []
# convert contours to x and y points where every second entry in x and y are outer contours
for i in range(preds.shape[0]):
  lumen, plaque = label_contours(preds[i, :, :], levels)
  # return the contour with the largest number of points
  keep_lumen = keep_largest_contour(lumen, image_shape)
  keep_plaque = keep_largest_contour(plaque, image_shape)
  x.append(keep_lumen[1, :])
  y.append(keep_lumen[0, :])
  x.append(keep_plaque[1, :])
  y.append(keep_plaque[0, :])
  lumen_pred.append(keep_lumen)
  plaque_pred.append(keep_plaque)

root = et.Element('AnalysisState')
analyzedfilename = et.SubElement(root, 'AnalyzedFileName')
analyzedfilename.text = 'FILE0000'
analyzedfilenamefullpath = et.SubElement(root, 'AnalyzedFileNameFullPath')
analyzedfilenamefullpath.text = 'D:\CASE0000\FILE0000'
previousanalysisstate = et.SubElement(root, 'PreviousAnalysisState')
username = et.SubElement(root, 'UserName')
username.text = 'ICViewAdmin'
computername = et.SubElement(root, 'ComputerName')
computername.text = 'USER-3BF85F9281'
softwareversion = et.SubElement(root, 'SoftwareVersion')
softwareversion.text = '4.0.27'
screenresolution = et.SubElement(root, 'ScreenResolution')
screenresolution.text = '1600 x 900'
date = et.SubElement(root, 'Date')
date.text = datetime.datetime.now().strftime('%d%b%Y %H:%M:%S')
timezone = et.SubElement(root, 'TimeZone')
timezone.text = 'GMT-300 min'
demographics = et.SubElement(root, 'Demographics')
patientname = et.SubElement(demographics, 'PatientName')
patientname.text = pname
patientid = et.SubElement(demographics, 'PatientID')
patientid.text = pname

imagestate = et.SubElement(root, 'ImageState')
xdim = et.SubElement(imagestate, 'Xdim')
xdim.text = str(preds.shape[1])
ydim = et.SubElement(imagestate, 'Ydim')
ydim.text = str(preds.shape[2])
numberofframes = et.SubElement(imagestate, 'NumberOfFrames')
numberofframes.text = str(num_frames)
firstframeloaded = et.SubElement(imagestate, 'FirstFrameLoaded')
firstframeloaded.text = str(0)
lastframeloaded = et.SubElement(imagestate, 'LastFrameLoaded')
lastframeloaded.text = str(num_frames-1)
stride = et.SubElement(imagestate, 'Stride')
stride.text = str(1)

imagecalibration = et.SubElement(root, 'ImageCalibration')
xcalibration = et.SubElement(imagecalibration, 'XCalibration')
xcalibration.text = str(resolution)
ycalibration = et.SubElement(imagecalibration, 'YCalibration')
ycalibration.text = str(resolution)
acqrateinfps = et.SubElement(imagecalibration, 'AcqRateInFPS')
acqrateinfps.text = str(133.0)
pullbackspeed = et.SubElement(imagecalibration, 'PullbackSpeed')
pullbackspeed.text = str(speed)

brightnesssetting = et.SubElement(root, 'BrightnessSetting')
brightnesssetting.text = str(50)
contrastsetting = et.SubElement(root, 'ContrastSetting')
contrastsetting.text = str(50)
freestepping = et.SubElement(root, 'FreeStepping')
freestepping.text = 'FALSE'
steppinginterval = et.SubElement(root, 'SteppingInterval')
steppinginterval.text = str(1)
volumehasbeencomputed = et.SubElement(root, 'VolumeHasBeenComputed')
volumehasbeencomputed.text = 'FALSE'

framestate = et.SubElement(root, 'FrameState')
imagerelativepoints = et.SubElement(framestate, 'ImageRelativePoints')
imagerelativepoints.text = 'TRUE'
xoffset = et.SubElement(framestate, 'Xoffset')
xoffset.text = str(109)
yoffset = et.SubElement(framestate, 'Yoffset')
yoffset.text = str(3)
for i in range(num_frames):
    fm = et.SubElement(framestate, 'Fm')
    num = et.SubElement(fm, 'Num')
    num.text = str(i)
    #num.text = file.split('pred_image')[1].split('.png')[0]

    if i in frames:
        frame_idx=[k for k in range(len(frames)) if i==frames[k]][0]
        for j in range(2):
            ctr = et.SubElement(fm, 'Ctr')
            npts = et.SubElement(ctr, 'Npts')
            npts.text = str(len(x[frame_idx*2+j]))
            type = et.SubElement(ctr, 'Type')
            if j == 0:
                type.text = 'L'
            elif j == 1:
                type.text = 'V'
            handdrawn = et.SubElement(ctr, 'HandDrawn')
            handdrawn.text = 'T'
            # iterative over the points in each contour
            for k in range(len(x[frame_idx*2+j])):
                p = et.SubElement(ctr, 'p')
                p.text = str(int(x[frame_idx*2+j][k])) + ',' + str(int(y[frame_idx*2+j][k]))


tree = et.ElementTree(root)
tree.write(pname+'_automatic.xml')