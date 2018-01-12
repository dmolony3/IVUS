import numpy as np
from scipy.interpolate import interp1d


class Contour:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.scale = 1
        self.center = [250, 250]
        self.area = 0
        #self.rad = 0
        #self.theta = 0
        self.interpmethod = 'cubic'
        self.resolution = 100

    def cart2pol(self):
        # convert cartesian contour to polar contour
        x = np.array(self.x, dtype=np.float32)
        y = np.array(self.y, dtype=np.float32)
        rad = np.sqrt((x - self.center[0]) ** 2 + (y - self.center[1]) ** 2)
        theta = np.arctan2((y - self.center[0]), (x - self.center[1]))

        # convert theta to degrees from 0 to 360
        theta = theta * (180 / np.pi)
        theta = theta + np.abs(theta.min())
        # multiply the radius by the scale, scale is the ratio of the original image size to polar size
        rad = rad * self.scale

        self.rad = rad
        self.theta = theta
        # x = radius.*np.cos(theta) - center[0]
        # y = radius.*np.sin(theta) - center[1]
        return rad, theta

    def pol2cart(self):
        # convert polar contour to cartesian
        x = self.rad*np.cos(self.theta) + self.center[0]
        y = self.rad*np.sin(self.theta) + self.center[1]

        return x, y

    def interp(self):
        # returns an interpolated contour

        # sort contour before stacking
        theta, sort_idx = np.unique(self.theta, return_index=True)
        rad = np.array(self.rad)[sort_idx]
        #theta = np.array(self.theta)[sort_idx]

        rad1 = (rad, rad, rad)
        theta1 = (theta, theta+360, theta +720)

        # concatenate contour
        rad = np.concatenate(rad1, axis=0)
        theta = np.concatenate(theta1, axis=0)

        # perform interpolation
        #f = interp1d(theta, rad, kind=self.interpmethod)
        f = interp1d(theta, rad, kind="linear")

        # interpolate with 100 points per cross section
        thetanew = np.linspace(360/self.resolution, 360, self.resolution)
        radnew = f(thetanew)

        # interpolate with 360 pooints per cross section (for masking image)
        radmask = f(np.linspace(1, 360, 360))

        # the image is offset by 90 degrees so shift the contour
        radnew = np.roll(radnew, self.resolution/2)
        radmask = np.roll(radmask, 180)

        self.radoriginal = self.rad
        self.thetaoriginal = self.theta
        self.rad = radnew
        self.theta = thetanew
        self.radmask = radmask

        return radnew, thetanew

    def centroid(self):
        # define contour centroid (assumes equiangular sampling)
        self.centroid = [np.mean(self.x), np.mean(self.y)]

        return self.centroid

    def contourArea(self):
        # returns the area of the contour
        if self.mask.any() != 0:
            self.area = np.sum(self.mask)
        else:
            print("area is undefined")
        return self.area

    def maskImage(self):
        # returns a mask from the contour points
        mask = np.zeros([self.center[0],360])
        # use radmask (1 radius point per degree)
        rad = self.radmask
        rad = rad.astype(int)

        # set pixels in lumen to 1
        for i in range(0, len(rad)):
            mask[:rad[i], i] = 1

        self.mask = mask

        return mask
