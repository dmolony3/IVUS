# this function computes the euclidean distance between the area of two contours
import numpy as np

def compute(area1, area2):
    dist = np.sqrt((area1 - area2)**2)

    return dist