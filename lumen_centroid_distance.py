# this function computes the distance from the lumen centroid to the lumen wall
# the distance is return as a list of numpy arrays
import numpy as np
from scipy.interpolate import interp1d

from matplotlib import cm, pyplot as plt

def interp(rad, theta, steps):
    # returns an interpolated contour

    # sort contour before stacking
    theta, sort_idx = np.unique(theta, return_index=True)
    rad = np.array(rad)[sort_idx]
    # theta = np.array(self.theta)[sort_idx]

    rad1 = (rad, rad, rad)
    theta1 = (theta, theta + 360, theta + 720)

    # concatenate contour
    rad = np.concatenate(rad1, axis=0)
    theta = np.concatenate(theta1, axis=0)

    # perform interpolation
    # f = interp1d(theta, rad, kind=self.interpmethod)
    f = interp1d(theta, rad, kind="linear")

    # interpolate with 100 points per cross section
    thetanew = np.linspace(steps, 360, 360/steps)
    radnew = f(thetanew)

    # interpolate with 360 pooints per cross section (for masking image)
    #radmask = f(np.linspace(1, 360, 360))

    # the image is offset by 90 degrees so shift the contour
    #radnew = np.roll(radnew, self.resolution / 2)
    #radmask = np.roll(radmask, 180)

    return radnew, thetanew


def compute(contours, centroid, steps, resolution=1):

    num_contours = centroid.shape[0]
    distance1 = np.zeros([num_contours, 360/steps])
    distance2 = np.zeros([num_contours, 360/steps])

    # convert contour numpy array
    for i in range(num_contours):
        contour1 = np.concatenate((np.asarray((contours.xInner[i])).reshape(-1, 1),
                                   np.asarray((contours.yInner[i])).reshape(-1, 1)), axis=1)
        contour2 = np.concatenate((np.asarray((contours.xOuter[i])).reshape(-1, 1),
                                   np.asarray((contours.yOuter[i])).reshape(-1, 1)), axis=1)

        # move to origin
        contour1 = contour1 - centroid[i, :]
        contour2 = contour2 - centroid[i, :]

        # convert to polar coordinates
        rad1 = np.sqrt(contour1[:, 0]**2 + contour1[:, 1]**2)
        rad2 = np.sqrt(contour2[:, 0]**2 + contour2[:, 1]**2)

        theta1 = np.arctan2(contour1[:, 1], contour1[:, 0])*180/np.pi
        theta2 = np.arctan2(contour2[:, 1], contour2[:, 0])*180/np.pi

        # set theta to be between 0 and 360
        min_theta = np.abs(theta1.min())
        theta1 = theta1 + min_theta
        min_theta = np.abs(theta2.min())
        theta2 = theta2 + min_theta

        # convert to required resolution
        rad1 = rad1*resolution
        rad2 = rad2*resolution

        # interpolate to the desired no. of circumferential points
        rad1, theta = interp(rad1, theta1, steps)
        rad2, _ = interp(rad2, theta2, steps)

        # return theta to the correct angle range
        theta2 = theta2 - min_theta

        if i == 0:
            plt.figure()
            plt.plot(rad2)

        # place in matrix starting at 3 o'clock
        distance1[i, :] = rad1
        distance2[i, :] = rad2

    return distance1, distance2