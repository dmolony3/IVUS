# this is a python implementation of the function PolarToIm by Prakash Manandhar
import numpy as np

def PolarToIm(img, rMin, rMax, Mr, Nr):
    imgCart = np.zeros([Mr, Nr])
    # image center coordinates
    Om = (Mr)/2.0
    On = (Nr)/2.0
    # scale factors
    sx = (Mr - 1)/2.0
    sy = (Nr - 1)/2.0

    M, N = img.shape

    deltaR = float((rMax - rMin))/float((M-1))
    deltaT = (2*np.pi)/float(N)

    for xi in range(0, Mr):
        for yi in range(0, Nr):
            x = (xi - Om)/sx
            y = (yi - On)/sx
            r = np.sqrt(x**2 + y**2)

            if (r >= rMin) & (r <= rMax):
                t = np.arctan2(y, x)
                if t < 0:
                    t = t + 2*np.pi

                imgCart[xi, yi] = interpolate(img, r, t, rMin, rMax, M, N, deltaR, deltaT)

    return imgCart

def interpolate(img, r, t, rMin, rMax, M, N, deltaR, deltaT):
    ri = (r - rMin)/deltaR
    ti = t/deltaT
    rf = int(np.floor(ri))
    rc = int(np.ceil(ri))
    tf = int(np.floor(ti))
    tc = int(np.ceil(ti))

    if tc > (N-1):
        tc = tf

    if (rf == rc) & (tc == tf):
        v = img[rc, tc]
    elif rf == rc:
        v = img[rf, tf] + (ti - tf)*(img[rf, tc] - img[rf, tf])
    elif tf == tc:
        v = img[rf, tf] + (ri - rf)*img[rc, tf] - img[rf, tf]
    else:
        A = np.array([[rf, tf, rf*tf, 1],
             [rf, tc, rf*tc, 1],
             [rc, tf, rc*tf, 1],
             [rc, tc, rc*tc, 1]])
        z = np.array([[img[rf, tf]], [img[rf, tc]], [img[rc, tf]], [img[rc, tc]]])
        a = np.linalg.solve(A, z)

        w = np.array([ri, ti, ri*ti, 1], ndmin=2)
        v = np.dot(w,a)[0][0]

    return v