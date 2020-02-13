import Cython
import numpy as np


def corr(points, x, y, im2):
    tmp = np.zeros([len(x), 1])
    for j in range(len(x)):
        points1 = np.array([[x[j]], [y[j]]])
        idx = np.sum(np.abs(points - points1), axis=0)
        idx = np.where(idx == np.min(idx))
        tmp[j]= im2[idx]
    return tmp
