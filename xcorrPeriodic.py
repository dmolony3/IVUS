# Python implementation of xcorrPeriodic. Based on original Matlab code created by Jonathan Suever
import numpy as np


# inputs A and B are numpy arrays of shape (n, 1) and (n,1)
def corr(A, B, maxlags):
    # de-mean and normalize each of the signals
    A1 = (A - A.mean())/A.std()
    B1 = (B - B.mean())/B.std()

    #maxlags = np.ceil(len(A1)/2)
    #lags = np.arange(-maxlags, maxlags+1, dtype = np.int)
    lags = np.arange(-maxlags[0], maxlags[1]+1)

    nPoints = len(A1)

    # shift indices for B (using broadcasting)
    #inds = np.arange(1, nPoints+1) - lags
    #(np.arange(1, nPoints + 1).reshape(1, 8) - lags.reshape(9, 1)) - 1
    inds = (((np.arange(1, nPoints + 1, dtype=np.int).reshape(1, len(A)) - lags.reshape(len(lags), 1))- 1) % nPoints)

    C = np.dot(np.squeeze(B1[inds]), A1)
    C = C.T/(nPoints)

    # set values to be in range 0 to 1
    C = (C + 1)/2

    # normalize by min, max so that different plaques size are taken into account
    C = (min(A.mean(), B.mean()))/(max(A.mean(), B.mean()))*C
    # np.roll(C, lags[0[)
    return C