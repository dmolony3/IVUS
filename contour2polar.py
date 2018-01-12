import numpy as np

def polar(x, y, center, scale):
    x = np.array(x, dtype=np.float32)
    y = np.array(y, dtype=np.float32)
    rad = np.sqrt((x - center[0])**2 + (y - center[1])**2)
    theta = np.arctan2((y - center[0]),(x - center[1]))
    #theta = np.arctan(y/x)
    # convert theta to degrees
    theta = theta*(180/np.pi)
    theta = theta + np.abs(theta.min())
    # multiply the radius by the scale, scale is the ratio of the original image size to polar size
    rad = rad*scale

    #x = radius.*np.cos(theta) - center[0]
    #y = radius.*np.sin(theta) - center[1]
    return rad, theta